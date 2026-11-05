# Guia para Iniciantes (Passo a Passo Descomplicado) 🚀 🎧

Bem-vindo ao **OpenVoice BR Engine**! Se você nunca instalou ou configurou um servidor de voz antes, este guia foi feito especialmente para você.

---

## 💡 O que este projeto faz?

O **OpenVoice BR Engine** recebe um texto e o transforma em um **arquivo de áudio falado (MP3, WAV, etc.)**.

- 💰 **100% Gratuito:** Sem cobranças da OpenAI, sem limite de tokens e sem cartão de crédito.
- 🇧🇷 **Vozes Brasileiras Naturais:** Vozes neurais masculinas e femininas (Thalita, Antonio, Francisca, etc.).
- 🛡️ **Proteção Anti-Bloqueio (v2.2.0):** Se a Microsoft tentar bloquear a conexão no seu servidor (erro 403 comum na Hetzner/VPS), o sistema chaveia automaticamente para o Google TTS sem quebrar suas automações!
- 🔌 **Compatível com Tudo:** Funciona direto com **n8n, Typebot, Chatwoot, Evolution API, Z-API** e qualquer app que use a OpenAI.

---

## ⏱️ Como Rodar em 2 Minutos

Escolha a forma mais conveniente para o seu ambiente:

### Opção 1: No Portainer (Mais Fácil para Servidores VPS)
1. Abra o painel do seu **Portainer**.
2. No menu esquerdo, vá em **Stacks** → **Add stack**.
3. Dê um nome (por exemplo: `multivozes`).
4. Selecione a aba **Web editor** e cole o conteúdo do arquivo [portainer-stack.yml](portainer-stack.yml).
5. Clique no botão azul **Deploy the stack**.
6. Pronto! O Portainer cuidará de tudo.

### Opção 2: Com Docker em 1 Linha de Comando
Se você tem Docker instalado na sua máquina ou VPS, abra o terminal e rode:

```bash
docker run -d \
  --name multivozes \
  --restart unless-stopped \
  -p 5050:5050 \
  -e TTS_ENGINE=auto \
  -e REQUIRE_API_KEY=false \
  ghcr.io/leaomoacir/multivozes_br_engine:latest
```

### Opção 3: No seu Computador com Python (Sem Docker)
Requisitos: Ter o **Python 3.10 a 3.13** e o **FFmpeg** instalados.

```bash
# 1. Clone o projeto
git clone https://github.com/leaomoacir/multivozes_br_engine.git
cd multivozes_br_engine

# 2. Crie e ative o ambiente virtual
python -m venv .venv

# No Windows:
.\.venv\Scripts\Activate.ps1
# No Linux / Mac:
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie o servidor
python main.py
```

---

## 🧪 Testando se está Funcionando

Com o servidor rodando, você pode testar em 30 segundos:

### 1. No Navegador:
- Acesse `http://localhost:5050/health`. Se responder `{"status":"ok", ...}`, o servidor está perfeito!
- Acesse `http://localhost:5050/docs` para ver a documentação interativa com tela para testar requisições.

### 2. Gerando seu Primeiro Arquivo de Áudio:

**No Windows (PowerShell):**
```powershell
$payload = @{
    model = "tts-1"
    input = "Olá! Parabéns, seu servidor de voz OpenVoice está funcionando com sucesso."
    voice = "alloy"
    response_format = "mp3"
} | ConvertTo-Json

Invoke-RestMethod -Uri 'http://localhost:5050/v1/audio/speech' `
    -Method Post `
    -ContentType 'application/json; charset=utf-8' `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($payload)) `
    -OutFile 'meu_primeiro_audio.mp3'
```

**No Linux / macOS (cURL):**
```bash
curl -X POST http://localhost:5050/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"tts-1","input":"Olá! Parabéns, seu servidor de voz está funcionando.","voice":"alloy"}' \
  --output meu_primeiro_audio.mp3
```

Abra o arquivo `meu_primeiro_audio.mp3` gerado na pasta e ouça a voz!

---

## 🤖 Como Conectar com Suas Ferramentas

### No n8n:
- **Se usa o Nó OpenAI:** No campo *Base URL*, coloque `http://multivozes:5050/v1`. Em *API Key*, escreva `local`. Modelo: `tts-1`. Voz: `alloy`.
- **Se usa o Nó HTTP Request:** Método `POST` para `http://multivozes:5050/v1/audio/speech` com resposta do tipo **File**.

### No Typebot:
- Crie um bloco de Webhook `POST` para `http://SEU_IP:5050/v1/audio/speech`, envie o JSON com seu texto e receba o áudio para reproduzir no bot.

### Na Evolution API (WhatsApp):
- Pegue o binário gerado pelo n8n, converta para Base64 e envie para `/message/sendWhatsAppAudio` para que a mensagem chegue como nota de voz gravada no WhatsApp.

👉 Veja exemplos detalhados de código e telas em **[INTEGRATIONS.md](INTEGRATIONS.md)**.

---

## 🎙️ Como Escolher Outra Voz

Basta trocar o parâmetro `"voice"` na requisição:

| Nome para Enviar | Voz / Sotaque | Estilo |
| --- | --- | --- |
| `"alloy"` ou `"thalita"` | `pt-BR-ThalitaMultilingualNeural` | Feminina, expressiva e natural (Padrão) |
| `"antonio"` | `pt-BR-AntonioNeural` | Masculina, séria e radiofônica |
| `"francisca"` | `pt-BR-FranciscaNeural` | Feminina, calorosa e comercial |
| `"fabio"` | `pt-BR-FabioNeural` | Masculina jovem e conversacional |

👉 Veja a lista com mais de 300 vozes internacionais no **[VOICES.md](VOICES.md)**.

---

## ❓ Perguntas Frequentes & Solução de Problemas

### 1. Meu servidor VPS na Hetzner dá erro 403 ou "WebSocket handshake failed"
- A Microsoft bloqueia ativamente os blocos de IPs de data centers para conexões WebSocket do Edge.
- **Solução no v2.2.0:** O OpenVoice BR Engine já detecta isso e faz **fallback automático para o Google TTS (gTTS)**.
- Se quiser pular a tentativa do Edge e usar 100% Google via HTTP normal desde o início, defina no seu `.env` ou Portainer:
  ```env
  TTS_ENGINE=gtts
  ```

### 2. O n8n não consegue acessar o endereço `http://localhost:5050`
- Quando o n8n roda dentro de um container Docker, `localhost` aponta para dentro do próprio container do n8n, e não para o computador host.
- **Solução:** Coloque os dois containers na mesma rede Docker (por exemplo, `network_public`) e use a URL interna:
  ```text
  http://multivozes:5050/v1/audio/speech
  ```

### 3. Preciso colocar senha na API?
- Para uso interno no mesmo servidor (com n8n na mesma rede Docker), você pode deixar `REQUIRE_API_KEY=false` (padrão).
- Se você for expor a porta para a internet pública, defina no `.env`:
  ```env
  REQUIRE_API_KEY=true
  API_KEY=sua_senha_secreta_aqui
  ```
  E nos seus bots, envie o cabeçalho `Authorization: Bearer sua_senha_secreta_aqui`.
