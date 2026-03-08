import os
from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
import anthropic
import psycopg2
from fastapi import Query

app = FastAPI(title="Sentinel AI - Assistente de Investimentos")

# Conecta ChromaDB
chroma_client = chromadb.HttpClient(host="localhost", port=8000)
collection = chroma_client.get_or_create_collection("sentinel_btc")

# Modelo da requisição
class Pergunta(BaseModel):
    texto: str

# Rota principal
@app.post("/perguntar")
def perguntar(pergunta: Pergunta):
    # Busca documentos relevantes
    resultado = collection.query(
        query_texts=[pergunta.texto],
        n_results=6
    )
    
    contexto = "\n".join(resultado['documents'][0])
    
    # Claude responde
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    resposta = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""Você é um assistente de investimentos pessoal.

Use apenas estas informações da estratégia do usuário:
{contexto}

Pergunta: {pergunta.texto}

Responda de forma direta e prática em português brasileiro."""
        }]
    )
    
    return {
        "pergunta": pergunta.texto,
        "resposta": resposta.content[0].text,
        "contexto_usado": resultado['documents'][0]
    }
@app.get("/cliente")
def get_cliente(token: str = Query(...)):
    try:
        conn = psycopg2.connect(
            host="172.17.0.4",
            database="sentinel_btc",
            user="postgres",
            password=os.environ.get("PG_PASSWORD")
        )
        cur = conn.cursor()
        
        cur.execute("SELECT nome, email, notas FROM clientes WHERE token=%s AND ativo=true", (token,))
        cliente = cur.fetchone()
        
        if not cliente:
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=401, content={"error": "Token inválido"})
        
        cur.execute("SELECT numero, classe, nome, descricao, valor, status FROM tranches WHERE token=%s ORDER BY numero", (token,))
        tranches = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return {
            "client_name": cliente[0],
            "email": cliente[1],
            "notas": cliente[2],
            "tranches": [
                {"numero": t[0], "classe": t[1], "nome": t[2], "descricao": t[3], "valor": t[4], "status": t[5]}
                for t in tranches
            ]
        }
    except Exception as e:
        return {"error": str(e)}

# Rota de health check
@app.get("/")
def health():
    return {"status": "online", "servico": "Sentinel AI"}
