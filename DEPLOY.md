# Guia de Deploy (Auto-Hospedado, Portainer, VPS Hetzner e CI/CD)

O **OpenVoice BR Engine** é auto-hospedado, leve e 100% gratuito. Ele pode ser executado em uma VPS própria (Hetzner, OVH, DigitalOcean, etc.), em seu homelab com Docker ou publicado como contêiner no Portainer.

---

## 1. Deploy Direto no Portainer (Via Stack Oficial)

A maneira mais rápida e elegante de rodar em um servidor com **Portainer**:

1. Acesse seu painel do **Portainer**.
2. Vá em **Stacks** → **Add stack**.
3. Defina um nome (ex: `openvoice-br`).
4. Selecione a aba **Web editor** e cole o conteúdo de [portainer-stack.yml](portainer-stack.yml).
5. Se desejar, ajuste as variáveis de ambiente (como `TTS_ENGINE=auto` ou `TTS_ENGINE=gtts`).
6. Clique no botão **Deploy the stack**.

> 💡 O Portainer irá baixar automaticamente a imagem pré-construída do GitHub Packages (`ghcr.io/leaomoacir/multivozes_br_engine:latest`) e iniciará a API na porta `5050`.

---

## 2. Deploy via Docker Compose no Terminal

Se preferir rodar direto pelo terminal via SSH:

```bash
# 1. Clone o repositório
git clone https://github.com/leaomoacir/multivozes_br_engine.git /opt/openvoice_br_engine
cd /opt/openvoice_br_engine

# 2. Crie e configure o .env
cp .env.example .env

# 3. Inicie o serviço
docker compose up -d
```

### Dicas para VPS Hetzner / Data Centers:
- **`TTS_ENGINE=auto`**: Tenta o Edge-TTS neural. Se houver erro 403 (bloqueio de IP pela Microsoft), faz fallback automático e instantâneo para o Google TTS.
- **`TTS_ENGINE=gtts`**: Se o seu IP de VPS estiver totalmente bloqueado para WebSockets, configure `TTS_ENGINE=gtts` para usar exclusivamente rotas HTTP normais do Google.
- **`BIND_ADDRESS=0.0.0.0`**: Permite que o n8n ou o proxy acessem o contêiner.

---

## 3. Rodando em 1 Linha com Docker Run

Para testar ou rodar rapidamente sem Compose:

```bash
docker run -d \
  --name openvoice_br_engine \
  --restart unless-stopped \
  -p 5050:5050 \
  -e TTS_ENGINE=auto \
  -e REQUIRE_API_KEY=false \
  ghcr.io/leaomoacir/multivozes_br_engine:latest
```

---

## 4. Integração com n8n no Mesmo Servidor (Rede Docker)

Se o n8n e o OpenVoice estiverem no mesmo servidor Docker/Portainer:
1. Conecte ambos na mesma rede Docker bridge (ex: `openvoice_net` ou `n8n_network`).
2. No n8n, use a URL interna direta:
   ```text
   http://openvoice_br_engine:5050/v1/audio/speech
   ```
   *(Não precisa de domínio público nem expor portas na internet!)*

---

## 5. Publicação Automática de Imagens (GitHub Actions CI/CD)

O repositório inclui um pipeline completo em [.github/workflows/docker-publish.yml](.github/workflows/docker-publish.yml):

- **Gatilhos:** A cada `push` na branch `master`/`main` ou criação de tags (`v*`), o GitHub Actions:
  1. Executa a suíte de testes unitários (`pytest test_app.py`) com FFmpeg.
  2. Compila a imagem Docker multi-plataforma (`linux/amd64` e `linux/arm64`).
  3. Publica a imagem no **GitHub Container Registry (GHCR)** em:
     `ghcr.io/leaomoacir/multivozes_br_engine:latest`
- **Zero Configuração de Secrets:** Usa a permissão nativa `GITHUB_TOKEN` do GitHub, sem precisar cadastrar senhas adicionais.
- **Suporte Opcional a Docker Hub:** Se desejar publicar também no Docker Hub, basta cadastrar os secrets `DOCKERHUB_USERNAME` e `DOCKERHUB_TOKEN` nas configurações do repositório no GitHub.

---

## 6. Acesso Externo via Cloudflare Tunnel (Opcional)

Se rodar o servidor em casa ou não quiser abrir portas públicas:

1. Instale o `cloudflared` na máquina.
2. Crie um túnel no **Cloudflare Zero Trust** apontando para `http://localhost:5050`.
3. Defina `REQUIRE_API_KEY=true` e `API_KEY=sua-chave` no `.env`.
