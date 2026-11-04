# Guia da API

Compatibilidade com o endpoint de geração de fala da OpenAI (`/v1/audio/speech`). Não fornece chat, transcrição, clonagem de voz ou modelos proprietários da OpenAI. O backend é **100% gratuito**, executando localmente com suporte dual: **Microsoft Edge-TTS neural** e **Google Translate TTS (gTTS)** com mecanismo de fallback transparente.

## Rotas

| Método e rota | Autenticação no backend | Resultado |
| --- | --- | --- |
| `GET /health` | Pública | Estado do serviço, motores ativos e versão |
| `GET /v1/models` | Pública | Modelos disponíveis (`tts-1`, `tts-1-hd`, `edge-tts`, `gtts`) |
| `GET /v1/audio/voices` | Pública ou Bearer (conforme .env) | Catálogo de vozes em `data` |
| `POST /v1/audio/speech` | Pública ou Bearer (conforme .env) | Arquivo binário de áudio sintetizado |

`/voices` e `/v1/voices` são aliases do catálogo. `/docs` contém a documentação Swagger interativa.

Catálogo: `?locale=pt-BR` filtra a localidade; `?locale=pt` inclui variantes de português; `?multilingual=true` filtra vozes MultilingualNeural.

---

## JSON de geração (`POST /v1/audio/speech`)

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `input` | String | Texto obrigatório (limite padrão: 10.000 caracteres) |
| `model` | String | `tts-1`, `tts-1-hd`, `edge-tts` ou `gtts`. Se especificado `gtts`, força o motor Google TTS. |
| `engine` | String | *(Opcional)* `auto` (padrão com fallback), `edge` (apenas Edge-TTS) ou `gtts` (Google TTS direto via HTTP). |
| `voice` | String | Apelido de `voices.json` (ex: `alloy`, `thalita`, `antonio`, `francisca`), nome técnico do Edge ou código de idioma gTTS (`pt-BR`, `pt`, `en`, `es`). |
| `response_format` | String | `mp3` (padrão), `wav`, `opus`, `aac`, `flac`, `pcm`. |
| `speed` | Número | `0.25` a `2.0` (padrão 1.0). Ajustado com alta fidelidade via filtro `atempo` do FFmpeg. |

### Cabeçalhos de Resposta Retornados
- `X-TTS-Engine-Used`: `edge-tts` ou `gtts`.
- `X-TTS-Fallback`: `true` se ocorreu fallback automático após falha no Edge, ou `false`.

---

## Exemplos de Chamada

### Bash / cURL

```sh
curl --fail-with-body http://localhost:5050/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{"model":"tts-1","input":"Olá! Áudio gerado localmente e gratuito.","voice":"alloy","response_format":"mp3","speed":1.0}' \
  --output fala.mp3
```

### Windows PowerShell

```powershell
$payload = @{
    model = 'tts-1'
    input = 'Olá! Teste de síntese de voz gratuita.'
    voice = 'alloy'
    response_format = 'mp3'
} | ConvertTo-Json

Invoke-RestMethod -Uri 'http://localhost:5050/v1/audio/speech' `
    -Method Post `
    -ContentType 'application/json; charset=utf-8' `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($payload)) `
    -OutFile 'fala.mp3'
```

### Python (exemplo simples com `requests` ou `httpx`)

```python
import requests

url = "http://localhost:5050/v1/audio/speech"
payload = {
    "model": "tts-1",
    "input": "Olá! Teste de síntese com fallback para gTTS.",
    "voice": "alloy",
    "response_format": "mp3",
    "speed": 1.0,
    "engine": "auto"
}

response = requests.post(url, json=payload)
if response.status_code == 200:
    with open("fala.mp3", "wb") as f:
        f.write(response.content)
    print("Áudio salvo com sucesso! Motor:", response.headers.get("x-tts-engine-used"))
```
