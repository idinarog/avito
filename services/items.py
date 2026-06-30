
from services.avito_api import AvitoAPI
from services.auth import AuthService

class ItemService:
    def __init__(self):
        self.auth = AuthService()
        self.api = AvitoAPI(self.auth)

    def get_items(self, project):
        data, error = self.api.get_items(project)

        if error:
            return None, error

        items = data.get("items", [])

        return [self.format_item(x) for x in items], None

    def format_item(self, item):
        return {
            "id": item.get("id"),
            "title": item.get("title", "Без названия"),
            "price": item.get("price"),
            "views": item.get("stats", {}).get("views", 0),
            "calls": item.get("stats", {}).get("calls", 0),
            "messages": item.get("stats", {}).get("messages", 0),
        }
