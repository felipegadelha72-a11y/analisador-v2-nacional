import json
import random
import time
from curl_cffi import requests

class SofaScoreScraper:
    def __init__(self, proxy_list=None):
        self.base_url = "https://api.sofascore.com/api/v1"
        self.proxy_list = proxy_list or []
        self.impersonates = ["chrome110", "chrome120", "safari17_2_ios"]
        
    def get_headers(self):
        """Headers exatos que simulam um navegador real acessando o site."""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.sofascore.com/",
            "Origin": "https://www.sofascore.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }

    def fetch_games(self, date_str):
        """Busca os jogos de uma data específica."""
        url = f"{self.base_url}/event/schedule/date/{date_str}"
        
        # Tenta primeiro sem proxy, depois rotaciona se houver proxies
        current_proxy = None
        for i in range(len(self.proxy_list) + 1):
            try:
                browser = random.choice(self.impersonates)
                
                proxies = None
                if current_proxy:
                    proxies = {"http": current_proxy, "https": current_proxy}

                response = requests.get(
                    url, 
                    headers=self.get_headers(),
                    impersonate=browser,
                    proxies=proxies,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    events = data.get("events", [])
                    return events
                else:
                    print(f"Erro {response.status_code} com {browser}")
            
            except Exception as e:
                print(f"Erro na requisição: {e}")

            # Se falhou, tenta o próximo proxy da lista
            if self.proxy_list and i < len(self.proxy_list):
                current_proxy = self.proxy_list[i]
            else:
                break
                
        return None
