from fastapi import FastAPI, Query
import httpx

app = FastAPI(title="The Analysis Machine - SofaSource")

# Disfarce reforçado para evitar o erro 403
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://www.sofascore.com",
    "Referer": "https://www.sofascore.com/",
    "Cache-Control": "max-age=0"
}

SOFA_LIGAS = {
    "71": 325,   # Brasileirão
    "255": 414,  # Paulistão
    "256": 329   # Copa do Brasil
}

@app.get("/jogos-do-dia")
async def get_jogos(data: str = Query(...), ligas: str = Query(...)):
    sofa_liga_id = SOFA_LIGAS.get(ligas)
    if not sofa_liga_id:
        return {"response": [], "error": "Liga nao mapeada"}

    # Usamos a URL de eventos do dia
    url = f"https://api.sofascore.com/api/v1/event/schedule/date/{data}"
    
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        try:
            response = await client.get(url)
            if response.status_code != 200:
                return {"response": [], "error": f"Erro SofaScore: {response.status_code}"}
            
            data_json = response.json()
            eventos = data_json.get("events", [])
            
            resultado = []
            for evento in eventos:
                # Filtra pela liga
                if evento.get("tournament", {}).get("uniqueTournament", {}).get("id") == sofa_liga_id:
                    resultado.append({
                        "fixture": {"id": evento.get("id")},
                        "teams": {
                            "home": {"name": evento.get("homeTeam", {}).get("name")},
                            "away": {"name": evento.get("awayTeam", {}).get("name")}
                        }
                    })
            
            return {"response": resultado}
        except Exception as e:
            return {"response": [], "error": str(e)}

@app.get("/")
def home():
    return {"status": "The Analysis Machine - SofaSource Ativa"}
