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
                version TEXT,
                prefix TEXT,
                bot_owner_id TEXT,
                time TEXT
            )
        ''')
        self.conn.commit()

    '''works'''
    def get_info_by_discord_id(self, discord_id):
        cursor = self.conn.cursor()
        # Retrieve all information for the specified Discord ID
        cursor.execute('SELECT * FROM users WHERE discord_id = ?', (discord_id,))
        rows = cursor.fetchall()
        # Return the retrieved rows
        return rows

    '''works'''
    def get_username_by_discord_id(self, discord_id):
        cursor = self.conn.cursor()

        # Retrieve the username for the specified Discord ID
        cursor.execute('SELECT username FROM users WHERE discord_id = ?', (discord_id,))
        row = cursor.fetchone()

        # Return the retrieved username
        if row is not None:
            return row[0]
        else:
            return None    

    '''works'''
    def add_username(self, discord_id, username):
        cursor = self.conn.cursor()
        # Check if the Discord ID already exists in the table
        cursor.execute('SELECT * FROM users WHERE discord_id = ?', (discord_id,))
        existing_row = cursor.fetchone()

        if existing_row is not None:
            # Discord ID already exists, update the username
            cursor.execute('UPDATE users SET username = ? WHERE discord_id = ?', (username, discord_id))
        else:
            # Discord ID does not exist, insert a new row with the Discord ID and username
            cursor.execute('INSERT INTO users (discord_id, username) VALUES (?, ?)', (discord_id, username))

    '''works'''
    def add_user(self, discord_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT discord_id FROM users WHERE discord_id = ?', (discord_id,))
        existing_id = cursor.fetchone()

        # If the Discord ID does not exist, insert a new row with the specified Discord ID
        if existing_id is None:
            cursor.execute('INSERT INTO users (discord_id) VALUES (?)', (discord_id,))
        
        self.conn.commit()

    '''works'''
    def delete_user(self, discord_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM users WHERE discord_id = ?', (discord_id,))
        self.conn.commit()
    
    '''oftenly works'''
    def add_streamer_to_user(self, discord_id, streamer):
        try:
            cursor = self.conn.cursor()

            # Retrieve the current value of the "streamer" column for the specified Discord ID
            cursor.execute('SELECT streamer FROM users WHERE discord_id = ?', (discord_id,))
            current_value = cursor.fetchone()

            # Check if the Discord ID exists in the table
            if current_value is None:
                # Discord ID does not exist, insert a new row with the specified Discord ID and streamer
                cursor.execute('INSERT INTO users (discord_id, streamer) VALUES (?, ?)', (discord_id, streamer))
            else:
                # Discord ID exists, concatenate the new streamer with the current value using a comma as a separator
                current_value = current_value[0]
                if current_value is not None:
                    streamers = current_value.split(',')
                else:
                    streamers = []
                if streamer not in streamers:
                    # Streamer is not in the current value, concatenate the new streamer with the current value using a comma as a separator
                    if current_value is not None:
                        new_value = current_value + ',' + streamer
                    else:
                        new_value = streamer
                    cursor.execute('UPDATE users SET streamer = ? WHERE discord_id = ?', (new_value, discord_id))

            self.conn.commit()
            cursor.close()
        except Exception as e:
            print(f"An error occurred: {e}")

    '''works'''
    def remove_streamer_from_user(self, discord_id, streamer):
        cursor = self.conn.cursor()
        cursor.execute('SELECT streamer FROM users WHERE discord_id = ?', (discord_id,))
        current_value = cursor.fetchone()

        # Check if the Discord ID exists in the table
        if current_value is not None:
            # Discord ID exists, check if the streamer is in the current value
            current_value = current_value[0]
            streamers = current_value.split(',')
            if streamer in streamers:
                # Streamer is in the current value, remove it from the list
                streamers.remove(streamer)
                new_value = ','.join(streamers)
                cursor.execute('UPDATE users SET streamer = ? WHERE discord_id = ?', (new_value, discord_id))
        
        self.conn.commit()

    '''works'''
    def get_streamers_for_user(self, discord_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT streamer FROM users WHERE discord_id = ?", (discord_id,))
        streamers = [row[0] for row in cursor.fetchall()]
        return streamers

    '''works'''
    def get_all_streamers(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT streamer FROM users")
        streamers = [row[0] for row in cursor.fetchall()]
        return streamers

    '''works'''
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

    '''works'''
    def get_all_user_ids(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT discord_id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
        return user_ids

    '''works'''
    def get_streamers_for_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT streamer FROM users WHERE discord_id = ?", (user_id,))
        streamers = [row[0] for row in cursor.fetchall()]
        return streamers

    '''works'''
    def set_version(self, new_version):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE Config SET version = ?', (new_version,))
        self.conn.commit()

    '''works'''
    def get_version(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT version FROM Config')
        version = cursor.fetchone()
        if version is not None:
            return version[0]
        else:
            return "No version found"

    '''works'''
    def set_prefix(self, prefix):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE Config SET prefix = ?', (prefix,))
        self.conn.commit()

    '''works'''
    def get_prefix(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT prefix FROM Config')
        prefix = cursor.fetchone()
        if prefix is not None:
            return prefix[0]
        else:
            return "No prefix found"

    '''works'''
    def get_time(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT time FROM Config')
        prefix = cursor.fetchone()
        if prefix is not None:
            return prefix[0]
        else:
            return "No time found"

    '''works'''
    def save_time(self, time):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE Config SET time = ?', (time,))
        self.conn.commit()
        
    '''works'''
    def get_bot_owner_id(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT bot_owner_id FROM Config')
        owner_id = cursor.fetchone()
        if owner_id is not None:
            return owner_id[0]
        else:
            return "No owner ID found"

    '''works'''
    def save_bot_owner_id(self, owner_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE Config SET bot_owner_id = ?', (owner_id,))
        self.conn.commit()
    
    '''works'''
    def create_new_guild_template(self, guild_id, guild_name):
        try:
            cursor = self.conn.cursor()

            # Check if a guild with the same ID already exists
            cursor.execute("SELECT guild_id FROM guilds WHERE guild_id = ?", (guild_id,))
            existing_guild = cursor.fetchone()

            if existing_guild is None:
                # Guild with the same ID does not exist, insert a new row
                cursor.execute("INSERT INTO guilds (guild_id, name, prefix, role_to_add) VALUES (?, ?, ?, ?)",
                            (guild_id, guild_name, ",", None))
                self.conn.commit()
                print("New guild created successfully.")
            else:
                print("Guild with the same ID already exists.")

            cursor.close()
        except Exception as e:
            print(f"An error occurred: {e}")

    '''works'''
    def is_guild_in_config(self, guild_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM guilds WHERE guild_id = ?", (guild_id,))
        count = cursor.fetchone()[0]
        return count > 0

    '''works'''
    def get_guild_prefix(self, guild_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT prefix FROM guilds WHERE guild_id = ?", (guild_id,))
        row = cursor.fetchone()
        if row:
            return row[0]
        return ""

    '''works'''
    def remove_guild(self, guild_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM guilds WHERE guild_id = ?", (guild_id,))
        self.conn.commit()

    '''works'''
    def change_role_to_add(self, guild_id, new_role_id):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE guilds SET role_to_add = ? WHERE guild_id = ?", (str(new_role_id), guild_id))
        self.conn.commit()

    '''works'''
    def get_role_to_add(self, guild_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT role_to_add FROM guilds WHERE guild_id = ?", (guild_id,))
        row = cursor.fetchone()
        if row:
            return row[0]
        return ""

    '''works'''
    def change_guild_prefix(self, guild_id, new_prefix):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE guilds SET prefix = ? WHERE guild_id = ?", (new_prefix, guild_id))
        self.conn.commit()

    '''idk how to test'''
    def save_to_temp_json(self, data):
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "temp_restart_data.json")

        with open(file_path, "w") as file:
            json.dump(data, file)

    '''need the upper one to test'''
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
