# CLAUDE.md — Sentinel Invest / AILo Project

## Visão Geral
AILo é um assessor de inteligência de mercado pessoal.
- Landing page: sentinelinvest.co
- Dashboard: app.sentinelinvest.co
- Bot Telegram: @rogo02_ai_bot

## Stack do Servidor (192.168.1.95)
- FastAPI porta 8001 — sentinel-ai.service
- nginx Docker — porta 8080
- PostgreSQL Docker — 172.17.0.4:5432
- ChromaDB Docker — porta 8000
- n8n Docker — 172.17.0.6:5678
- Cloudflare Tunnel — app.sentinelinvest.co

## Paths importantes
- API: /home/rogo/rag/api.py
- Briefing: /home/rogo/rag/daily_briefing.py
- Coleta: /home/rogo/rag/market_data.py
- Dashboard: /home/rogo/ailo_dashboard.html
- Logs: /home/rogo/logs/

## REGRA DE OURO — Nunca violar
- NUNCA hardcodar credenciais no código
- SEMPRE usar os.environ.get("VARIAVEL")
- NUNCA commitar secrets no GitHub

## Variáveis de ambiente (sentinel-ai.service)
- ANTHROPIC_API_KEY
- PG_PASSWORD
- FRED_API_KEY
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID

## PostgreSQL
- Host: 172.17.0.4
- Database: sentinel_btc
- User: postgres
- Tabelas: clientes, tranches, market_snapshots

## Comandos frequentes

Atualizar dashboard:
docker cp /home/rogo/ailo_dashboard.html nginx-dashboard:/usr/share/nginx/html/ailo_dashboard.html

Reiniciar API:
sudo systemctl restart sentinel-ai.service

Recarregar nginx:
docker exec nginx-dashboard nginx -s reload

## Adicionar novo cliente
INSERT INTO clientes (token, nome, email, idioma)
VALUES ('ailo-nome-XXXXXXXX', 'Nome', 'email', 'pt');

## Nunca alterar sem aprovação
- Schema PostgreSQL
- Cloudflare Tunnel config
- nginx locations
- Token pattern dos clientes
