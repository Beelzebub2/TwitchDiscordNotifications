import json
import os
import tempfile

class ConfigHandler:
    def __init__(self, config_file):
        self.config_file = config_file
        self.data = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_config(self):
        with open(self.config_file, "w") as file:
            json.dump(self.data, file, indent=4)

    def add_user(self, user_data):
        self.data = self.load_config()
        user_key = f"User{len(self.data['User-list']) + 1}"
        self.data["User-list"][user_key] = [user_data]
        self.save_config()
        return user_key

    def add_streamer_to_user(self, user_id, streamer):
        self.data = self.load_config()
        for user_data_list in self.data["User-list"].values():
            for user_data in user_data_list:
                if user_data["discord_id"] == user_id:
                    user_data["streamer_list"].append(streamer)
                    self.save_config()
                    return True
        return False

    def remove_streamer_from_user(self, user_id, streamer):
        self.data = self.load_config()
        for user_data_list in self.data["User-list"].values():
            for user_data in user_data_list:
                if user_data["discord_id"] == user_id:
                    if streamer in user_data["streamer_list"]:
                        user_data["streamer_list"].remove(streamer)
                        self.save_config()
                        return True
        return False

    def get_all_streamers(self):
        self.data = self.load_config()
        streamers = set()
        for user_data in self.data["User-list"].values():
            streamers.update(user_data[0]["streamer_list"])
        return list(streamers)

    def get_user_ids_with_streamers(self):
        self.data = self.load_config()
        user_ids_with_streamers = {}
        for user, user_data_list in self.data["User-list"].items():
            for user_data in user_data_list:
                user_id = user_data["discord_id"]
                streamer_list = user_data["streamer_list"]
                if user_id not in user_ids_with_streamers:
                    user_ids_with_streamers[user_id] = streamer_list
                else:
                    user_ids_with_streamers[user_id].extend(streamer_list)
        return user_ids_with_streamers

    def get_all_user_ids(self):
        self.data = self.load_config()
        user_ids = []
        for user_data_list in self.data["User-list"].values():
            for user_data in user_data_list:
                user_id = user_data["discord_id"]
                if user_id not in user_ids:
                    user_ids.append(user_id)
        return user_ids

    def get_streamers_for_user(self, user_id):
        self.data = self.load_config()
        for user_data_list in self.data["User-list"].values():
            for user_data in user_data_list:
                if user_data["discord_id"] == user_id:
                    return user_data["streamer_list"]
        return []

    def get_version(self):
        self.data = self.load_config()
        return self.data.get("Config", {}).get("version")

    def get_prefix(self):
        self.data = self.load_config()
        return self.data.get("Config", {}).get("prefix")
    
    def get_time(self):
        self.data = self.load_config()
        return self.data.get("Config", {}).get("time")
    
    def save_time(self, start_time):
        self.data = self.load_config()
        self.data["Config"]["time"] = start_time
        self.save_config()
        

    def create_new_guild_template(self, guild_id, guild_name):
        self.data = self.load_config()
        self.data["Guilds"][str(guild_id)] = {
            "name": guild_name,
            "prefix": ",",
            "role_to_add": None,
        }
        self.save_config()

    def is_guild_in_config(self, guild_id):
        self.data = self.load_config()
        return str(guild_id) in self.data.get("Guilds", {})

    def get_guild_prefix(self, guild_id):
        self.data = self.load_config()
        guild_info = self.data["Guilds"].get(str(guild_id), {})
        return guild_info.get("prefix", "")
    
    def remove_guild(self, guild_id):
        self.data = self.load_config()
        if str(guild_id) in self.data["Guilds"]:
            del self.data["Guilds"][str(guild_id)]
            self.save_config()

    def change_role_to_add(self, guild_id, new_role_id):
        self.data = self.load_config()
        guild_info = self.data["Guilds"].get(str(guild_id), {})
        guild_info["role_to_add"] = str(new_role_id)
        self.save_config()

    def get_role_to_add(self, guild_id):
        self.data = self.load_config()
        guild_info = self.data["Guilds"].get(str(guild_id), {})
        return guild_info.get("role_to_add", "")

    def change_guild_prefix(self, guild_id, new_prefix):
        self.data = self.load_config()
        guild_info = self.data["Guilds"].get(str(guild_id), {})
        guild_info["prefix"] = new_prefix
        self.save_config()

    def delete_user(self, user_id):
        self.data = self.load_config()
        user_key_to_delete = None

        for user_key, user_data_list in self.data["User-list"].items():
            for user_data in user_data_list:
                if user_data["discord_id"] == user_id:
                    user_key_to_delete = user_key
                    break

        if user_key_to_delete is not None:
            del self.data["User-list"][user_key_to_delete]
            user_keys = list(self.data["User-list"].keys())
            for i, user_key in enumerate(user_keys):
                new_user_key = f"User{i+1}"
                self.data["User-list"][new_user_key] = self.data["User-list"].pop(
                    user_key
                )

            self.save_config()
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
        bot_owner_id = self.data.get("Config", {}).get("bot_owner_id", "")
        return bot_owner_id
    
    def save_bot_owner_id(self, owner_id):
        self.data = self.load_config()
        config_data = self.data.get("Config", {})
        config_data["bot_owner_id"] = owner_id
        self.data["Config"] = config_data
        self.save_config()