"""Exemplo de integração em Python com o OpenVoice BR Engine."""
import requests

BASE_URL = "http://localhost:5050"

def sintetizar_fala(texto: str, voz: str = "alloy", motor: str = "auto", formato: str = "mp3", velocidade: float = 1.0, arquivo_saida: str = "saida.mp3"):
    url = f"{BASE_URL}/v1/audio/speech"
    payload = {
        "model": "tts-1",
        "input": texto,
        "voice": voz,
        "response_format": formato,
        "speed": velocidade,
        "engine": motor
    }

    print(f"Sintetizando: '{texto[:40]}...' (Voz: {voz}, Motor: {motor})")
    response = requests.post(url, json=payload, timeout=60)

    if response.status_code == 200:
        motor_usado = response.headers.get("x-tts-engine-used", "desconhecido")
        fallback = response.headers.get("x-tts-fallback", "false")
        with open(arquivo_saida, "wb") as f:
            f.write(response.content)
        print(f"-> Áudio salvo em: {arquivo_saida} ({len(response.content)} bytes)")
        print(f"-> Motor utilizado: {motor_usado} | Fallback: {fallback}\n")
    else:
        print(f"Erro {response.status_code}: {response.text}\n")


if __name__ == "__main__":
    # Teste 1: Voz Neural Thalita (Edge-TTS)
    sintetizar_fala(
        texto="Olá! Esta é a voz neural brasileira Thalita, processada localmente com total fidelidade.",
        voz="alloy",
        motor="auto",
        arquivo_saida="exemplo_thalita.mp3"
    )

    # Teste 2: Voz Masculina Antônio
    sintetizar_fala(
        texto="Olá, eu sou o Antônio, uma voz masculina neural brasileira.",
        voz="antonio",
        motor="edge",
        arquivo_saida="exemplo_antonio.mp3"
    )

    # Teste 3: Google TTS via HTTP
    sintetizar_fala(
        texto="Este áudio foi gerado pelo Google TTS, perfeito para servidores de data center como Hetzner e OVH.",
        voz="pt-br",
        motor="gtts",
        velocidade=1.1,
        arquivo_saida="exemplo_google.mp3"
    )

