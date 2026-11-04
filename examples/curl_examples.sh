#!/usr/bin/env bash
# ==============================================================================
# OpenVoice BR Engine - Exemplos cURL
# ==============================================================================

BASE_URL="http://localhost:5050"
API_KEY="sua-chave-se-configurada"

echo "1. Verificando a saúde do serviço..."
curl -s "${BASE_URL}/health" | jq .

echo -e "\n2. Listando modelos disponíveis..."
curl -s "${BASE_URL}/v1/models" | jq .

echo -e "\n3. Gerando áudio com motor neural Edge (Thalita BR)..."
curl -X POST "${BASE_URL}/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "Olá! Este é um teste com a voz neural brasileira Thalita.",
    "voice": "alloy",
    "response_format": "mp3",
    "speed": 1.0,
    "engine": "auto"
  }' \
  --output "fala_edge_thalita.mp3"

echo -e "\n4. Gerando áudio com motor HTTP Google TTS (Anti-bloqueio VPS)..."
curl -X POST "${BASE_URL}/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "Olá! Áudio gerado diretamente pelo Google TTS via HTTP.",
    "voice": "pt-br",
    "response_format": "mp3",
    "speed": 1.25,
    "engine": "gtts"
  }' \
  --output "fala_google_gtts.mp3"

echo -e "\n5. Gerando áudio em formato WAV..."
curl -X POST "${BASE_URL}/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "Áudio de alta fidelidade em formato WAV sem compressão MP3.",
    "voice": "antonio",
    "response_format": "wav",
    "speed": 1.0
  }' \
  --output "fala_antonio.wav"

echo -e "\nConcluído! Arquivos gerados no diretório atual."

