# Catálogo de Vozes / Voice Catalog 🎙️

O **OpenVoice BR Engine** suporta dois motores integrados de síntese gratuitos:
1. **Microsoft Edge-TTS:** Vozes neurais com entonação natural, incluindo suporte multilíngue e sotaques regionais.
2. **Google Translate TTS (gTTS):** Vozes via HTTP padrão, estáveis e ideais para servidores VPS de data center (Hetzner, OVH, etc.).

---

## 🇧🇷 Vozes em Português do Brasil (pt-BR)

| Alias Rápido | Nome Técnico (Edge) | Gênero | Tipo | Descrição |
| --- | --- | --- | --- | --- |
| `alloy` / `thalita` | `pt-BR-ThalitaMultilingualNeural` | Feminino | Neural Multilíngue | **Padrão do projeto**. Voz expressiva, natural e com alta clareza. |
| `antonio` | `pt-BR-AntonioNeural` | Masculino | Neural Regional | Tom sério, natural, excelente para narrações e notícias. |
| `francisca` | `pt-BR-FranciscaNeural` | Feminino | Neural Regional | Voz calorosa, amigável, ótima para atendimento e tutoriais. |
| - | `pt-BR-BrendaNeural` | Feminino | Neural Regional | Tom jovem e dinâmico. |
| - | `pt-BR-DonatoNeural` | Masculino | Neural Regional | Tom maduro e formal. |
| - | `pt-BR-ElzaNeural` | Feminino | Neural Regional | Tom suave e acolhedor. |
| - | `pt-BR-FabioNeural` | Masculino | Neural Regional | Voz jovial e conversacional. |
| - | `pt-BR-GiovannaNeural` | Feminino | Neural Regional | Clara e pausada. |
| - | `pt-BR-HumbertoNeural` | Masculino | Neural Regional | Firme e corporativa. |
| - | `pt-BR-JulioNeural` | Masculino | Neural Regional | Conversacional e fluida. |
| - | `pt-BR-LeilsonNeural` | Masculino | Neural Regional | Entonação natural e clara. |
| - | `pt-BR-LeticiaNeural` | Feminino | Neural Regional | Tom alegre e prestativo. |
| - | `pt-BR-ManuelaNeural` | Feminino | Neural Regional | Ideal para histórias e audiolivros. |
| - | `pt-BR-NicolauNeural` | Masculino | Neural Regional | Voz clássica e radiofônica. |
| - | `pt-BR-ValerioNeural` | Masculino | Neural Regional | Profissional e direto. |
| - | `pt-BR-YaraNeural` | Feminino | Neural Regional | Expressiva e envolvente. |

---

## 🇵🇹 Vozes em Português de Portugal (pt-PT)

| Nome Técnico | Gênero | Descrição |
| --- | --- | --- |
| `pt-PT-DuarteNeural` | Masculino | Português europeu, formal e claro. |
| `pt-PT-RaquelNeural` | Feminino | Português europeu, natural e comunicativa. |
| `pt-PT-FernaoNeural` | Masculino | Português europeu, tom narrativo. |

---

## 🤖 Aliases Compatíveis com a OpenAI (OpenAI Node n8n)

Se você utiliza o nó oficial da OpenAI no n8n ou SDKs compatíveis, o engine mapeia automaticamente os nomes nativos da OpenAI para vozes neurais equivalentes:

| Alias OpenAI | Voz Mapeada no Backend | Gênero | Localidade |
| --- | --- | --- | --- |
| `alloy` | `pt-BR-ThalitaMultilingualNeural` | Feminino | Brasil (Multilíngue) |
| `ash` | `en-US-AndrewMultilingualNeural` | Masculino | EUA (Multilíngue) |
| `ballad` | `en-US-BrianMultilingualNeural` | Masculino | EUA (Multilíngue) |
| `cedar` | `en-AU-WilliamMultilingualNeural` | Masculino | Austrália (Multilíngue) |
| `coral` | `en-US-AvaMultilingualNeural` | Feminino | EUA (Multilíngue) |
| `echo` | `it-IT-GiuseppeMultilingualNeural` | Masculino | Itália (Multilíngue) |
| `fable` | `it-IT-GiuseppeMultilingualNeural` | Masculino | Itália (Multilíngue) |
| `marin` | `en-US-EmmaMultilingualNeural` | Feminino | EUA (Multilíngue) |
| `onyx` | `fr-FR-RemyMultilingualNeural` | Masculino | França (Multilíngue) |
| `nova` | `de-DE-SeraphinaMultilingualNeural` | Feminino | Alemanha (Multilíngue) |
| `sage` | `fr-FR-VivienneMultilingualNeural` | Feminino | França (Multilíngue) |
| `shimmer` | `en-US-EmmaMultilingualNeural` | Feminino | EUA (Multilíngue) |
| `verse` | `ko-KR-HyunsuMultilingualNeural` | Masculino | Coreia do Sul (Multilíngue) |

> **Nota:** As vozes marcadas como **Multilíngue** são capazes de pronunciar textos em português mesmo quando seu prefixo é internacional. A síntese preserva o idioma original do texto enviado no campo `input`.

---

## 🌐 Motor Google Translate TTS (gTTS)

Quando o motor `gtts` é acionado (diretamente ou via fallback anti-bloqueio), você pode passar códigos de idioma padrão:

| Código de Voz | Idioma | Sotaque / Domínio |
| --- | --- | --- |
| `pt-br` ou `alloy` | Português | Brasil (`google.com.br`) |
| `pt-pt` | Português | Portugal (`google.pt`) |
| `en-us` ou `en` | Inglês | Estados Unidos (`google.com`) |
| `en-gb` ou `en-uk` | Inglês | Reino Unido (`google.co.uk`) |
| `es-es` ou `es` | Espanhol | Espanha (`google.es`) |
| `es-mx` | Espanhol | México (`google.com.mx`) |
| `fr-fr` ou `fr` | Francês | França (`google.fr`) |
| `de-de` ou `de` | Alemão | Alemanha (`google.de`) |
| `it-it` ou `it` | Italiano | Itália (`google.it`) |

---

## 🔍 Como Consultar o Catálogo Completo

Você pode listar todas as vozes em tempo real via linha de comando:

```bash
# Listar todas as vozes em português
python voices_catalog.py --locale pt-BR

# Listar em formato JSON
python voices_catalog.py --locale pt-BR --json

# Verificar a integridade dos aliases do voices.json
python voices_catalog.py --check-aliases
```

Ou através do endpoint da API:
```http
GET http://localhost:5050/v1/audio/voices?locale=pt-BR
```
