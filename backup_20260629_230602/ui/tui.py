# -*- coding: utf-8 -*-
import os
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table

console = Console()

MODE_LIST = "list"
MODE_VIEW = "view"
MODE_EDIT = "edit"


class TUI:
    def __init__(self, app):
        self.app = app
        self.mode = MODE_LIST

        self.selected_index = 0

        # 🔥 пока mock (потом заменится на API)
        self.items = [
            {"id": 1, "title": "iPhone 13", "price": 75000},
            {"id": 2, "title": "MacBook Air", "price": 120000},
            {"id": 3, "title": "iPad Pro", "price": 90000},
            {"id": 4, "title": "AirPods Pro", "price": 20000},
        ]

    def clear(self):
        os.system("clear")

    # 🚀 основной цикл
    def main_loop(self):
        while True:
            self.draw()
            key = input("> ").lower()

            # 🔴 выход
            if key == "q":
                break

            # 🔼 вверх
            elif key == "w":
                if self.selected_index > 0:
                    self.selected_index -= 1

            # 🔽 вниз
            elif key == "s":
                if self.selected_index < len(self.items) - 1:
                    self.selected_index += 1

            # 👁 просмотр (Enter или F3)
            elif key == "" or key == "3":
                self.mode = MODE_VIEW

            # ✏️ редактирование
            elif key == "4":
                self.mode = MODE_EDIT

            # 🔙 назад
            elif key == "0":
                self.mode = MODE_LIST

    # 🎨 отрисовка
    def draw(self):
        layout = self.build_layout()

        layout["header"].update(self.render_header())
        layout["left"].update(self.render_left())

        if self.mode == MODE_LIST:
            layout["right"].update(self.render_items())
        elif self.mode == MODE_VIEW:
            layout["right"].update(self.render_view())
        elif self.mode == MODE_EDIT:
            layout["right"].update(self.render_edit())

        layout["footer"].update(self.render_footer())

        console.clear()
        console.print(layout)

    # 📐 layout
    def build_layout(self):
        layout = Layout()

        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )

        layout["body"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=2),
        )

        return layout

    # 🔵 header
    def render_header(self):
        return Panel(" AVITO COMMANDER ", style="bold white on blue")

    # 🔵 footer
    def render_footer(self):
        return Panel(
            "W/S Навигация | Enter/F3 Просмотр | F4 Редактирование | 0 Назад | q Выход",
            style="white on blue",
        )

    # 📁 левая панель
    def render_left(self):
        structure = [
            "📁 ВСЕ",
            "📁 ПАПКИ",
            "📁 ТЕГИ",
            "📁 КАМПАНИИ",
        ]

        text = "\n".join(structure)

        return Panel(text, title="Структура", style="white on blue")

    # 📋 список объявлений
    def render_items(self):
        if not self.items:
            return Panel("Нет объявлений", style="white on blue")

        table = Table(expand=True)

        table.add_column("ID", width=6)
        table.add_column("Название")
        table.add_column("Цена", justify="right")

        for i, item in enumerate(self.items):
            style = "black on white" if i == self.selected_index else ""

            table.add_row(
                str(item["id"]),
                item["title"],
                str(item["price"]),
                style=style,
            )

        return Panel(table, title="Объявления", style="white on blue")

    # 👁 просмотр
    def render_view(self):
        if not self.items:
            return Panel("Нет данных", style="white on blue")

        item = self.items[self.selected_index]

        text = (
            f"ID: {item['id']}\n"
            f"Название: {item['title']}\n"
            f"Цена: {item['price']}"
        )

        return Panel(text, title="Просмотр", style="white on blue")

    # ✏️ редактирование
    def render_edit(self):
        return Panel(
            "✏️ Редактирование\n\n[форма будет позже]",
            title="Редактирование",
            style="white on blue",
        )