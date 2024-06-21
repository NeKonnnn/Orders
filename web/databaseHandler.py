import hashlib
import sqlite3

import constants
from helpers.warningAndErrorBoxes import generate_message_box
from translator import Translator
from users.user import User


class DatabaseHandler:
    def __init__(self, db_path: str, user: User = None):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.user = user

    def execute_query(self, query, parameters=None, fetch_all=True):
        """
        Execute a database query and optionally fetch the results.

        Args:
            query (str): The SQL query to execute.
            parameters (tuple, optional): The parameters for the query.
            fetch_all (bool, optional): Whether to fetch all results (True) or just one (False).

        Returns:
            list or tuple: The fetched results.
        """
        self.cursor.execute(query, parameters or ())
        if fetch_all:
            return self.cursor.fetchall()
        return self.cursor.fetchone()

    def fetch_table_data(self, table_name: str):
        return self.execute_query(f"SELECT * FROM {table_name}")

    def fetch_all_tables(self, depending_on_user: bool = False):
        tables = self.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        if depending_on_user:
            return [table[0] for table in tables if constants.allowed_to_see(self.get_user_role(self.user.user_id),
                                                                             table[0])]
        return [table[0] for table in tables]

    def fetch_table_columns(self, table_name: str):
        return [column[1] for column in self.execute_query(f"PRAGMA table_info({table_name})")]

    def insert_into_table(self, table_name: str, columns, data):
        try:
            placeholders = ", ".join(["?" for _ in data])
            self.execute_query(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})", data, False)
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            generate_message_box(self, translator=Translator(), text="Integrity Error\n" + str(e), box_type="error")

    def update_table_data(self, table_name: str, columns: list[str], data: list, conditions: list):
        update_parts = [f"{col} = ?" for col in columns]
        update_query = f"UPDATE {table_name} SET {', '.join(update_parts)} WHERE {' AND '.join([f'{col} = ?' for col in columns])}"
        self.execute_query(update_query, data + conditions, False)
        self.conn.commit()

    def delete_from_table(self, table_name: str, columns: list[str], conditions: list):
        delete_query = f"DELETE FROM {table_name} WHERE {' AND '.join([f'{col} = ?' for col in columns])}"
        self.execute_query(delete_query, conditions, False)
        self.conn.commit()

    def search_table_data(self, table_name, search_criteria):
        criteria = {k: v for k, v in search_criteria.items() if v}
        where_clause = " AND ".join([f"{col} LIKE ?" for col in criteria])
        query = f"SELECT * FROM {table_name}" + (f" WHERE {where_clause}" if criteria else "")
        return self.execute_query(query, ["%" + v + "%" for v in criteria.values()])

    def login(self, username, password):
        return self.execute_query("SELECT * FROM users WHERE username=? AND password=?",
                                  (username, self.hash_password(password)), False)

    def register(self, username: str, password: str):
        role_id = self.execute_query("SELECT id FROM user_roles WHERE role_name = 'viewer'", fetch_all=False)
        if role_id is None:
            return False
        hashed_password = self.hash_password(password)
        try:
            self.execute_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                               (username, hashed_password, role_id[0]), False)
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_login_by_user_id(self, user_id: int):
        result = self.execute_query("SELECT username FROM users WHERE id=?", (user_id,), False)
        return result[0] if result else "<no login found>"

    @staticmethod
    def hash_password(password: str):
        return hashlib.sha256(password.encode('utf-8')).hexdigest() if constants.HASH_PASSWORDS else password

    def get_user_permissions(self, user_id: int, required_permissions: list = None):
        role_id = self.execute_query("SELECT role FROM users WHERE id=?", (user_id,), False)
        if role_id:
            permissions = self.execute_query("SELECT * FROM user_roles WHERE id=?", (role_id[0],), False)
            col_names = [desc[0] for desc in self.cursor.description]
            if required_permissions:
                return {col: val for col, val in zip(col_names, permissions) if col in required_permissions}
            return {col: val for col, val in zip(col_names, permissions)}

    def get_user_role(self, user_id: int):
        role_id = self.execute_query("SELECT role FROM users WHERE id=?", (user_id,), False)
        if role_id:
            role_name = self.execute_query("SELECT role_name FROM user_roles WHERE id=?", (role_id[0],), False)
            return role_name[0] if role_name else None

    def close(self):
        self.conn.close()
