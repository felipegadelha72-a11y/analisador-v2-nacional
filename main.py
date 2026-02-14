from fastapi import FastAPI, Query
from curl_cffi.requests import AsyncSession

app = FastAPI()

# Termos que queremos filtrar
CAMPEONATOS_ALVO = ["Paulista", "Brasileirão", "Copa do Brasil", "Serie A"]

@app.get("/jogos-do-dia")
async def get_jogos(data: str = Query(...)):
    url = f"https://api.sofascore.com/api/v1/event/schedule/date/{data}"
    
    try:
        async with AsyncSession() as session:
            # Bypass do seu guia (funciona 100% no Render)
            response = await session.get(url, impersonate="chrome120")
            
            if response.status_code == 200:
                data_json = response.json()
                eventos = data_json.get("events", [])
                
                resultado = []
                for ev in eventos:
                    torneio_nome = ev.get("tournament", {}).get("name", "")
                    
                    # Verifica se o nome do campeonato contém nossos alvos
                    if any(alvo.lower() in torneio_nome.lower() for alvo in CAMPEONATOS_ALVO):
                        resultado.append({
                            "campeonato": torneio_nome,
                            "confronto": f"{ev.get('homeTeam', {}).get('name')} x {ev.get('awayTeam', {}).get('name')}",
                            "id_sofa": ev.get("id")
                        })
                
                return {
                    "data_solicitada": data,
                    "total_encontrado": len(resultado),
                    "jogos": resultado
                }
            else:
                return {"erro": f"Status {response.status_code}"}
    except Exception as e:
        return {"erro": str(e)}
