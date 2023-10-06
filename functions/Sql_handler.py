import json
import os
import sqlite3
import tempfile

class SQLiteHandler:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                discord_id TEXT UNIQUE,
                streamer TEXT
            )
        ''')
        self.conn.commit()

    def add_user(self, discord_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO users (discord_id) VALUES (?)", (discord_id,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # User with the same discord_id already exists

    def add_streamer_to_user(self, discord_id, streamer):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users (discord_id, streamer) VALUES (?, ?)", (discord_id, streamer))
        self.conn.commit()

    def remove_streamer_from_user(self, discord_id, streamer):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM users WHERE discord_id = ? AND streamer = ?", (discord_id, streamer))
        self.conn.commit()

    def get_streamers_for_user(self, discord_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT streamer FROM users WHERE discord_id = ?", (discord_id,))
        streamers = [row[0] for row in cursor.fetchall()]
        return streamers

    def get_all_streamers(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT streamer FROM users")
        streamers = [row[0] for row in cursor.fetchall()]
        return streamers

    def get_user_ids_with_streamers(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT discord_id, streamer FROM users")
        rows = cursor.fetchall()
        user_ids_with_streamers = {}
        for row in rows:
            discord_id, streamer = row
            if discord_id not in user_ids_with_streamers:
                user_ids_with_streamers[discord_id] = [streamer]
            else:
                user_ids_with_streamers[discord_id].append(streamer)
        return user_ids_with_streamers

    def get_all_user_ids(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT discord_id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
        return user_ids

    def get_streamers_for_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT streamer FROM users WHERE discord_id = ?", (user_id,))
        streamers = [row[0] for row in cursor.fetchall()]
        return streamers

    def get_version(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = 'version'")
        row = cursor.fetchone()
        if row:
            return row[0]

    def get_prefix(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = 'prefix'")
        row = cursor.fetchone()
        if row:
            return row[0]

    def get_time(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = 'time'")
        row = cursor.fetchone()
        if row:
            return row[0]

    def save_time(self, start_time):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE config SET value = ? WHERE key = 'time'", (start_time,))
        self.conn.commit()
        

    def create_new_guild_template(self, guild_id, guild_name):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO guilds (guild_id, name, prefix, role_to_add) VALUES (?, ?, ?, ?)",
                       (guild_id, guild_name, ",", None))
        self.conn.commit()

    def is_guild_in_config(self, guild_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM guilds WHERE guild_id = ?", (guild_id,))
        count = cursor.fetchone()[0]
        return count > 0

    def get_guild_prefix(self, guild_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT prefix FROM guilds WHERE guild_id = ?", (guild_id,))
        row = cursor.fetchone()
        if row:
            return row[0]
        return ""

    def remove_guild(self, guild_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM guilds WHERE guild_id = ?", (guild_id,))
        self.conn.commit()

    def change_role_to_add(self, guild_id, new_role_id):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE guilds SET role_to_add = ? WHERE guild_id = ?", (str(new_role_id), guild_id))
        self.conn.commit()

    def get_role_to_add(self, guild_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT role_to_add FROM guilds WHERE guild_id = ?", (guild_id,))
        row = cursor.fetchone()
        if row:
            return row[0]
        return ""

    def change_guild_prefix(self, guild_id, new_prefix):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE guilds SET prefix = ? WHERE guild_id = ?", (new_prefix, guild_id))
        self.conn.commit()

    def delete_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_key FROM users WHERE discord_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            user_key = row[0]
            cursor.execute("DELETE FROM users WHERE user_key = ?", (user_key,))
            cursor.execute("SELECT user_key FROM users WHERE user_key > ?", (user_key,))
            remaining_user_keys = cursor.fetchall()
            for i, (new_user_key,) in enumerate(remaining_user_keys, start=1):
                cursor.execute("UPDATE users SET user_key = ? WHERE user_key = ?", (i, new_user_key))
            self.conn.commit()
            return True
        else:
            return False

    def save_to_temp_json(self, data):
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "temp_restart_data.json")

        with open(file_path, "w") as file:
            json.dump(data, file)

    def check_restart_status(self):
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "temp_restart_data.json")

        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                restarted = data.get("Restarted", False)

                if restarted:
                    self.processed_streamers = data.get("Streamers", [])
                    data["Restarted"] = False
                    with open(file_path, "w") as file:
                        json.dump(data, file)
                    return True
                else:
                    return False
        except FileNotFoundError:
            return False

    def get_bot_owner_id(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = 'bot_owner_id'")
        row = cursor.fetchone()
        if row:
            return row[0]
        return ""

    def save_bot_owner_id(self, owner_id):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE config SET value = ? WHERE key = 'bot_owner_id'", (owner_id,))
        self.conn.commit()