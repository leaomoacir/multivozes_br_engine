# ==============================================================================
# OpenVoice BR Engine - Exemplos PowerShell (Windows / macOS / Linux)
# ==============================================================================

$BaseUrl = "http://localhost:5050"

Write-Host "1. Verificando estado do serviço..." -ForegroundColor Cyan
$health = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get
$health | Format-List

Write-Host "`n2. Gerando fala com voz neural brasileira (Thalita / Alloy)..." -ForegroundColor Cyan
$payloadEdge = @{
    model = "tts-1"
    input = "Olá! Teste de síntese com a voz neural brasileira Thalita no OpenVoice Engine."
    voice = "alloy"
    response_format = "mp3"
    speed = 1.0
    engine = "auto"
} | ConvertTo-Json

$bytesEdge = [System.Text.Encoding]::UTF8.GetBytes($payloadEdge)
Invoke-WebRequest -Uri "$BaseUrl/v1/audio/speech" -Method Post `
    -Body $bytesEdge -ContentType "application/json; charset=utf-8" `
    -OutFile "fala_edge_thalita.mp3"

Write-Host "Áudio salvo em: fala_edge_thalita.mp3" -ForegroundColor Green

Write-Host "`n3. Gerando fala com Google TTS direto via HTTP..." -ForegroundColor Cyan
$payloadGtts = @{
    model = "tts-1"
    input = "Olá! Este áudio foi processado via Google TTS em alta velocidade."
    voice = "alloy"
    response_format = "mp3"
    speed = 1.15
    engine = "gtts"
} | ConvertTo-Json

$bytesGtts = [System.Text.Encoding]::UTF8.GetBytes($payloadGtts)
Invoke-WebRequest -Uri "$BaseUrl/v1/audio/speech" -Method Post `
    -Body $bytesGtts -ContentType "application/json; charset=utf-8" `
    -OutFile "fala_google_gtts.mp3"

Write-Host "Áudio salvo em: fala_google_gtts.mp3" -ForegroundColor Green

