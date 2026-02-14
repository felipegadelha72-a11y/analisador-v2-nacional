from fastapi import FastAPI, Query
from curl_cffi.requests import AsyncSession

app = FastAPI(title="The Analysis Machine")

# IDs fornecidos pela Manus IA
LIGAS_IDS = {
    "brasileirao": 325,
    "paulista": 372,
    "copa_do_brasil": 373
}

@app.get("/jogos-do-dia")
async def get_jogos(data: str = Query(...)):
    url = f"https://api.sofascore.com/api/v1/event/schedule/date/{data}"
    
    try:
        async with AsyncSession() as session:
            # Simula Chrome 120 para evitar erro 403
            response = await session.get(url, impersonate="chrome120")
            
            if response.status_code == 200:
                data_json = response.json()
                eventos = data_json.get("events", [])
                
                resultado = []
                for ev in eventos:
                    u_tournament = ev.get("tournament", {}).get("uniqueTournament", {})
                    liga_id = u_tournament.get("id")
                    
                    # Verifica se o jogo pertence a uma das nossas ligas
                    if liga_id in LIGAS_IDS.values():
                        nome_liga = "Desconhecida"
                        for nome, id_liga in LIGAS_IDS.items():
                            if id_liga == liga_id:
                                nome_liga = nome.upper()

                        resultado.append({
                            "liga": nome_liga,
                            "id_evento": ev.get("id"),
                            "confronto": f"{ev.get('homeTeam', {}).get('name')} x {ev.get('awayTeam', {}).get('name')}"
                        })
                
                return {"data": data, "total_jogos": len(resultado), "jogos": resultado}
            else:
                return {"erro": f"SofaScore negou acesso (Status {response.status_code})"}
                
    except Exception as e:
        return {"erro": str(e)}

@app.get("/")
def home():
    return {"status": "The Analysis Machine Online", "metodo": "Foco Odd 1.50+"}
