import os
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import chromadb
import anthropic
import psycopg2

app = FastAPI(title="Sentinel AI - Assistente de Investimentos")

# Conecta ChromaDB
chroma_client = chromadb.HttpClient(host="localhost", port=8000)
collection = chroma_client.get_or_create_collection("sentinel_btc")

def get_conn():
    return psycopg2.connect(
        host="172.17.0.4",
        database="sentinel_btc",
        user="postgres",
        password=os.environ.get("PG_PASSWORD")
    )

# ── Modelos ──────────────────────────────────────────────
class Pergunta(BaseModel):
    texto: str

class ClienteBody(BaseModel):
    token: str
    nome: str
    email: Optional[str] = None
    idioma: Optional[str] = "pt"

class ClienteUpdateBody(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    idioma: Optional[str] = None
    notas: Optional[str] = None

class TrancheBody(BaseModel):
    token: str
    numero: int
    classe: str
    nome: str
    descricao: Optional[str] = None
    valor: Optional[str] = None
    status: Optional[str] = "pendente"

class TrancheUpdateBody(BaseModel):
    numero: Optional[int] = None
    classe: Optional[str] = None
    nome: Optional[str] = None
    descricao: Optional[str] = None
    valor: Optional[str] = None
    status: Optional[str] = None

class SignalBody(BaseModel):
    token: str
    categoria: str
    texto: str
    subtexto: Optional[str] = None
    checked: Optional[bool] = False
    ordem: Optional[int] = 0

class SignalUpdateBody(BaseModel):
    categoria: Optional[str] = None
    texto: Optional[str] = None
    subtexto: Optional[str] = None
    checked: Optional[bool] = None
    ordem: Optional[int] = None

class PlaybookBody(BaseModel):
    titulo: Optional[str] = None
    step_atual: Optional[int] = 1
    alert_texto: Optional[str] = None
    alert_sub: Optional[str] = None

class PlaybookStepBody(BaseModel):
    token: str
    numero: int
    label: str
    status: Optional[str] = "pending"

class PlaybookStepUpdateBody(BaseModel):
    numero: Optional[int] = None
    label: Optional[str] = None
    status: Optional[str] = None

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
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT nome, email, notas, idioma FROM clientes WHERE token=%s AND ativo=true", (token,))
        cliente = cur.fetchone()

        if not cliente:
            cur.close(); conn.close()
            return JSONResponse(status_code=401, content={"error": "Token inválido"})

        cur.execute("SELECT numero, classe, nome, descricao, valor, status FROM tranches WHERE token=%s ORDER BY numero", (token,))
        tranches = cur.fetchall()

        cur.close(); conn.close()

        return {
            "client_name": cliente[0],
            "email": cliente[1],
            "notas": cliente[2],
            "idioma": cliente[3] or "pt",
            "tranches": [
                {"numero": t[0], "classe": t[1], "nome": t[2], "descricao": t[3], "valor": t[4], "status": t[5]}
                for t in tranches
            ]
        }
    except Exception as e:
        return {"error": str(e)}


# ══════════════════════════════════════════════════════════
# ADMIN ENDPOINTS
# ══════════════════════════════════════════════════════════

# ── Auth ─────────────────────────────────────────────────
@app.get("/admin/auth")
def admin_auth(senha: str = Query(...)):
    if senha == os.environ.get("ADMIN_PASSWORD"):
        return {"ok": True}
    return JSONResponse(status_code=401, content={"ok": False})


# ── Clientes ─────────────────────────────────────────────
@app.get("/admin/clientes")
def admin_list_clientes():
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT token, nome, email, idioma, ativo, criado_em FROM clientes ORDER BY criado_em DESC")
        rows = cur.fetchall()
        cur.close(); conn.close()
        return [
            {"token": r[0], "nome": r[1], "email": r[2], "idioma": r[3], "ativo": r[4], "criado_em": str(r[5])}
            for r in rows
        ]
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/admin/cliente")
def admin_create_cliente(body: ClienteBody):
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute(
            "INSERT INTO clientes (token, nome, email, idioma) VALUES (%s, %s, %s, %s)",
            (body.token, body.nome, body.email, body.idioma)
        )
        conn.commit(); cur.close(); conn.close()
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.put("/admin/cliente/{token}")
def admin_update_cliente(token: str, body: ClienteUpdateBody):
    try:
        conn = get_conn(); cur = conn.cursor()
        fields, values = [], []
        if body.nome   is not None: fields.append("nome=%s");   values.append(body.nome)
        if body.email  is not None: fields.append("email=%s");  values.append(body.email)
        if body.idioma is not None: fields.append("idioma=%s"); values.append(body.idioma)
        if body.notas  is not None: fields.append("notas=%s");  values.append(body.notas)
        if not fields:
            return {"ok": True}
        values.append(token)
        cur.execute(f"UPDATE clientes SET {', '.join(fields)} WHERE token=%s", values)
        conn.commit(); cur.close(); conn.close()
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ── Tranches ─────────────────────────────────────────────
@app.get("/admin/tranches")
def admin_list_tranches(token: str = Query(...)):
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute(
            "SELECT id, numero, classe, nome, descricao, valor, status FROM tranches WHERE token=%s ORDER BY numero",
            (token,)
        )
        rows = cur.fetchall()
        cur.close(); conn.close()
        return [
            {"id": r[0], "numero": r[1], "classe": r[2], "nome": r[3], "descricao": r[4], "valor": r[5], "status": r[6]}
            for r in rows
        ]
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/admin/tranche")
def admin_create_tranche(body: TrancheBody):
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute(
            "INSERT INTO tranches (token, numero, classe, nome, descricao, valor, status) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (body.token, body.numero, body.classe, body.nome, body.descricao, body.valor, body.status)
        )
        conn.commit(); cur.close(); conn.close()
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.put("/admin/tranche/{id}")
def admin_update_tranche(id: int, body: TrancheUpdateBody):
    try:
        conn = get_conn(); cur = conn.cursor()
        fields, values = [], []
        if body.numero   is not None: fields.append("numero=%s");   values.append(body.numero)
        if body.classe   is not None: fields.append("classe=%s");   values.append(body.classe)
        if body.nome     is not None: fields.append("nome=%s");     values.append(body.nome)
        if body.descricao is not None: fields.append("descricao=%s"); values.append(body.descricao)
        if body.valor    is not None: fields.append("valor=%s");    values.append(body.valor)
        if body.status   is not None: fields.append("status=%s");   values.append(body.status)
        if not fields:
            return {"ok": True}
        values.append(id)
        cur.execute(f"UPDATE tranches SET {', '.join(fields)} WHERE id=%s", values)
        conn.commit(); cur.close(); conn.close()
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.delete("/admin/tranche/{id}")
def admin_delete_tranche(id: int):
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute("DELETE FROM tranches WHERE id=%s", (id,))
        conn.commit(); cur.close(); conn.close()
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ── Signals ──────────────────────────────────────────────
@app.get("/admin/signals")
def admin_list_signals(token: str = Query(...)):
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute(
            "SELECT id, categoria, texto, subtexto, checked, ordem FROM signals WHERE token=%s ORDER BY ordem",
            (token,)
        )
        rows = cur.fetchall()
        cur.close(); conn.close()
        return [
            {"id": r[0], "categoria": r[1], "texto": r[2], "subtexto": r[3], "checked": r[4], "ordem": r[5]}
            for r in rows
        ]
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/admin/signal")
def admin_create_signal(body: SignalBody):
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute(
            "INSERT INTO signals (token, categoria, texto, subtexto, checked, ordem) VALUES (%s,%s,%s,%s,%s,%s)",
            (body.token, body.categoria, body.texto, body.subtexto, body.checked, body.ordem)
        )
        conn.commit(); cur.close(); conn.close()
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.put("/admin/signal/{id}")
def admin_update_signal(id: int, body: SignalUpdateBody):
    try:
        conn = get_conn(); cur = conn.cursor()
        fields, values = [], []
        if body.categoria is not None: fields.append("categoria=%s"); values.append(body.categoria)
        if body.texto     is not None: fields.append("texto=%s");     values.append(body.texto)
        if body.subtexto  is not None: fields.append("subtexto=%s");  values.append(body.subtexto)
        if body.checked   is not None: fields.append("checked=%s");   values.append(body.checked)
        if body.ordem     is not None: fields.append("ordem=%s");     values.append(body.ordem)
        if not fields:
            return {"ok": True}
        values.append(id)
        cur.execute(f"UPDATE signals SET {', '.join(fields)} WHERE id=%s", values)
        conn.commit(); cur.close(); conn.close()
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.delete("/admin/signal/{id}")
def admin_delete_signal(id: int):
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute("DELETE FROM signals WHERE id=%s", (id,))
        conn.commit(); cur.close(); conn.close()
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ── Playbook ─────────────────────────────────────────────
@app.get("/admin/playbook")
def admin_get_playbook(token: str = Query(...)):
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute(
            "SELECT titulo, step_atual, alert_texto, alert_sub FROM playbook WHERE token=%s",
            (token,)
        )
        pb = cur.fetchone()
        if not pb:
            cur.close(); conn.close()
            return JSONResponse(status_code=404, content={"error": "Playbook não encontrado"})
        cur.execute(
            "SELECT id, numero, label, status FROM playbook_steps WHERE token=%s ORDER BY numero",
            (token,)
        )
        steps = cur.fetchall()
        cur.close(); conn.close()
        return {
            "titulo":      pb[0],
            "step_atual":  pb[1],
            "alert_texto": pb[2],
            "alert_sub":   pb[3],
            "steps": [
                {"id": s[0], "numero": s[1], "label": s[2], "status": s[3]}
                for s in steps
            ]
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.put("/admin/playbook/{token}")
def admin_upsert_playbook(token: str, body: PlaybookBody):
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT 1 FROM playbook WHERE token=%s", (token,))
        exists = cur.fetchone()
        if exists:
            cur.execute(
                "UPDATE playbook SET titulo=%s, step_atual=%s, alert_texto=%s, alert_sub=%s WHERE token=%s",
                (body.titulo, body.step_atual, body.alert_texto, body.alert_sub, token)
            )
        else:
            cur.execute(
                "INSERT INTO playbook (token, titulo, step_atual, alert_texto, alert_sub) VALUES (%s,%s,%s,%s,%s)",
                (token, body.titulo, body.step_atual, body.alert_texto, body.alert_sub)
            )
        conn.commit(); cur.close(); conn.close()
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/admin/playbook_step")
def admin_create_step(body: PlaybookStepBody):
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute(
            "INSERT INTO playbook_steps (token, numero, label, status) VALUES (%s,%s,%s,%s)",
            (body.token, body.numero, body.label, body.status)
        )
        conn.commit(); cur.close(); conn.close()
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.put("/admin/playbook_step/{id}")
def admin_update_step(id: int, body: PlaybookStepUpdateBody):
    try:
        conn = get_conn(); cur = conn.cursor()
        fields, values = [], []
        if body.numero is not None: fields.append("numero=%s"); values.append(body.numero)
        if body.label  is not None: fields.append("label=%s");  values.append(body.label)
        if body.status is not None: fields.append("status=%s"); values.append(body.status)
        if not fields:
            return {"ok": True}
        values.append(id)
        cur.execute(f"UPDATE playbook_steps SET {', '.join(fields)} WHERE id=%s", values)
        conn.commit(); cur.close(); conn.close()
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.delete("/admin/playbook_step/{id}")
def admin_delete_step(id: int):
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute("DELETE FROM playbook_steps WHERE id=%s", (id,))
        conn.commit(); cur.close(); conn.close()
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Rota de health check
@app.get("/")
def health():
    return {"status": "online", "servico": "Sentinel AI"}
