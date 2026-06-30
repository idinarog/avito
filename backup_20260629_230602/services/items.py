class ItemService:
    def __init__(self, api):
        self.api = api

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
            "conversions": item.get("stats", {}).get("conversions", 0),
        }