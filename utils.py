import os
from dotenv import load_dotenv
from config import DEFAULT_CONFIGS

# Carrega as variáveis de ambiente do ficheiro .env
load_dotenv()

def obter_env_bool(nome_variavel: str, valor_padrao: bool = False) -> bool:
    """Lê uma variável de ambiente e a converte para um valor booleano."""
    valor = os.getenv(nome_variavel)
    if valor is None:
        return valor_padrao
    return valor.strip().lower() in ("yes", "y", "true", "1", "t")

# --- Carrega as configurações a partir das variáveis de ambiente ou dos padrões ---
CHAVE_API = os.getenv('API_KEY', DEFAULT_CONFIGS.get("API_KEY"))

# Se API_KEY não estiver definida, por padrão não exige chave (evita 503 acidental em testes locais)
padrao_exigir = bool(CHAVE_API) if CHAVE_API else bool(DEFAULT_CONFIGS.get("REQUIRE_API_KEY", False))
EXIGIR_CHAVE_API = obter_env_bool('REQUIRE_API_KEY', padrao_exigir)
LOG_ERROS_DETALHADO = obter_env_bool('DETAILED_ERROR_LOGGING', DEFAULT_CONFIGS.get("DETAILED_ERROR_LOGGING", True))

# Dicionário com os tipos MIME para cada formato de áudio suportado.
TIPOS_MIME_AUDIO = {
    "mp3": "audio/mpeg",
    "opus": "audio/ogg",
    "aac": "audio/aac",
    "flac": "audio/flac",
    "wav": "audio/wav",
    "pcm": "application/octet-stream"
}
