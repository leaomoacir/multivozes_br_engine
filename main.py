"""OpenAI-compatible HTTP adapter for OpenVoice BR Engine (Edge-TTS & gTTS with Fallback)."""
import asyncio
import hmac
import json
import logging
import math
import os
import re
from pathlib import Path
import fastapi
import uvicorn
from fastapi import Depends, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer
from config import DEFAULT_CONFIGS
from handle_text import preparar_texto_para_tts
from tts_handler import DADOS_MODELOS, MAPEAMENTO_VOZES, gerar_audio
from utils import CHAVE_API, EXIGIR_CHAVE_API, LOG_ERROS_DETALHADO, TIPOS_MIME_AUDIO, obter_env_bool

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('openvoice')

app = fastapi.FastAPI(
    title='OpenVoice BR Engine',
    version='2.2.0',
    description='Serviço de Text-to-Speech gratuito compatível com OpenAI, integrando Edge-TTS neural e gTTS com fallback automático.'
)

PORTA = int(os.getenv('PORT', DEFAULT_CONFIGS['PORT']))
HOST = os.getenv('HOST', DEFAULT_CONFIGS.get('HOST', '0.0.0.0'))
VOZ_PADRAO = os.getenv('DEFAULT_VOICE', DEFAULT_CONFIGS['DEFAULT_VOICE'])
FORMATO_RESPOSTA_PADRAO = os.getenv('DEFAULT_RESPONSE_FORMAT', 'mp3')
VELOCIDADE_PADRAO = float(os.getenv('DEFAULT_SPEED', '1.0'))
TTS_ENGINE_PADRAO = os.getenv('TTS_ENGINE', DEFAULT_CONFIGS.get('TTS_ENGINE', 'auto')).strip().lower()

REMOVER_FILTRO = obter_env_bool('REMOVE_FILTER', False)
MAX_INPUT_CHARS = int(os.getenv('MAX_INPUT_CHARS', '10000'))
MAX_REQUEST_BYTES = int(os.getenv('MAX_REQUEST_BYTES', '131072'))
TTS_TIMEOUT_SECONDS = float(os.getenv('TTS_TIMEOUT_SECONDS', '90'))
MAX_CONCURRENT_TTS = int(os.getenv('MAX_CONCURRENT_TTS', '4'))

if not math.isfinite(TTS_TIMEOUT_SECONDS) or min(MAX_INPUT_CHARS, MAX_REQUEST_BYTES, TTS_TIMEOUT_SECONDS, MAX_CONCURRENT_TTS) <= 0:
    raise ValueError('Os limites e timeout de TTS devem ser positivos.')

_synthesis_slots = asyncio.Semaphore(MAX_CONCURRENT_TTS)
_bearer_auth = HTTPBearer(
    auto_error=False, scheme_name='BearerAuth',
    description='Informe API_KEY. Obrigatória apenas quando REQUIRE_API_KEY=true no servidor.',
)


class TemporaryAudioResponse(FileResponse):
    """Remove o arquivo de áudio temporário após o envio ou em caso de cancelamento da requisição."""
    async def __call__(self, scope, receive, send):
        try:
            await super().__call__(scope, receive, send)
        finally:
            try:
                Path(self.path).unlink(missing_ok=True)
            except OSError as error:
                logger.warning('Falha na limpeza do arquivo de áudio temporário (%s)', type(error).__name__)


async def verificar_chave_api(request: Request, _credentials=Depends(_bearer_auth)):
    if not EXIGIR_CHAVE_API:
        return
    if not CHAVE_API:
        raise HTTPException(503, 'Defina API_KEY no servidor antes de usar a API.')
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer ') or not hmac.compare_digest(auth[7:].encode('utf-8'), CHAVE_API.encode('utf-8')):
        raise HTTPException(401, 'Chave de API ausente ou inválida.')


async def _read_payload(request: Request):
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > MAX_REQUEST_BYTES:
            raise HTTPException(413, 'Requisição excede o tamanho máximo permitido.')
    try:
        data = json.loads(body)
    except (ValueError, UnicodeDecodeError, RecursionError):
        raise HTTPException(400, 'JSON inválido.')
    if not isinstance(data, dict):
        raise HTTPException(400, 'O corpo JSON deve ser um objeto.')
    return data


@app.post(
    '/v1/audio/speech', dependencies=[Depends(verificar_chave_api)],
    response_class=TemporaryAudioResponse,
    responses={200: {'description': 'Arquivo de áudio sintetizado.', 'content': {
        mime: {'schema': {'type': 'string', 'format': 'binary'}}
        for mime in TIPOS_MIME_AUDIO.values()
    }}},
    openapi_extra={'requestBody': {'required': True, 'content': {'application/json': {
        'schema': {
            'type': 'object', 'required': ['input'],
            'properties': {
                'input': {'type': 'string', 'minLength': 1, 'maxLength': MAX_INPUT_CHARS},
                'model': {'type': 'string', 'default': 'tts-1',
                          'description': 'Modelo OpenAI compatível: tts-1, tts-1-hd, edge-tts ou gtts.'},
                'voice': {'type': 'string', 'default': VOZ_PADRAO,
                          'description': 'Apelido (ex: alloy, thalita, antonio) ou nome do catálogo Edge/gTTS.'},
                'response_format': {'type': 'string', 'enum': list(TIPOS_MIME_AUDIO), 'default': FORMATO_RESPOSTA_PADRAO},
                'speed': {'type': 'number', 'minimum': 0.25, 'maximum': 2.0, 'default': VELOCIDADE_PADRAO},
                'engine': {'type': 'string', 'enum': ['auto', 'edge', 'gtts'], 'default': 'auto',
                           'description': 'Motor TTS: auto (fallback para gTTS), edge ou gtts.'},
            },
        },
        'example': {'input': 'Olá! Esta é uma demonstração de síntese de voz.',
                    'model': 'tts-1', 'voice': VOZ_PADRAO,
                    'response_format': 'mp3', 'speed': 1.0, 'engine': 'auto'},
    }}}},
)
async def text_to_speech(request: Request):
    data = await _read_payload(request)
    text = data.get('input')
    if not isinstance(text, str) or not text.strip():
        raise HTTPException(400, "O campo 'input' deve conter texto válido.")
    if len(text) > MAX_INPUT_CHARS:
        raise HTTPException(413, f'O texto excede o limite de {MAX_INPUT_CHARS} caracteres.')

    if not REMOVER_FILTRO:
        text = preparar_texto_para_tts(text)
    if not text.strip():
        raise HTTPException(400, 'O texto ficou vazio após a remoção de formatação e emojis.')

    voice = data.get('voice', VOZ_PADRAO)
    if not isinstance(voice, str) or len(voice) > 150 or not re.fullmatch(r'[A-Za-z0-9_.-]+', voice):
        raise HTTPException(400, 'Voz inválida. Use um apelido de voices.json ou nome de voz/idioma.')

    format_name = data.get('response_format', FORMATO_RESPOSTA_PADRAO)
    if not isinstance(format_name, str) or format_name.lower() not in TIPOS_MIME_AUDIO:
        raise HTTPException(400, 'Formato de áudio não suportado.')
    format_name = format_name.lower()

    speed = data.get('speed', VELOCIDADE_PADRAO)
    try:
        if isinstance(speed, bool):
            raise ValueError
        speed = float(speed)
        if not math.isfinite(speed) or not 0.25 <= speed <= 2.0:
            raise ValueError
    except (ValueError, TypeError, OverflowError):
        raise HTTPException(400, 'A velocidade deve estar entre 0.25 e 2.0.')

    # Seleção do motor TTS
    motor_solicitado = data.get('engine')
    modelo_solicitado = (data.get('model') or '').lower()
    if motor_solicitado in ('auto', 'edge', 'gtts'):
        motor = motor_solicitado
    elif modelo_solicitado == 'gtts':
        motor = 'gtts'
    elif modelo_solicitado in ('edge', 'edge-tts'):
        motor = 'edge'
    else:
        motor = TTS_ENGINE_PADRAO

    if _synthesis_slots.locked():
        raise HTTPException(503, 'Servidor ocupado. Tente novamente em instantes.', headers={'Retry-After': '5'})

    async with _synthesis_slots:
        try:
            path, motor_usado, foi_fallback = await asyncio.wait_for(
                gerar_audio(text, voice, format_name, speed, motor=motor),
                TTS_TIMEOUT_SECONDS
            )
        except asyncio.TimeoutError:
            raise HTTPException(504, 'O serviço de síntese excedeu o tempo limite configurado.')
        except Exception as error:
            if LOG_ERROS_DETALHADO:
                logger.exception('Falha na síntese de áudio: %s', error)
            else:
                logger.warning('Falha na síntese de áudio (%s: %s)', type(error).__name__, error)
            raise HTTPException(
                502,
                f'Falha na síntese de áudio ou na conversão via FFmpeg: {error}'
            )

    headers = {
        'X-TTS-Engine-Used': motor_usado,
        'X-TTS-Fallback': 'true' if foi_fallback else 'false',
    }
    return TemporaryAudioResponse(
        path,
        media_type=TIPOS_MIME_AUDIO[format_name],
        filename=f'speech.{format_name}',
        headers=headers
    )


@app.get('/health')
def health():
    """Retorna o estado operacional e configurações do serviço."""
    return {
        'status': 'ok',
        'engine': TTS_ENGINE_PADRAO,
        'available_engines': ['edge-tts', 'gtts'],
        'default_voice': VOZ_PADRAO,
        'version': '2.2.0'
    }


@app.get('/v1/models')
def listar_modelos():
    return {'data': [{'id': m['id'], 'object': 'model', 'name': m['name']} for m in DADOS_MODELOS]}


@app.get('/voices', dependencies=[Depends(verificar_chave_api)], include_in_schema=False)
@app.get('/v1/voices', dependencies=[Depends(verificar_chave_api)], include_in_schema=False)
@app.get('/v1/audio/voices', dependencies=[Depends(verificar_chave_api)])
async def listar_vozes(locale: str | None = None, multilingual: bool = False):
    from voices_catalog import get_voices
    try:
        return {'data': await get_voices(locale=locale, multilingual=multilingual)}
    except asyncio.TimeoutError:
        raise HTTPException(504, 'Consulta de vozes excedeu o tempo limite.')
    except Exception as error:
        logger.warning('Falha na consulta de vozes (%s: %s)', type(error).__name__, error)
        raise HTTPException(502, 'Não foi possível consultar o catálogo de vozes.')


if __name__ == '__main__':
    print('========================================================')
    print('  OpenVoice BR Engine v2.2.0 - 100% Gratuito & Local    ')
    print('  Motores: Microsoft Edge Neural + Google Translate TTS  ')
    print(f'  Modo: {TTS_ENGINE_PADRAO.upper()} | Porta: {PORTA} | Host: {HOST}')
    print('  Créditos: samucatutoriais, travisvn & rany2           ')
    print('========================================================')
    uvicorn.run(app, host=HOST, port=PORTA)
