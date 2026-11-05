# 🎧 Amostras de Áudio / Audio Samples

Esta pasta contém exemplos reais de áudio gerados pelo **OpenVoice BR Engine** (v2.2.0) utilizando os dois motores integrados.

---

## 🇧🇷 Amostras Disponíveis para Ouvir

### 1. Microsoft Edge-TTS Neural (Voz: `pt-BR-ThalitaMultilingualNeural`)
- **Arquivo:** [exemplo_edge_neural_ptbr.mp3](exemplo_edge_neural_ptbr.mp3)
- **Tamanho:** ~63 KB
- **Formato:** MP3 (24 kHz, estéreo, voz neural com entonação humana ultra-realista)
- **Texto sintetizado:**
  > *"Olá! Bem-vindo ao OpenVoice BR Engine. Este áudio foi gerado com a voz neural da Microsoft, totalmente gratuito e compatível com a API da OpenAI."*

### 2. Google Translate TTS (Motor HTTP / Fallback Anti-Bloqueio)
- **Arquivo:** [exemplo_google_gtts_ptbr.mp3](exemplo_google_gtts_ptbr.mp3)
- **Tamanho:** ~78 KB
- **Formato:** MP3 (24 kHz, voz gerada via chamadas HTTP estáveis ao Google TTS)
- **Texto sintetizado:**
  > *"Olá! Este é um teste do motor Google TTS com fallback automático. Ele garante que seu fluxo no n8n continue funcionando mesmo se a Microsoft bloquear o IP do seu servidor."*

---

## 🛠️ Como Gerar Seus Próprios Áudios

### Gerar via Edge-TTS (Neural)
```bash
curl -X POST http://localhost:5050/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"tts-1","input":"Testando síntese neural com Thalita.","voice":"alloy","engine":"edge"}' \
  --output meu_audio_edge.mp3
```

### Gerar via Google TTS (gTTS HTTP)
```bash
curl -X POST http://localhost:5050/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"tts-1","input":"Testando síntese com Google Translate TTS.","voice":"alloy","engine":"gtts"}' \
  --output meu_audio_google.mp3
```

### Gerar no Modo Inteligente com Fallback (`engine: auto`)
```bash
curl -X POST http://localhost:5050/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"tts-1","input":"Áudio inteligente com proteção anti-bloqueio.","voice":"alloy","engine":"auto"}' \
  --output meu_audio_inteligente.mp3
```
