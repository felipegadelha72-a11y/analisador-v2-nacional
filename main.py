from fastapi import FastAPI, Query
from curl_cffi.requests import AsyncSession

app = FastAPI()

@app.get("/jogos-do-dia")
async def get_jogos(data: str = Query(...)):
    url = f"https://api.sofascore.com/api/v1/event/schedule/date/{data}"
    
    try:
        async with AsyncSession() as session:
            # Bypass Chrome 110 para estabilidade no Render
            response = await session.get(url, impersonate="chrome110")
            
            if response.status_code == 200:
                data_json = response.json()
                eventos = data_json.get("events", [])
                
                analise_bruta = []
                for ev in eventos:
                    analise_bruta.append({
                        "id_partida": ev.get("id"),
                        "campeonato": ev.get("tournament", {}).get("name"),
                        "confronto": f"{ev.get('homeTeam', {}).get('name')} x {ev.get('awayTeam', {}).get('name')}"
                    })
                
                return {"data": data, "total_analisados": len(analise_bruta), "jogos": analise_bruta}
            else:
                return {"erro": f"Bloqueio SofaScore: {response.status_code}"}
    except Exception as e:
        return {"erro": str(e)}
