# Guia de Integrações / Integrations Guide 🤖 🔌

O **OpenVoice BR Engine** é 100% compatível com a especificação de áudio da OpenAI (`POST /v1/audio/speech`). Isso significa que **qualquer software, plataforma de automação ou bot que suporte a API da OpenAI ou chamadas HTTP/Webhooks** pode utilizá-lo sem custos.

---

## 📑 Índice de Plataformas

1. [🔴 n8n (Nó OpenAI & Nó HTTP Request)](#1-n8n-automation)
2. [🤖 Typebot (Chatbots Web & WhatsApp)](#2-typebot)
3. [📱 Evolution API (WhatsApp Gateway / Mensagem de Voz PTT)](#3-evolution-api-whatsapp)
4. [💬 Chatwoot (Atendimento Omnichannel com Áudio)](#4-chatwoot)
5. [⚡ Z-API & WPPConnect](#5-z-api--wppconnect)
6. [🧠 Flowise & Dify (Agentes de IA e RAG)](#6-flowise--dify)

---

## 1. n8n Automation

Você tem duas formas de usar o engine no n8n:

### Opção A: Nó Oficial da OpenAI (Configuração Mais Rápida)
1. No n8n, adicione uma credencial do tipo **OpenAI**:
   - **API Key:** Sua chave do `.env` (se `REQUIRE_API_KEY=false`, digite qualquer texto, ex: `local`).
   - **Base URL:** `http://multivozes:5050/v1` (se na mesma rede Docker) ou `http://SEU_IP:5050/v1`.
2. Adicione o nó **OpenAI**:
   - **Resource:** `Audio`
   - **Operation:** `Generate Speech`
   - **Model:** `tts-1`
   - **Voice:** `alloy` (Thalita BR), `antonio`, `francisca` ou qualquer apelido do catálogo.
   - **Input Text:** Texto que deseja sintetizar.

### Opção B: Nó HTTP Request (Mais Robusto com Fallback e Controle Fino)
1. **Method:** `POST`
2. **URL:** `http://multivozes:5050/v1/audio/speech`
3. **Authentication:** 
   - Se `REQUIRE_API_KEY=true`: Header Auth com `Authorization: Bearer SUA_CHAVE`.
   - Se `REQUIRE_API_KEY=false`: Nenhuma.
4. **Body Parameters:**
   ```json
   {
     "model": "tts-1",
     "input": "Olá! Seu fluxo no n8n agora sintetiza áudio gratuitamente.",
     "voice": "alloy",
     "response_format": "mp3",
     "speed": 1.0,
     "engine": "auto"
   }
   ```
5. **Response Format:** Selecione **File** para receber o binário de áudio e passá-lo para outros nós (WhatsApp, Telegram, etc.).

> 💡 Template pronto para importar no n8n: [examples/n8n_workflow_template.json](examples/n8n_workflow_template.json).

---

## 2. Typebot

No **Typebot**, você pode gerar áudios para responder aos usuários com mensagens de voz.

### Passo a Passo no Typebot:
1. No fluxo do seu bot, adicione um bloco de **Webhook**:
   - **Method:** `POST`
   - **URL:** `http://SEU_DOMINIO_OU_IP:5050/v1/audio/speech`
   - **Headers:**
     - `Content-Type: application/json`
     - *(Opcional)* `Authorization: Bearer SUA_CHAVE`
   - **Body (JSON):**
     ```json
     {
       "model": "tts-1",
       "input": "{{texto_da_resposta}}",
       "voice": "alloy",
       "response_format": "mp3",
       "engine": "auto"
     }
     ```
2. Salve a resposta do Webhook na variável `audio_gerado`.
3. Adicione um bloco de exibição do tipo **Áudio** e aponte para a URL retornada ou use via webhook do WhatsApp para envio de áudio nativo.

---

## 3. Evolution API (WhatsApp)

A **Evolution API** é o gateway de WhatsApp open-source mais utilizado do Brasil. Você pode converter qualquer texto gerado pela sua IA em um **áudio gravado na hora (Push-to-Talk / microfone azul)**.

### Fluxo Recomendado (n8n + OpenVoice + Evolution API):
1. **Passo 1 (OpenVoice BR Engine):**
   - O n8n faz a requisição para `http://multivozes:5050/v1/audio/speech` com `response_format: "mp3"`.
2. **Passo 2 (Conversão Base64 no n8n):**
   - No n8n, use o nó Code para converter o arquivo binário em Base64:
     ```javascript
     const binaryData = await this.helpers.getBinaryDataBuffer(0, 'data');
     return [{
       json: {
         base64Audio: binaryData.toString('base64')
       }
     }];
     ```
3. **Passo 3 (Envio via Evolution API):**
   - Faça um `POST` para o endpoint da Evolution API:
     `http://evolution-api:8080/message/sendWhatsAppAudio/SUA_INSTANCIA`
   - **Headers:** `apikey: SUA_EVOLUTION_API_KEY`, `Content-Type: application/json`
   - **Body:**
     ```json
     {
       "number": "5511999999999",
       "audio": "data:audio/mp3;base64,{{ $json.base64Audio }}",
       "delay": 1200,
       "encoding": true
     }
     ```
   - O WhatsApp receberá a mensagem como **nota de voz gravada** pelo operador!

---

## 4. Chatwoot

Para enviar mensagens de voz automáticas nos atendimentos do **Chatwoot**:

1. No seu webhook / bot do n8n que atende as mensagens do Chatwoot:
2. Quando a IA gerar a resposta em texto, envie para o **OpenVoice BR Engine**.
3. O binário `.mp3` retornado é anexado via `multipart/form-data` no endpoint de mensagens do Chatwoot:
   - **POST:** `https://seu-chatwoot.com/api/v1/accounts/{account_id}/conversations/{conversation_id}/messages`
   - **Headers:** `api_access_token: SEU_TOKEN_CHATWOOT`
   - **Form Data:**
     - `content`: *(Opcional, transcrição ou vazio)*
     - `message_type`: `outgoing`
     - `attachments[]`: Arquivo binário de áudio gerado pelo OpenVoice

---

## 5. Z-API & WPPConnect

Envio direto para endpoints de áudio das APIs do WhatsApp:

### Z-API (`/send-audio`):
```bash
curl -X POST "https://api.z-api.io/instances/SUA_INSTANCIA/token/SEU_TOKEN/send-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "5511999999999",
    "audio": "https://seu-dominio.com/audio-gerado.mp3"
  }'
```

---

## 6. Flowise & Dify (Agentes de IA e RAG)

Plataformas de orquestração de LLMs e agentes como **Flowise** e **Dify** possuem nós nativos de conversão Texto-para-Fala (Text-to-Speech) que usam a OpenAI.

1. No nó **OpenAI TTS / Speech Generator**:
2. Substitua a **Base URL** da OpenAI por:
   ```text
   http://multivozes:5050/v1
   ```
3. No campo **API Key**, informe a chave cadastrada no seu `.env` (ou `local` se desabilitada).
4. Modelo: `tts-1`. Voz: `alloy`.
5. O agente agora responde por voz sem consumir créditos da OpenAI!
