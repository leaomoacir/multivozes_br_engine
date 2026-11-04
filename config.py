DEFAULT_CONFIGS = {
    # --- Configurações do Servidor ---
    "PORT": 5050,
    "HOST": "0.0.0.0",
    "API_KEY": None,

    # --- Configurações de TTS ---
    # TTS_ENGINE: 'auto' (tenta Edge-TTS neural; se falhar/403, faz fallback automático para gTTS)
    #             'gtts' (usa 100% Google Translate TTS via HTTP padrão - ideal para VPS/Datacenters)
    #             'edge' (usa exclusivamente Edge-TTS via WebSocket)
    "TTS_ENGINE": "auto",
    "DEFAULT_VOICE": "pt-BR-ThalitaMultilingualNeural",
    "DEFAULT_RESPONSE_FORMAT": "mp3",
    "DEFAULT_SPEED": 1.0,
    "DEFAULT_LANGUAGE": "pt-BR",

    # --- Configurações padrão do gTTS ---
    "DEFAULT_GTTS_LANG": "pt",
    "DEFAULT_GTTS_TLD": "com.br",

    # --- Funcionalidades (Flags) ---
    "REQUIRE_API_KEY": False,
    "REMOVE_FILTER": False,
    "DETAILED_ERROR_LOGGING": True,
}

# Aliases padrão compatíveis com a OpenAI. Os aliases usam vozes multilíngues;
# nomes técnicos e apelidos personalizados continuam disponíveis.
DEFAULT_OPENAI_VOICES = {
    "alloy": "pt-BR-ThalitaMultilingualNeural",
    "ash": "en-US-AndrewMultilingualNeural",
    "ballad": "en-US-BrianMultilingualNeural",
    "cedar": "en-AU-WilliamMultilingualNeural",
    "coral": "en-US-AvaMultilingualNeural",
    "echo": "it-IT-GiuseppeMultilingualNeural",
    "fable": "it-IT-GiuseppeMultilingualNeural",
    "marin": "en-US-EmmaMultilingualNeural",
    "onyx": "fr-FR-RemyMultilingualNeural",
    "nova": "de-DE-SeraphinaMultilingualNeural",
    "sage": "fr-FR-VivienneMultilingualNeural",
    "shimmer": "en-US-EmmaMultilingualNeural",
    "verse": "ko-KR-HyunsuMultilingualNeural",
}
