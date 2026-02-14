from fastapi import FastAPI
from sofascore_final import SofaScoreScraper
import uvicorn
import os

app = FastAPI(title="The Analysis Machine API")
scraper = SofaScoreScraper()

@app.get("/")
def read_root():
    return {"message": "The Analysis Machine está online!"}

@app.get("/jogos-do-dia")
def obter_jogos(data: str):
    eventos = scraper.fetch_games(data)
    if eventos:
        return {"sucesso": True, "total": len(eventos), "jogos": eventos}
    return {"sucesso": False, "erro": "IP Bloqueado ou Data Inválida."}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
