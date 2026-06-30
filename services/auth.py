import os
import json
import time
import requests

CONFIG_PATH = os.path.expanduser("~/.avito_config.json")

class AuthService:
    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        return {}

    def save_config(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=2)

    def get_auth(self, project):
        return {
            "client_id": os.getenv(f"AVITO_{project.upper()}_CLIENT_ID"),
            "client_secret": os.getenv(f"AVITO_{project.upper()}_CLIENT_SECRET"),
            "token": self.config.get(f"{project}_token"),
            "expires": self.config.get(f"{project}_expires", 0)
        }

    def ensure_token_valid(self, project):
        auth = self.get_auth(project)

        if time.time() < auth["expires"]:
            return auth["token"]

        token, error = self.fetch_token(auth["client_id"], auth["client_secret"])

        if token:
            self.config[f"{project}_token"] = token
            self.config[f"{project}_expires"] = time.time() + 3600
            self.save_config()
            return token

        print("❌ Не удалось получить токен:", error)
        return None

    def fetch_token(self, client_id, client_secret):  # ✅ ВНУТРИ класса
        print("🔐 Запрос токена...")
        print("CLIENT_ID:", client_id)

        try:
            response = requests.post(
                "https://api.avito.ru/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret
                },
                timeout=10
            )

            print("STATUS:", response.status_code)
            print("RESPONSE:", response.text)

            if response.status_code == 200:
                return response.json().get("access_token"), None

            return None, response.text

        except Exception as e:
            print("EXCEPTION:", e)
            return None, str(e)