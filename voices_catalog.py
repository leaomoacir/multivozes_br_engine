"""Consulta o catálogo real do Edge sem alterar aliases nem gerar áudio, com fallback para catálogo estático."""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

import edge_tts
from dotenv import load_dotenv

logger = logging.getLogger("multivozes.voices")

CATALOGO_BACKUP = [
    {"Name": "Microsoft Server Speech Text to Speech Voice (pt-BR, ThalitaMultilingualNeural)", "ShortName": "pt-BR-ThalitaMultilingualNeural", "Gender": "Female", "Locale": "pt-BR"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (pt-BR, AntonioNeural)", "ShortName": "pt-BR-AntonioNeural", "Gender": "Male", "Locale": "pt-BR"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (pt-BR, FranciscaNeural)", "ShortName": "pt-BR-FranciscaNeural", "Gender": "Female", "Locale": "pt-BR"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (pt-BR, BrendaNeural)", "ShortName": "pt-BR-BrendaNeural", "Gender": "Female", "Locale": "pt-BR"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (pt-BR, DonatoNeural)", "ShortName": "pt-BR-DonatoNeural", "Gender": "Male", "Locale": "pt-BR"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (pt-BR, ElzaNeural)", "ShortName": "pt-BR-ElzaNeural", "Gender": "Female", "Locale": "pt-BR"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (pt-BR, FabioNeural)", "ShortName": "pt-BR-FabioNeural", "Gender": "Male", "Locale": "pt-BR"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (pt-BR, GiovannaNeural)", "ShortName": "pt-BR-GiovannaNeural", "Gender": "Female", "Locale": "pt-BR"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (pt-BR, HumbertoNeural)", "ShortName": "pt-BR-HumbertoNeural", "Gender": "Male", "Locale": "pt-BR"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (pt-BR, JulioNeural)", "ShortName": "pt-BR-JulioNeural", "Gender": "Male", "Locale": "pt-BR"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (pt-BR, LeticiaNeural)", "ShortName": "pt-BR-LeticiaNeural", "Gender": "Female", "Locale": "pt-BR"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (pt-BR, ManuelaNeural)", "ShortName": "pt-BR-ManuelaNeural", "Gender": "Female", "Locale": "pt-BR"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (pt-BR, NicolauNeural)", "ShortName": "pt-BR-NicolauNeural", "Gender": "Male", "Locale": "pt-BR"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (pt-BR, ValerioNeural)", "ShortName": "pt-BR-ValerioNeural", "Gender": "Male", "Locale": "pt-BR"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (pt-BR, YaraNeural)", "ShortName": "pt-BR-YaraNeural", "Gender": "Female", "Locale": "pt-BR"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (pt-PT, DuarteNeural)", "ShortName": "pt-PT-DuarteNeural", "Gender": "Male", "Locale": "pt-PT"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (pt-PT, RaquelNeural)", "ShortName": "pt-PT-RaquelNeural", "Gender": "Female", "Locale": "pt-PT"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (en-US, AndrewMultilingualNeural)", "ShortName": "en-US-AndrewMultilingualNeural", "Gender": "Male", "Locale": "en-US"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (en-US, BrianMultilingualNeural)", "ShortName": "en-US-BrianMultilingualNeural", "Gender": "Male", "Locale": "en-US"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (en-US, AvaMultilingualNeural)", "ShortName": "en-US-AvaMultilingualNeural", "Gender": "Female", "Locale": "en-US"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (en-US, EmmaMultilingualNeural)", "ShortName": "en-US-EmmaMultilingualNeural", "Gender": "Female", "Locale": "en-US"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (en-AU, WilliamMultilingualNeural)", "ShortName": "en-AU-WilliamMultilingualNeural", "Gender": "Male", "Locale": "en-AU"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (it-IT, GiuseppeMultilingualNeural)", "ShortName": "it-IT-GiuseppeMultilingualNeural", "Gender": "Male", "Locale": "it-IT"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (fr-FR, RemyMultilingualNeural)", "ShortName": "fr-FR-RemyMultilingualNeural", "Gender": "Male", "Locale": "fr-FR"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (fr-FR, VivienneMultilingualNeural)", "ShortName": "fr-FR-VivienneMultilingualNeural", "Gender": "Female", "Locale": "fr-FR"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (de-DE, SeraphinaMultilingualNeural)", "ShortName": "de-DE-SeraphinaMultilingualNeural", "Gender": "Female", "Locale": "de-DE"},
    {"Name": "Microsoft Server Speech Text to Speech Voice (ko-KR, HyunsuMultilingualNeural)", "ShortName": "ko-KR-HyunsuMultilingualNeural", "Gender": "Male", "Locale": "ko-KR"},
    {"Name": "Google Translate TTS (pt-BR)", "ShortName": "gtts-pt-BR", "Gender": "Neutral", "Locale": "pt-BR"},
    {"Name": "Google Translate TTS (en-US)", "ShortName": "gtts-en-US", "Gender": "Neutral", "Locale": "en-US"},
]


async def get_voices(locale=None, multilingual=False):
    """Lista vozes atuais; locale aceita idioma (pt) ou localidade (pt-BR).

    Se a consulta remota ao Edge falhar (como em VPS com IP bloqueado), utiliza o
    catálogo de backup garantindo que a API nunca falhe.
    """
    load_dotenv(Path(__file__).with_name(".env"))
    try:
        voices = await asyncio.wait_for(
            edge_tts.list_voices(proxy=os.getenv("PROXY") or None), timeout=15
        )
    except Exception as exc:
        logger.warning(
            "Não foi possível consultar catálogo remoto Edge (%s: %s). Usando catálogo estático de backup.",
            type(exc).__name__, exc
        )
        voices = CATALOGO_BACKUP

    if locale:
        requested = locale.casefold()
        voices = [
            voice for voice in voices
            if voice.get("Locale", "").casefold() == requested
            or voice.get("Locale", "").casefold().startswith(requested + "-")
        ]
    if multilingual:
        voices = [voice for voice in voices if "MultilingualNeural" in voice.get("ShortName", "")]
    return sorted(voices, key=lambda voice: voice.get("ShortName", ""))


async def _run(args):
    if args.check_aliases:
        all_voices = await get_voices()
        available = {voice["ShortName"] for voice in all_voices}
        aliases = json.loads(Path(__file__).with_name("voices.json").read_text(encoding="utf-8"))
        missing = {alias: voice for alias, voice in aliases.items() if voice not in available}
        print(json.dumps({"aliases": aliases, "unavailable": missing}, ensure_ascii=False, indent=2))
        return 1 if missing else 0
    voices = await get_voices(args.locale, args.multilingual)
    if args.json:
        print(json.dumps(voices, ensure_ascii=False, indent=2))
    else:
        for voice in voices:
            print(f"{voice['ShortName']:<45} {voice.get('Gender', 'Unknown'):<8} {voice.get('Locale', '')}")
        print(f"Total: {len(voices)}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locale", help="Idioma/localidade, por exemplo pt ou pt-BR")
    parser.add_argument("--multilingual", action="store_true", help="Somente MultilingualNeural")
    parser.add_argument("--json", action="store_true", help="Exibir metadados em JSON")
    parser.add_argument("--check-aliases", action="store_true", help="Verificar voices.json no catálogo completo")
    args = parser.parse_args()
    try:
        return asyncio.run(_run(args))
    except Exception as exc:
        print(f"Não foi possível consultar o catálogo: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
