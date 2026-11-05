# Integração com n8n 🇧🇷 🔴

> 💡 **Dica:** Para guias de outras plataformas como **Typebot, Chatwoot, Evolution API (WhatsApp) e Z-API**, consulte o arquivo **[INTEGRATIONS.md](INTEGRATIONS.md)**.

O **OpenVoice BR Engine** é 100% gratuito e compatível com a API de áudio da OpenAI (`/v1/audio/speech`). Ele pode ser conectado ao n8n tanto pelo **Nó Oficial da OpenAI** quanto pelo **Nó HTTP Request**.

---

## 1. Conexão via Rede Docker (Recomendado para VPS / Portainer)

Se o seu n8n e o multivozes estiverem rodando no mesmo servidor Docker:
- `localhost` dentro do contêiner do n8n aponta para o próprio n8n, não para a máquina host.
- Ambos os contêineres devem estar conectados na mesma rede Docker (por exemplo, `multivozes_net`).
- **URL interna direta:** `http://multivozes_br_engine:5050/v1` ou `http://multivozes:5050/v1`.

### Como conectar os contêineres:
Se o seu n8n já está rodando em uma rede (ex: `n8n_network`), basta definir no seu `.env` do multivozes:
```dotenv
DOCKER_NETWORK=n8n_network
```
Ou no terminal do Docker:
```sh
docker network connect multivozes_net <nome_do_container_n8n>
```

---

## 2. Opção A: Nó OpenAI (Áudio / Fala)

1. Crie uma nova credencial do tipo **OpenAI**:
   - **API Key:** Sua chave definida em `API_KEY` (se `REQUIRE_API_KEY=false`, pode colocar qualquer texto, ex: `local`).
   - **Base URL:** `http://multivozes_br_engine:5050/v1` (rede interna) ou `http://SEU_IP:5050/v1` (ou seu domínio HTTPS).
   - Não preencha Organization ID.
2. No nó OpenAI:
   - **Resource:** `Audio`
   - **Operation:** `Generate Speech`
   - **Model:** `tts-1` (ou `gtts` para forçar Google TTS direto)
   - **Voice:** `alloy` (Thalita), `antonio`, `francisca` ou qualquer apelido de [VOICES.md](VOICES.md).
   - **Input Text:** O texto que deseja sintetizar.

---

## 3. Opção B: Nó HTTP Request (Controle Total & Fallback)

O nó HTTP Request é ideal para definir parâmetros avançados e inspecionar os cabeçalhos de resposta:

1. **Method:** `POST`
2. **URL:** `http://multivozes_br_engine:5050/v1/audio/speech` (ou via HTTPS se publicado)
3. **Authentication:** 
   - Se `REQUIRE_API_KEY=true`: Selecione Header Auth com `Authorization: Bearer SUA_CHAVE`.
   - Se `REQUIRE_API_KEY=false`: Nenhuma autenticação é necessária.
4. **Send Headers:** `Content-Type: application/json`
5. **Send Body:** Ative e selecione `JSON`.
6. **JSON do Corpo (Payload):**

```json
{
  "model": "tts-1",
  "input": "Olá! Seu áudio foi processado com sucesso pelo Multivozes BR Engine.",
  "voice": "alloy",
  "response_format": "mp3",
  "speed": 1.0,
  "engine": "auto"
}
```

### Parâmetros Suportados:
- `engine`:
  - `"auto"` (Padrão): Tenta sintetizar primeiro com voz neural do **Edge-TTS**. Se houver bloqueio de IP (erro 403) ou instabilidade na Microsoft, **aciona o fallback automático para o Google TTS (gTTS)** sem derrubar seu fluxo!
  - `"gtts"`: Vai direto para o Google TTS via HTTP normal. 100% imune a bloqueios de data center (Hetzner, OVH, etc.).
  - `"edge"`: Usa exclusivamente o Edge-TTS.
- `voice`: `alloy` (Thalita BR), `antonio`, `francisca`, ou nomes completos (`pt-BR-ThalitaMultilingualNeural`).
- `response_format`: `mp3` (padrão), `wav`, `aac`, `opus`, `flac`.
- `speed`: `0.25` a `2.0` (suportado com ajuste fino pelo FFmpeg em ambos os motores).

7. **Response Format:** Selecione **File** (saída binária) para que o n8n salve o arquivo de áudio para enviar pelo WhatsApp, Telegram, email, etc.
8. **Timeout:** Defina 120000 ms (2 minutos) no nó para dar tempo de sintetizar textos longos.

---

## 4. Cabeçalhos de Diagnóstico no n8n

O motor responde com cabeçalhos HTTP que você pode conferir na aba de execução do n8n:
- `X-TTS-Engine-Used`: Indica se o áudio foi produzido por `edge-tts` ou `gtts`.
- `X-TTS-Fallback`: Indica `true` se o Edge falhou e o Google TTS assumiu o pedido de forma transparente, ou `false` se rodou diretamente.
