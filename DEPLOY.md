# Guia de Deploy (Auto-Hospedado, VPS Hetzner e Cloudflare Tunnel)

O **OpenVoice BR Engine** é auto-hospedado, leve e não requer serviços em nuvem pagos. Ele pode ser executado em uma VPS própria (Hetzner, OVH, DigitalOcean, etc.), em casa via Cloudflare Tunnel ou em sua máquina de desenvolvimento.

---

## 1. Deploy em VPS (Ubuntu / Debian com Docker & Portainer)

Este é o cenário padrão para uso conjunto com o **n8n**.

### Passo a Passo no Servidor:
1. Conecte-se via SSH ao seu servidor VPS.
2. Clone o repositório:
   ```bash
   git clone https://github.com/samucamg/multivozes_br_engine.git /opt/openvoice_br_engine
   cd /opt/openvoice_br_engine
   ```
3. Copie o arquivo de variáveis de ambiente:
   ```bash
   cp .env.example .env
   ```
4. Edite o `.env`:
   ```bash
   nano .env
   ```
   **Dicas cruciais para VPS Hetzner / Data Centers:**
   - **`TTS_ENGINE=auto`**: Tenta o Edge-TTS e faz fallback automático para o Google TTS em caso de erro 403.
   - **`TTS_ENGINE=gtts`**: Se a Hetzner estiver com o IP 100% bloqueado para conexões WebSocket na Microsoft, configure `TTS_ENGINE=gtts` para usar direto as rotas HTTP normais do Google.
   - **`BIND_ADDRESS=0.0.0.0`**: Permite que o n8n ou o proxy acessem o contêiner.
   - **`DOCKER_NETWORK=openvoice_net`** (ou a rede onde o seu n8n já está rodando, ex: `n8n_network`).

5. Inicie o serviço:
   ```bash
   docker compose up -d --build
   ```

### Integração com n8n no Portainer:
Se o seu n8n e o OpenVoice estiverem na mesma máquina através do Portainer:
- Conecte o contêiner do n8n à rede `openvoice_net` (ou adicione ambos à mesma rede no Docker).
- No n8n, use a URL direta:
  ```text
  http://openvoice_br_engine:5050/v1/audio/speech
  ```
  *(Não precisa de domínio público nem expor portas na internet!)*

---

## 2. Acesso Externo Seguro via Cloudflare Tunnel

Se você roda o servidor em casa ou não quer abrir portas no firewall da VPS:

1. Instale o conector `cloudflared` na sua máquina/servidor.
2. Crie um túnel no painel do **Cloudflare Zero Trust** direcionando para:
   ```text
   HTTP -> localhost:5050
   ```
3. No `.env`, proteja com chave de API:
   ```dotenv
   API_KEY=sua-chave-ultra-segura-aqui
   REQUIRE_API_KEY=True
   ```
4. Configure suas chamadas no n8n ou clientes externos usando o cabeçalho:
   ```text
   Authorization: Bearer sua-chave-ultra-segura-aqui
   ```

---

## 3. Proxy Cloudflare Worker (Opcional)

Na pasta `workers/` há um template de Cloudflare Worker para criar um proxy intermediário caso queira ocultar a URL real do servidor ou aplicar regras customizadas de cache e timeout. Consulte `workers/README.md` se desejar utilizá-lo.
