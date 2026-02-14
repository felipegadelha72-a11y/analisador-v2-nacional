from fastapi import FastAPI, Query
from curl_cffi.requests import AsyncSession

app = FastAPI(title="The Analysis Machine - SofaSource")

# Mapeamento das ligas
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

    url = f"https://api.sofascore.com/api/v1/event/schedule/date/{data}"
    
    try:
        # Usando o 'impersonate' para fingir ser um Chrome real (Bypass 403)
        async with AsyncSession() as session:
            response = await session.get(url, impersonate="chrome120")
            
            if response.status_code == 200:
                data_json = response.json()
                eventos = data_json.get("events", [])
                
                resultado = []
                for evento in eventos:
                    if evento.get("tournament", {}).get("uniqueTournament", {}).get("id") == sofa_liga_id:
                        resultado.append({
                            "fixture": {"id": evento.get("id")},
                            "teams": {
                                "home": {"name": evento.get("homeTeam", {}).get("name")},
                                "away": {"name": evento.get("awayTeam", {}).get("name")}
                            }
                        })
                return {"response": resultado}
            else:
                return {"response": [], "error": f"Erro SofaScore: {response.status_code}"}
                
    except Exception as e:
        return {"response": [], "error": str(e)}

@app.get("/")
def home():
    return {"status": "The Analysis Machine - Online via Bypass"}
