import json


class JsonConfigHandler:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            default_config = {
                "config": {
                    "version": "v2.6",
                    "debug": False,
                    "autoupdates": True
                }
            }
            self.save_config(default_config)
            return default_config

    def save_config(self, config):
        with open(self.config_file, 'w') as file:
            json.dump(config, file, indent=4)

    def get_version(self):
        return self.config["config"]["version"]

    def set_version(self, version):
        self.config["config"]["version"] = version
        self.save_config(self.config)

    def get_debug(self):
        return self.config["config"]["debug"]

    def set_debug(self, debug):
        self.config["config"]["debug"] = debug
        self.save_config(self.config)

    def get_autoupdates(self):
        return self.config["config"]["autoupdates"]

    def set_autoupdates(self, autoupdates):
        self.config["config"]["autoupdates"] = autoupdates
        self.save_config(self.config)

    def get_prefix(self):
        return self.config["config"]["default_prefix"]

    def set_prefix(self, prefix):
        self.config["config"]["default_prefix"] = prefix
        self.save_config(self.config)

    def get_max_lines(self):
        return int(self.config["config"]["max_lines"])

    def set_max_lines(self, max_lines):
        self.config["config"]["max_lines"] = int(max_lines)
        self.save_config(self.config)

    def get_pid(self):
        self.config = self.load_config()
        return self.config["config"]["bot_PID"]

    def set_pid(self, pid):
        self.config["config"]["bot_PID"] = pid
        self.save_config(self.config)

    def get_time(self):
        self.config = self.load_config()
        return self.config["config"]["start_time"]

    def set_time(self, start_time):
        self.config["config"]["start_time"] = start_time
        self.save_config(self.config)
