class AppState:
    def __init__(self):
        self.selected_project = 0
        self.selected_menu_item = 0
        self.selected_item_idx = 0
        self.current_page = 0
        self.items_per_page = 10
        self.all_items = []
        self.current_item_detail = None
        self.detail_mode = 'content'