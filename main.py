from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import requests
import random

app = FastAPI(title="Cérebro do Robô de Análises - Brasileirão 2026")

# Configurações
API_FOOTBALL_KEY = "SUA_CHAVE_AQUI"
BASE_URL = "https://v3.football.api-sports.io"
LIGAS_IDS = {
    "BRASILEIRAO": 71,
    "COPA_DO_BRASIL": 256,
    "PAULISTAO": 255
}
SEASON = 2026

class AnaliseRequest(BaseModel):
    partida_id: int
    dados_planilha: Dict[str, Any]

class Entrada(BaseModel):
    data: str
    jogo: str
    mercado: str
    entrada: str
    odd: float
    confianca: float
    metodo: str
    justificativa: str

def processar_database(rows: List[List[Any]]) -> Dict[str, Dict[str, Any]]:
    """Mapeia a aba DATABASE_ROBO para um dicionário de times"""
    db = {}
    if not rows or len(rows) < 2: return db
    
    headers = rows[0]
    for row in rows[1:]:
        if not row: continue
        time_nome = str(row[0])
        db[time_nome] = {headers[i]: row[i] for i in range(len(headers)) if i < len(row)}
    return db

def processar_metodos(rows: List[List[Any]]) -> List[Dict[str, Any]]:
    """Mapeia a aba CONFIG_METODOS"""
    metodos = []
    if not rows or len(rows) < 2: return metodos
    
    headers = rows[0]
    for row in rows[1:]:
        if not row: continue
        metodos.append({headers[i]: row[i] for i in range(len(headers)) if i < len(row)})
    return metodos

@app.post("/analisar-partida", response_model=List[Entrada])
def analisar_partida(request: AnaliseRequest):
    partida_id = request.partida_id
    raw_db = request.dados_planilha.get("database_robo", [])
    raw_metodos = request.dados_planilha.get("config_metodos", [])
    
    db_times = processar_database(raw_db)
    lista_metodos = processar_metodos(raw_metodos)
    
    # 1. Buscar dados reais da partida na API-Football
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    # fixture_data = requests.get(f"{BASE_URL}/fixtures?id={partida_id}", headers=headers).json()
    # odds_data = requests.get(f"{BASE_URL}/odds?fixture={partida_id}&bookmaker=8", headers=headers).json()
    
    # Simulação de dados da partida para o exemplo
    time_home = "Flamengo" # Exemplo
    time_away = "Palmeiras" # Exemplo
    
    analises = []
    
    # O Robô "vê" o jogo cruzando os 50 métodos com o database e stats live
    for m in lista_metodos:
        nome_metodo = m.get("Nome do Método", "Desconhecido")
        mercado_alvo = m.get("Mercado Bet365", "Todos")
        logica = m.get("Lógica Matemática (Cérebro)", "")
        
        # Simulação de cruzamento inteligente
        # O robô avalia se o time home/away no database_robo bate com a lógica do método
        score = random.uniform(0.6, 0.98)
        
        if score > 0.85:
            analises.append(Entrada(
                data="14/02/26",
                jogo=f"{time_home} x {time_away}",
                mercado=mercado_alvo,
                entrada=f"Sugestão baseada em {nome_metodo}",
                odd=round(random.uniform(1.6, 2.4), 2),
                confianca=round(score * 100, 2),
                metodo=nome_metodo,
                justificativa=f"ANÁLISE: {logica}. Cruzamento com Database: {time_home} apresenta estatísticas compatíveis."
            ))

    # Ordena por confiança e retorna as 5 melhores
    analises.sort(key=lambda x: x.confianca, reverse=True)
    return analises[:5]

@app.get("/jogos-do-dia")
def get_jogos_do_dia(data: str, ligas: Optional[str] = None):
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    ids = ligas.split(",") if ligas else [str(id) for id in LIGAS_IDS.values()]
    
    todos_jogos = []
    for liga_id in ids:
        params = {"league": liga_id, "season": SEASON, "date": data}
        res = requests.get(f"{BASE_URL}/fixtures", headers=headers, params=params).json()
        if "response" in res:
            todos_jogos.extend(res["response"])
            
    return {"response": todos_jogos}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
