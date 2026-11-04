"""Módulo de síntese de voz (TTS) com suporte a múltiplos motores gratuitos (Edge-TTS e gTTS) e fallback automático."""
import asyncio
import json
import logging
import os
import re
import shutil
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from config import DEFAULT_CONFIGS, DEFAULT_OPENAI_VOICES

load_dotenv()
logger = logging.getLogger("multivozes.tts")

PROXY = os.getenv('PROXY') or None
TTS_ENGINE_PADRAO = os.getenv('TTS_ENGINE', DEFAULT_CONFIGS.get('TTS_ENGINE', 'auto')).strip().lower()
DEFAULT_GTTS_LANG = os.getenv('DEFAULT_GTTS_LANG', DEFAULT_CONFIGS.get('DEFAULT_GTTS_LANG', 'pt')).strip().lower()
DEFAULT_GTTS_TLD = os.getenv('DEFAULT_GTTS_TLD', DEFAULT_CONFIGS.get('DEFAULT_GTTS_TLD', 'com.br')).strip().lower()


def carregar_mapeamento_vozes():
    path = Path(__file__).with_name('voices.json')
    if not path.exists():
        return dict(DEFAULT_OPENAI_VOICES)
    with path.open(encoding='utf-8') as stream:
        mapping = json.load(stream)
    if not isinstance(mapping, dict) or not all(
        isinstance(alias, str) and alias and isinstance(voice, str) and voice
        for alias, voice in mapping.items()
    ):
        raise ValueError('voices.json deve mapear nomes para vozes em texto.')
    for alias, voice in mapping.items():
        if alias in DEFAULT_OPENAI_VOICES and not voice.endswith('MultilingualNeural'):
            raise ValueError(f'O alias OpenAI {alias!r} deve usar uma voz MultilingualNeural.')
    return mapping


MAPEAMENTO_VOZES = carregar_mapeamento_vozes()

DADOS_MODELOS = [
    {'id': 'tts-1', 'name': 'Text-to-speech v1 (Padrão OpenAI - Auto Fallback)'},
    {'id': 'tts-1-hd', 'name': 'Text-to-speech v1 HD (Alta Fidelidade)'},
    {'id': 'edge-tts', 'name': 'Microsoft Edge Neural TTS (100% Gratuito)'},
    {'id': 'gtts', 'name': 'Google Translate TTS (100% Gratuito - HTTP Estável)'},
]

CONVERSION_ARGS = {
    'opus': ['-c:a', 'libopus', '-f', 'ogg'],
    'aac': ['-c:a', 'aac', '-f', 'adts'],
    'flac': ['-c:a', 'flac', '-f', 'flac'],
    'wav': ['-c:a', 'pcm_s16le', '-f', 'wav'],
    'pcm': ['-c:a', 'pcm_s16le', '-ar', '24000', '-ac', '1', '-f', 's16le'],
}

TLD_MAP = {
    'br': 'com.br',
    'pt': 'pt',
    'us': 'com',
    'uk': 'co.uk',
    'gb': 'co.uk',
    'au': 'com.au',
    'ca': 'ca',
    'es': 'es',
    'mx': 'com.mx',
    'fr': 'fr',
    'de': 'de',
    'it': 'it',
    'jp': 'co.jp',
}


def resolver_parametros_gtts(voz: str) -> tuple[str, str]:
    """Determina o idioma (lang) e domínio regional (tld) para o gTTS a partir do nome ou alias da voz."""
    voz_alvo = MAPEAMENTO_VOZES.get(voz, voz)

    # Suporte a formatos como pt-BR-..., en-US-..., pt-BR, pt, etc.
    match = re.match(r'^([a-zA-Z]{2,3})(?:[-_]([a-zA-Z]{2,4}))?', voz_alvo)
    if match:
        lang = match.group(1).lower()
        region = (match.group(2) or '').lower()
        if lang == 'pt':
            tld = 'pt' if region == 'pt' else 'com.br'
        else:
            tld = TLD_MAP.get(region, 'com')
        return lang, tld

    return DEFAULT_GTTS_LANG, DEFAULT_GTTS_TLD


def velocidade_para_taxa(velocidade: float) -> str:
    if not 0.25 <= velocidade <= 2.0:
        raise ValueError('A velocidade deve estar entre 0.25 e 2.0.')
    return f'{round((velocidade - 1) * 100):+d}%'


def _temporary_path(suffix: str) -> str:
    descriptor, path = tempfile.mkstemp(suffix=suffix)
    os.close(descriptor)
    return path


async def _convert(source: str, destination: str, format_name: str, speed: float = 1.0):
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        raise RuntimeError('FFmpeg não está instalado para converter áudio.')

    args = ['-nostdin', '-hide_banner', '-loglevel', 'error', '-y', '-i', source, '-vn']

    # Se a velocidade diferir de 1.0x, aplica filtro de tempo
    if abs(speed - 1.0) >= 0.01:
        if speed < 0.5:
            args.extend(['-filter:a', f'atempo=0.5,atempo={speed / 0.5:.4f}'])
        else:
            args.extend(['-filter:a', f'atempo={speed:.4f}'])

    if format_name in CONVERSION_ARGS:
        args.extend(CONVERSION_ARGS[format_name])
    elif format_name == 'mp3':
        args.extend(['-c:a', 'libmp3lame', '-f', 'mp3'])
    else:
        raise ValueError(f'Formato de áudio "{format_name}" não suportado.')

    args.append(destination)

    process = await asyncio.create_subprocess_exec(
        ffmpeg, *args,
        stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
    )
    try:
        if await process.wait() != 0:
            raise RuntimeError('FFmpeg não conseguiu converter o áudio.')
    except BaseException:
        if process.returncode is None:
            process.kill()
            await process.wait()
        raise


async def _executar_sintese_edge(texto: str, voz: str, formato_resposta: str, velocidade: float) -> str:
    """Sintetiza o áudio via Microsoft Edge-TTS."""
    import edge_tts
    taxa = velocidade_para_taxa(velocidade)
    voz_edge = MAPEAMENTO_VOZES.get(voz, voz)
    source = _temporary_path('.mp3')
    destination = source
    try:
        communicator = edge_tts.Communicate(texto, voz_edge, rate=taxa, proxy=PROXY)
        await communicator.save(source)
        if not Path(source).exists() or not Path(source).stat().st_size:
            raise RuntimeError('O Edge-TTS retornou áudio vazio.')

        if formato_resposta != 'mp3':
            destination = _temporary_path(f'.{formato_resposta}')
            await _convert(source, destination, formato_resposta, speed=1.0)
            Path(source).unlink(missing_ok=True)
        return destination
    except BaseException:
        Path(source).unlink(missing_ok=True)
        Path(destination).unlink(missing_ok=True)
        raise


async def _executar_sintese_gtts(texto: str, voz: str, formato_resposta: str, velocidade: float) -> str:
    """Sintetiza o áudio via Google Translate TTS (gTTS via HTTP)."""
    from gtts import gTTS
    lang, tld = resolver_parametros_gtts(voz)
    source = _temporary_path('.mp3')
    destination = source
    try:
        def _gtts_call():
            tts = gTTS(text=texto, lang=lang, tld=tld, slow=False)
            tts.save(source)

        await asyncio.to_thread(_gtts_call)

        if not Path(source).exists() or not Path(source).stat().st_size:
            raise RuntimeError('O gTTS retornou áudio vazio.')

        # gTTS gera mp3 em velocidade 1.0x padrão. Se precisar de ajuste de velocidade ou outro formato:
        precisa_conversao = (formato_resposta != 'mp3') or (abs(velocidade - 1.0) >= 0.01)
        if precisa_conversao:
            destination = _temporary_path(f'.{formato_resposta}')
            await _convert(source, destination, formato_resposta, speed=velocidade)
            Path(source).unlink(missing_ok=True)
        return destination
    except BaseException:
        Path(source).unlink(missing_ok=True)
        Path(destination).unlink(missing_ok=True)
        raise


async def gerar_audio(
    texto: str,
    voz: str,
    formato_resposta: str,
    velocidade: float,
    motor: str | None = None
) -> tuple[str, str, bool]:
    """
    Gera o arquivo de áudio usando o motor especificado ou com fallback automático.

    Retorna:
        tuple[caminho_arquivo: str, motor_utilizado: str, foi_fallback: bool]
    """
    formato_resposta = formato_resposta.lower()
    if formato_resposta not in {'mp3', *CONVERSION_ARGS}:
        raise ValueError(f'Formato de áudio "{formato_resposta}" não suportado.')

    motor_escolhido = (motor or TTS_ENGINE_PADRAO).strip().lower()

    if motor_escolhido == 'gtts':
        dest = await _executar_sintese_gtts(texto, voz, formato_resposta, velocidade)
        return dest, 'gtts', False

    if motor_escolhido == 'edge':
        dest = await _executar_sintese_edge(texto, voz, formato_resposta, velocidade)
        return dest, 'edge-tts', False

    # Motor 'auto' (padrão): Tenta Edge-TTS neural primeiro; se falhar/bloquear, executa fallback no gTTS
    edge_error = None
    try:
        dest = await _executar_sintese_edge(texto, voz, formato_resposta, velocidade)
        return dest, 'edge-tts', False
    except Exception as exc:
        edge_error = exc
        logger.warning(
            "Falha na síntese primária Edge-TTS (%s: %s). Ativando fallback automático para gTTS...",
            type(exc).__name__, exc
        )

    try:
        dest = await _executar_sintese_gtts(texto, voz, formato_resposta, velocidade)
        logger.info("Áudio gerado com sucesso via fallback do gTTS.")
        return dest, 'gtts', True
    except Exception as gtts_exc:
        logger.error("Falha também no fallback gTTS (%s: %s).", type(gtts_exc).__name__, gtts_exc)
        raise RuntimeError(
            f"Falha na síntese de áudio. Edge-TTS: {edge_error} | gTTS: {gtts_exc}"
        ) from gtts_exc
