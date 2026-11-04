"""Testes automatizados do Multivozes BR Engine (Edge-TTS, gTTS e Fallback)."""
import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert 'gtts' in data['available_engines']
    assert 'edge-tts' in data['available_engines']


def test_models():
    response = client.get('/v1/models')
    assert response.status_code == 200
    ids = [m['id'] for m in response.json()['data']]
    assert 'tts-1' in ids
    assert 'gtts' in ids
    assert 'edge-tts' in ids


def test_voices_list():
    response = client.get('/v1/audio/voices?locale=pt-BR')
    assert response.status_code == 200
    voices = response.json()['data']
    assert len(voices) > 0
    short_names = [v['ShortName'] for v in voices]
    assert any('Thalita' in name or 'pt-BR' in name for name in short_names)


def test_speech_gtts_direct():
    payload = {
        'input': 'Teste direto com motor gTTS em português.',
        'voice': 'alloy',
        'engine': 'gtts',
        'response_format': 'mp3',
        'speed': 1.0,
    }
    response = client.post('/v1/audio/speech', json=payload)
    assert response.status_code == 200
    assert response.headers.get('content-type') == 'audio/mpeg'
    assert response.headers.get('x-tts-engine-used') == 'gtts'
    assert response.headers.get('x-tts-fallback') == 'false'
    assert len(response.content) > 1000


def test_speech_gtts_with_speed_and_wav():
    payload = {
        'input': 'Velocidade alterada no motor gTTS.',
        'voice': 'alloy',
        'engine': 'gtts',
        'response_format': 'wav',
        'speed': 1.25,
    }
    response = client.post('/v1/audio/speech', json=payload)
    assert response.status_code == 200
    assert response.headers.get('content-type') == 'audio/wav'
    assert response.headers.get('x-tts-engine-used') == 'gtts'
    assert len(response.content) > 1000


def test_speech_edge_or_auto():
    payload = {
        'input': 'Teste com motor padrão auto.',
        'voice': 'alloy',
        'response_format': 'mp3',
        'speed': 1.0,
    }
    response = client.post('/v1/audio/speech', json=payload)
    assert response.status_code == 200
    assert response.headers.get('content-type') == 'audio/mpeg'
    assert response.headers.get('x-tts-engine-used') in ('edge-tts', 'gtts')
    assert len(response.content) > 1000


def test_automatic_fallback_when_edge_fails():
    """Simula um erro no Edge-TTS (ex: 403 / Handshake) e verifica o fallback transparente para o gTTS."""
    payload = {
        'input': 'Este teste deve ativar o fallback automático para o Google TTS.',
        'voice': 'alloy',
        'engine': 'auto',
        'response_format': 'mp3',
        'speed': 1.0,
    }

    async def _mock_edge_fail(*args, **kwargs):
        raise ConnectionError("WSServerHandshakeError: 403 Forbidden (Simulado)")

    with patch('tts_handler._executar_sintese_edge', side_effect=_mock_edge_fail):
        response = client.post('/v1/audio/speech', json=payload)
        assert response.status_code == 200
        assert response.headers.get('content-type') == 'audio/mpeg'
        assert response.headers.get('x-tts-engine-used') == 'gtts'
        assert response.headers.get('x-tts-fallback') == 'true'
        assert len(response.content) > 1000

