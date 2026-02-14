import json
import random
import time
from curl_cffi import requests

class SofaScoreScraper:
    def __init__(self):
        # Usamos a API mobile, que costuma ser menos bloqueada
        self.base_url = "https://api.sofascore.com/mobile/v4"
        
    def get_headers(self):
        # Cabeçalhos exatos de um iPhone
        return {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            "Accept": "*/*",
            "Accept-Language": "pt-BR,pt;q=0.9",
            "Referer": "https://www.sofascore.com/",
            "Origin": "https://www.sofascore.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "no-cache",
        }

    def fetch_games(self, date_str):
        # Tenta a rota padrão de eventos
        url = f"https://api.sofascore.com/api/v1/event/schedule/date/{date_str}"
        
        try:
            # O segredo: impersonate="safari15_5_ios" finge ser um iPhone real
            response = requests.get(
                url, 
                headers=self.get_headers(),
                impersonate="safari15_5_ios",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("events", [])
            else:
                print(f"Bloqueio detectado: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Erro de conexão: {e}")
            return None
