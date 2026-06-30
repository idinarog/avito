"""
Репозитории для работы с базой данных
"""

class UserRepository:
    def __init__(self, db):
        self.db = db

    def get_all_active(self):
        cursor = self.db.execute("SELECT * FROM users WHERE is_active = 1")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_by_id(self, user_id):
        cursor = self.db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_by_username(self, username):
        cursor = self.db.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def create(self, username, user_id_avito):
        cursor = self.db.execute(
            "INSERT INTO users (username, user_id_avito, is_active) VALUES (?, ?, 1)",
            (username, user_id_avito)
        )
        self.db.commit()
        return cursor.lastrowid

    def update(self, user):
        self.db.execute(
            """UPDATE users SET username = ?, user_id_avito = ?, access_token = ?, refresh_token = ?, token_expires_at = ? WHERE id = ?""",
            (user['username'], user['user_id_avito'], user['access_token'], user['refresh_token'], user['token_expires_at'], user['id'])
        )
        self.db.commit()


class ProjectRepository:
    def __init__(self, db):
        self.db = db


class ItemRepository:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        cursor = self.db.execute("SELECT * FROM items")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_by_item_id(self, item_id: str):
        cursor = self.db.execute("SELECT * FROM items WHERE item_id = ?", (item_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_by_user_id(self, user_id_avito: str):
        cursor = self.db.execute("SELECT * FROM items WHERE user_id_avito = ?", (user_id_avito,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def create(self, data: dict):
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"INSERT INTO items ({columns}) VALUES ({placeholders})"
        cursor = self.db.execute(query, list(data.values()))
        self.db.commit()
        return cursor.lastrowid

    def update(self, item_id: str, data: dict):
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        values = list(data.values()) + [item_id]
        query = f"UPDATE items SET {set_clause} WHERE item_id = ?"
        self.db.execute(query, values)
        self.db.commit()
