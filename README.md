# OpenVoice BR Engine 🇧🇷 🎙️

<p align="center">
  <b>Serviço Local de Síntese de Voz (TTS) 100% Gratuito e Compatível com a API da OpenAI.</b><br/>
  <i>Motor Dual: Microsoft Edge-TTS Neural + Google Translate TTS com Fallback Automático Anti-Bloqueio.</i><br/>
  <b>Free & Local OpenAI-Compatible Text-to-Speech Engine with Neural & HTTP Dual Fallback.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue?logo=python" alt="Python Version"/>
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker" alt="Docker Ready"/>
  <img src="https://img.shields.io/badge/API-OpenAI%20Compatible-green" alt="OpenAI Compatible"/>
  <img src="https://img.shields.io/badge/n8n-Ready-EA4B71?logo=n8n" alt="n8n Ready"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License MIT"/>
</p>

<p align="center">
  <b><a href="#-português">🇧🇷 Português</a></b> · <b><a href="#-english">🇺🇸 English</a></b> · <b><a href="#-exemplos-de-uso--examples">💡 Exemplos</a></b> · <b><a href="VOICES.md">🎙️ Catálogo de Vozes</a></b>
</p>

---

# 🇧🇷 Português

O **OpenVoice BR Engine** transforma texto em áudio de alta qualidade (**MP3, WAV, Opus, AAC, FLAC**) no seu próprio computador ou servidor VPS. Ele expõe exatamente a mesma interface HTTP da OpenAI (`POST /v1/audio/speech`), permitindo que você o conecte diretamente ao **n8n**, Typebot, chatbots, assistentes virtuais ou qualquer software compatível com a OpenAI — **sem pagar nada, sem precisar de cartão de crédito e sem tokens da OpenAI/ChatGPT**.

### 🚀 Novidades da Versão 2.2.0 (Resolução do Bloqueio de IP / Erro 403)
- **Mecanismo Dual & Fallback Automático:** Combina a voz neural ultrarrealista do **Microsoft Edge-TTS** com a estabilidade contínua do **Google Translate TTS (gTTS)**.
- **Solução Definitiva para Data Centers (Hetzner, OVH, DigitalOcean, etc.):** Mesmo quando a Microsoft bloqueia conexões WebSocket com erro 403 / handshake, o motor faz **fallback transparente para o Google TTS via HTTP padrão**, entregando o áudio com status `200 OK`. **Seu fluxo no n8n nunca quebra!**
- **Modo 100% HTTP:** Configure `TTS_ENGINE=gtts` no `.env` para rodar exclusivamente via requisições HTTP normais em servidores de data center.
- **Ajuste Fino de Velocidade e Formatos com FFmpeg:** Suporta velocidades fracionadas de `0.25x` a `2.0x` (com filtro `atempo`) e conversão para MP3, WAV, Opus, AAC, FLAC e PCM.
- **Desacoplamento de Redes no Docker:** Comunicação simplificada entre contêineres vizinhos na rede bridge `openvoice_net`.

---

## ⚡ Início Rápido com Docker (Recomendado)

O modo mais simples e isolado de rodar em qualquer máquina (Windows, Linux, macOS ou VPS):

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/samucamg/multivozes_br_engine.git
   cd multivozes_br_engine
   ```

2. **Crie o arquivo de configuração `.env`:**
   ```bash
   # Windows (PowerShell)
   Copy-Item .env.example .env

   # Linux / macOS
   cp .env.example .env
   ```

3. **Suba o contêiner:**
   ```bash
   docker compose up -d --build
   ```

Pronto! O serviço estará respondendo em `http://localhost:5050` (ou no IP do seu servidor).

Para conferir os logs:
```bash
docker logs -f openvoice_br_engine
```

---

## 🐍 Início Rápido sem Docker (Instalação Direta em Python)

Requisitos: **Python 3.10 a 3.13** e **FFmpeg** instalado no sistema.

1. **Clone e entre na pasta:**
   ```bash
   git clone https://github.com/samucamg/multivozes_br_engine.git
   cd multivozes_br_engine
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   python -m venv .venv

   # Windows (PowerShell)
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   source .venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Copie o `.env` e inicie o servidor:**
   ```bash
   # Windows: Copy-Item .env.example .env | Linux: cp .env.example .env
   python main.py
   ```

---

## 🤖 Integração com n8n

O OpenVoice BR Engine é 100% compatível com o n8n. Você pode usá-lo de duas formas:

### 1. Nó Oficial da OpenAI (Geração de Áudio)
- **Credencial OpenAI:**
  - **API Key:** Sua chave do `.env` (se `REQUIRE_API_KEY=false`, informe qualquer texto, ex: `local`).
  - **Base URL:** `http://openvoice_br_engine:5050/v1` (se na mesma rede Docker) ou `http://SEU_IP:5050/v1`.
- **Configurações do Nó:**
  - **Resource:** `Audio` → **Operation:** `Generate Speech`
  - **Model:** `tts-1` (ou `gtts`)
  - **Voice:** `alloy` (Thalita BR), `antonio`, `francisca` ou qualquer apelido de [VOICES.md](VOICES.md).

### 2. Nó HTTP Request (Mais Robusto e com Fallback)
- **Method:** `POST`
- **URL:** `http://openvoice_br_engine:5050/v1/audio/speech`
- **Body Content Type:** `JSON`
- **JSON Body:**
  ```json
  {
    "model": "tts-1",
    "input": "Olá! Seu fluxo do n8n agora gera áudio gratuitamente.",
    "voice": "alloy",
    "response_format": "mp3",
    "speed": 1.0,
    "engine": "auto"
  }
  ```
- **Response Format:** Selecione **File** para salvar o binário de áudio e enviá-lo via WhatsApp (Evolution API, Z-API), Telegram, e-mail, etc.

> 📁 Um template pronto para importar diretamente no seu n8n está disponível em [examples/n8n_workflow_template.json](examples/n8n_workflow_template.json).

---

## ⚙️ Motores de Síntese (`engine`)

Você pode escolher o motor na variável `TTS_ENGINE` do `.env` ou enviar dinamicamente no JSON da requisição:

| Valor | Comportamento | Quando Usar |
| --- | --- | --- |
| `"auto"` *(Padrão)* | Tenta o **Edge-TTS neural**. Se falhar (erro 403, timeout ou handshake), aciona automaticamente o **Google TTS**. | Recomendado para a maioria dos casos. Garante máxima qualidade e nunca deixa seu fluxo na mão. |
| `"gtts"` | Vai direto para o **Google Translate TTS** via HTTP padrão. | Ideal para servidores VPS de data center (Hetzner, OVH, Linode) com IP bloqueado na Microsoft. |
| `"edge"` | Usa exclusivamente o **Edge-TTS**. | Quando você deseja apenas voz neural e não aceita áudio sintetizado pelo Google. |

---

## 🎙️ Vozes Disponíveis

O sistema suporta apelidos amigáveis, compatibilidade total com os 13 aliases da OpenAI e o catálogo neural completo:

- **Principais vozes brasileiras:**
  - `alloy` ou `thalita`: `pt-BR-ThalitaMultilingualNeural` (Feminina, expressiva, padrão do projeto)
  - `antonio`: `pt-BR-AntonioNeural` (Masculina, natural, ideal para notícias e narrações)
  - `francisca`: `pt-BR-FranciscaNeural` (Feminina, calorosa, ótima para atendimento)
- **Vozes multilíngues da OpenAI:** `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`, `ash`, `ballad`, `cedar`, `coral`, `marin`, `sage`, `verse`.
- **Consulte a tabela completa de mais de 300 vozes em [VOICES.md](VOICES.md).**

---

<br/>

---

# 🇺🇸 English

**OpenVoice BR Engine** is an open-source, **100% free**, self-hosted Text-to-Speech (TTS) server that is fully compatible with OpenAI's speech API (`POST /v1/audio/speech`). It allows you to generate lifelike speech in multiple formats (**MP3, WAV, Opus, AAC, FLAC**) without needing an OpenAI account, credit card, or API tokens.

### 🚀 Key Features
- **Dual-Engine Architecture with Automatic Fallback:** Combines lifelike neural voices from **Microsoft Edge-TTS** with the robust reliability of **Google Translate TTS (gTTS)**.
- **Datacenter Anti-Block (Solves Error 403 / Handshake Issues):** If hosted on cloud VPS providers (such as Hetzner, OVH, or AWS) where Microsoft blocks datacenter WebSocket IPs, the engine **automatically falls back to Google TTS via standard HTTP**, guaranteeing a `200 OK` response.
- **Pure HTTP Mode:** Set `TTS_ENGINE=gtts` to bypass WebSockets entirely.
- **FFmpeg Speed & Pitch Adjustments:** Accurate speed adjustments (`0.25x` to `2.0x`) using the FFmpeg `atempo` filter.
- **Ready for n8n & Docker:** Pre-configured Docker Compose with internal network bridging for seamless automation workflows.

---

## ⚡ Quick Start with Docker

1. **Clone the repository:**
   ```bash
   git clone https://github.com/samucamg/multivozes_br_engine.git
   cd multivozes_br_engine
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   ```

3. **Start with Docker Compose:**
   ```bash
   docker compose up -d --build
   ```
   The service will be listening on `http://localhost:5050`.

---

## 🛠️ API Reference (`POST /v1/audio/speech`)

### Request Payload:
```json
{
  "model": "tts-1",
  "input": "Hello! This is a test using OpenVoice BR Engine.",
  "voice": "alloy",
  "response_format": "mp3",
  "speed": 1.0,
  "engine": "auto"
}
```

### Parameters:
- `input` *(string, required)*: Text to synthesize (up to 10,000 characters).
- `voice` *(string, optional)*: Voice alias (`alloy`, `thalita`, `antonio`, `francisca`) or Edge/Google locale tag.
- `response_format` *(string, optional)*: `mp3` (default), `wav`, `opus`, `aac`, `flac`, `pcm`.
- `speed` *(float, optional)*: Speech rate from `0.25` to `2.0` (default `1.0`).
- `engine` *(string, optional)*: `auto` (default with fallback), `gtts` (pure HTTP), or `edge` (neural only).

### Response Headers:
- `X-TTS-Engine-Used`: Identifies whether `edge-tts` or `gtts` synthesized the audio.
- `X-TTS-Fallback`: `true` if fallback was triggered, `false` otherwise.

---

## 💡 Exemplos de Uso / Examples

Explore practical integration examples in the [examples/](examples/) directory:
- [examples/curl_examples.sh](examples/curl_examples.sh) — Bash/cURL scripts for testing.
- [examples/powershell_examples.ps1](examples/powershell_examples.ps1) — PowerShell scripts for Windows/Linux.
- [examples/python_example.py](examples/python_example.py) — Python script using `requests`.
- [examples/n8n_workflow_template.json](examples/n8n_workflow_template.json) — Ready-to-import n8n workflow.
- [examples/audio_samples/](examples/audio_samples/) — Real audio files generated by the engines.

---

## 👥 Créditos e Agradecimentos / Credits & Acknowledgements

Este projeto é disponibilizado para a comunidade como uma solução aberta e gratuita.

Agradecimentos especiais aos desenvolvedores e projetos que tornaram isso possível:
- **Samuel de Sousa Santos (samucatutoriais)** — Criador do projeto MultiVozes BR original.
- **[travisvn/openai-edge-tts](https://github.com/travisvn/openai-edge-tts)** — Projeto base de inspiração para a camada compatível com OpenAI.
- **[rany2/edge-tts](https://github.com/rany2/edge-tts)** — Biblioteca Python para comunicação com o serviço Edge TTS.
- **[Belledonne Communications / gTTS](https://github.com/BelledonneCommunications/gTTS)** — Biblioteca de interface para o Google Translate TTS.
- **Comunidade n8n e automação open-source**.

---

## 📄 Licença / License

Distribuído sob a licença [MIT](LICENSE). Consulte o arquivo `LICENSE` para mais informações.
