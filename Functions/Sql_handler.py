import json
import os
import sqlite3
import tempfile
import concurrent.futures
import Utilities.custom_decorators


class SQLiteHandler:
    def __init__(self, db_file=None, conn=None):
        app_data_dir = os.getenv('APPDATA')
        default_db_file = os.path.join(
            app_data_dir, "TwitchDiscordNotifications", "data.db")

        if db_file:
            self.db_file = db_file
            self.conn = sqlite3.connect(default_db_file)
        elif conn:
            self.conn = conn
        else:
            self.db_file = default_db_file
            self.conn = sqlite3.connect(default_db_file)

        self.create_tables()
        self.create_indexes()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                discord_id TEXT UNIQUE,
                streamer TEXT,
                username TEXT UNIQUE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guilds (
                guild_id TEXT UNIQUE,
                name TEXT,
                prefix TEXT,
                role_to_add TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY,
                version TEXT,
                prefix TEXT,
                bot_owner_id TEXT,
                time TEXT
            )
        ''')
        self.conn.commit()

    def create_indexes(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS streamer_index ON users (streamer);
        ''')
        self.conn.commit()

    def get_info_by_discord_id(self, discord_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM users WHERE discord_id = ?', (discord_id,))
        rows = cursor.fetchall()
        return rows

    def get_username_by_discord_id(self, discord_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT username FROM users WHERE discord_id = ?', (discord_id,))
        row = cursor.fetchone()
        return row[0] if row else None

    def add_user(self, user_data):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (discord_id, streamer, username)
            VALUES (?, ?, ?)
        ''', (
            user_data['discord_id'],
            user_data['streamer_list'][0],
            user_data['discord_username']
        ))

        if cursor.rowcount > 0:
            self.conn.commit()
            return True
        else:
            return False

    def delete_user(self, discord_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM users WHERE discord_id = ?', (discord_id,))

        if cursor.rowcount > 0:
            self.conn.commit()
            return True
        else:
            return False

    def add_streamer_to_user(self, discord_id, streamer):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT streamer FROM users WHERE discord_id = ?', (discord_id,))
            current_value = cursor.fetchone()

            if current_value is None:
                new_value = streamer
            else:
                current_value = current_value[0]
                streamers = current_value.split(',') if current_value else []

                if streamer not in streamers:
                    streamers.append(streamer)
                    new_value = ','.join(streamers)
                else:
                    new_value = current_value

            cursor.execute(
                'UPDATE users SET streamer = ? WHERE discord_id = ?', (new_value, discord_id))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def remove_streamer_from_user(self, discord_id, streamer):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT streamer FROM users WHERE discord_id = ?', (discord_id,))
        current_value = cursor.fetchone()

        if current_value is not None:
            current_value = current_value[0]
            streamers = current_value.split(',')
            if streamer in streamers:
                streamers.remove(streamer)
                new_value = ','.join(streamers)
                cursor.execute(
                    'UPDATE users SET streamer = ? WHERE discord_id = ?', (new_value, discord_id))
                self.conn.commit()
                return True

        return False

    @Utilities.custom_decorators.performance_tracker
    def get_streamers_for_user(self, discord_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT streamer FROM users WHERE discord_id = ?", (discord_id,))
        streamers_string = cursor.fetchone()

        return streamers_string[0].split(',') if streamers_string else []

    @Utilities.custom_decorators.performance_tracker
    def get_all_streamers(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT streamer FROM users")
        unique_streamers_set = set()

        for row in cursor.fetchall():
            streamers = row[0].split(',')
            unique_streamers_set.update(streamers)

        unique_streamers_list = list(unique_streamers_set)
        return unique_streamers_list

    @Utilities.custom_decorators.performance_tracker
    def get_user_ids_with_streamers(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT discord_id, streamer FROM users")
        rows = cursor.fetchall()

        user_ids_with_streamers = {}

        def process_row(row):
            discord_id, streamers_string = row
            streamers_list = streamers_string.split(',')

            if discord_id not in user_ids_with_streamers:
                user_ids_with_streamers[discord_id] = streamers_list
            else:
                user_ids_with_streamers[discord_id].extend(streamers_list)

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(process_row, rows)

        return user_ids_with_streamers

    @Utilities.custom_decorators.performance_tracker
    def get_all_user_ids(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT discord_id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
        return user_ids

    def set_version(self, new_version):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Config (id, version) VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET version = excluded.version
            """, (1, new_version))
        self.conn.commit()

    def get_version(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT version FROM config')
        version = cursor.fetchone()
        if version is not None:
            return version[0]
        else:
            return "No version found"

    def set_prefix(self, prefix):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Config (id, prefix) VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET prefix = excluded.prefix
            """, (1, prefix))
        self.conn.commit()

    def get_prefix(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT prefix FROM config')
        prefix = cursor.fetchone()
        if prefix is not None:
            return prefix[0]
        else:
            return "No prefix found"

    def get_time(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT time FROM config')
        prefix = cursor.fetchone()
        if prefix is not None:
            return prefix[0]
        else:
            return "No time found"

    def save_time(self, time):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Config (id, time) VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET time = excluded.time
            """, (1, time))
        self.conn.commit()

    def get_bot_owner_id(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT bot_owner_id FROM config')
        owner_id = cursor.fetchone()
        if owner_id is not None:
            return owner_id[0]
        else:
            return "No owner ID found"

    def save_bot_owner_id(self, owner_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Config (id, bot_owner_id) VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET bot_owner_id = excluded.bot_owner_id
            """, (1, owner_id))
        self.conn.commit()

    def create_new_guild_template(self, guild_id, guild_name):
        try:
            cursor = self.conn.cursor()

            cursor.execute(
                "SELECT guild_id FROM guilds WHERE guild_id = ?", (guild_id,))
            existing_guild = cursor.fetchone()

            if existing_guild is None:
                cursor.execute("INSERT INTO guilds (guild_id, name, prefix, role_to_add) VALUES (?, ?, ?, ?)",
                               (guild_id, guild_name, ",", None))
                self.conn.commit()

            cursor.close()
        except Exception as e:
            print(f"An error occurred: {e}")

    def is_guild_in_config(self, guild_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM guilds WHERE guild_id = ?)", (guild_id,))
        exists = cursor.fetchone()[0]
        return exists

    def get_guild_prefix(self, guild_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT prefix FROM guilds WHERE guild_id = ?", (guild_id,))
        row = cursor.fetchone()
        return row[0] if row else ""

    def remove_guild(self, guild_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM guilds WHERE guild_id = ?", (guild_id,))
        self.conn.commit()

    def change_role_to_add(self, guild_id, new_role_id):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE guilds SET role_to_add = ? WHERE guild_id = ?", (str(
            new_role_id), guild_id))
        self.conn.commit()

    def get_role_to_add(self, guild_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT role_to_add FROM guilds WHERE guild_id = ?", (guild_id,))
        row = cursor.fetchone()
        return row[0] if row else ""

    def change_guild_prefix(self, guild_id, new_prefix):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE guilds SET prefix = ? WHERE guild_id = ?", (new_prefix, guild_id))
        self.conn.commit()

    def save_to_temp_json(self, data):
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "temp_restart_data.json")

        with open(file_path, "w") as file:
            json.dump(data, file)

    @Utilities.custom_decorators.performance_tracker
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
