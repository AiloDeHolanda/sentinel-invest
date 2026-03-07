<div align="center">

# ⚡ Sentinel Invest — AILo

### Seu assessor de investimentos pessoal, potencializado por IA

![Versão](https://img.shields.io/badge/versão-1.2.0-orange?style=flat-square)
![Status](https://img.shields.io/badge/status-live-brightgreen?style=flat-square)
![Idiomas](https://img.shields.io/badge/idiomas-PT%20%7C%20ES%20%7C%20EN-blue?style=flat-square)
![Early Adopter](https://img.shields.io/badge/🚀_Early_Adopter-$29%2Fmês-orange?style=flat-square)

</div>

---

## O que é o Sentinel Invest

O **Sentinel Invest** é um serviço personalizado de assessoria de investimentos entregue via **Telegram**, potencializado pelo **AILo** — _Artificial Intelligence Language Oracle_.

Não é um software genérico. Não é um dashboard com gráficos bonitos. É um assessor que **conhece a sua carteira real** — seus ativos, seu histórico de aportes, sua estratégia e seus objetivos — e usa esse contexto para entregar análises e alertas feitos especificamente para você.

> *"Não conselhos genéricos. Análise baseada na sua carteira real."*

### O que torna o AILo diferente

- **Contexto real**: no onboarding, mapeamos sua carteira atual, histórico de aportes, estratégia e objetivos. O AILo parte do seu contexto específico — não de um perfil genérico.
- **Análise personalizada**: quando o mercado se move, o alerta que chega não é genérico. É contextualizado para a sua posição, a sua estratégia e o seu momento.
- **Evolui com você**: cada interação enriquece o contexto. Quanto mais tempo de uso, mais preciso e útil o assessor fica.
- **Presença latino-americana**: suporte nativo a Fintual, Nomad, Nu Invest, XP, exchanges cripto e carteiras multi-câmbio (BRL/CLP/USD).

---

## Como funciona

```
1. Onboarding personalizado
   └── Você conta sobre sua carteira, plataformas, estratégia e objetivos

2. Configuração do contexto (RAG)
   └── Seus documentos e dados são vetorizados no ChromaDB
   └── O AILo passa a conhecer você antes de monitorar o primeiro ativo

3. Assessoria contínua via Telegram 24/7
   ├── Alertas contextualizados quando algo relevante acontece
   ├── Análises sob demanda (pergunte qualquer coisa)
   └── Revisões periódicas da carteira
```

### RAG com dados reais do cliente

O coração técnico do serviço é **Retrieval-Augmented Generation** alimentado pelos dados reais de cada cliente:

| Dado | Descrição |
|---|---|
| Carteira atual | Ativos, proporções, moedas |
| Histórico de aportes | Quando comprou, a que preço, com qual intenção |
| Estratégia declarada | Perfil de risco, horizonte, metas |
| Preferências | Setores que evita, exposição máxima, etc. |
| Histórico de interações | Perguntas anteriores, decisões tomadas |

---

## 🚀 Early Adopter

Os primeiros **50 clientes** têm acesso a condições especiais com **preço travado para sempre**:

| Fase | Preço | Condição |
|---|---|---|
| Early Adopter (primeiros 50) | **$29/mês** | Preço travado enquanto mantiver assinatura ativa |
| Regular | $49/mês | Após esgotamento das vagas Early Adopter |

> O preço Early Adopter é garantido permanentemente — nunca aumenta enquanto a assinatura estiver ativa.

---

## Stack técnica

```
Backend & Orquestração
├── n8n               — automação de workflows e agentes
├── FastAPI           — API para integração e webhooks
└── PostgreSQL        — armazenamento de leads e dados estruturados

IA & RAG
├── ChromaDB          — banco de vetores para documentos da carteira
└── LLM               — modelo de linguagem para geração de análises

Canal de entrega
└── Telegram Bot      — interface principal de comunicação com o cliente

Frontend
└── Landing page      — HTML/CSS/JS vanilla, dark mode, trilíngue (PT/ES/EN)
```

---

## Estrutura do repositório

```
sentinel-invest/
├── index.html        # Landing page (PT/ES/EN, dark mode)
├── IDEA.md           # Documento de posicionamento do produto
└── README.md         # Este arquivo
```

---

## Links

| | |
|---|---|
| 🌐 Landing page | [sentinelinvest.co](https://sentinelinvest.co) |
| 📬 Contato | Via formulário na landing page |

---

<div align="center">

*Sentinel Invest · v1.2.0 · Março 2026*

</div>
