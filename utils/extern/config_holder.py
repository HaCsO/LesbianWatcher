import tomli
import tomli_w
import datetime

class ConfigHolder():
    def __init__(self, config_path):
        self._config: dict = {}
        self.path: str = config_path
        self.lastupdate: datetime = None
        self.validate_config()
        self.update_from_file()
    
    def validate_config(self):
        try:
            open(self.path, "rb")
        except:
            self.create_config()
    
    def sync_config(self):
        self._config["bot"] = self.bot
        self._config["users"] = self.users
        self._config["roles"] = self.roles
        self._config["channels"] = self.channels
    
    def update_from_file(self):
        with open(self.path, "rb") as f:
            try:
                self._config: dict = tomli.load(f)
                self.bot: dict = self._config["bot"]
                self.users: dict = self._config["users"]
                self.channels: dict = self._config["channels"]
                self.roles: dict = self._config["roles"]
            except tomli.TOMLDecodeError as e:
                print(f"Can't decode {f.name}: {e}")

        print("Config was updated from a file.")
        self.lastupdate = datetime.datetime.now()
    
    def upload_to_file(self):
        with open(self.path, "wb") as f:
            self.sync_config()
            tomli_w.dump(self._config, f)
            
        print("Config file was updated.")
        self.lastupdate = datetime.datetime.now()
    
    def create_config(self):
        bot: dict = {
            "token": "",
            "guild_id": 0,
            "debug_guilds": []
        }
        users: dict = {
            "owner": 0,
            "headmod": 0,
            "mods": []
        }
        roles: dict = {
            "mime": 0,
            "clown": 0
        }
        channels: dict = {
            "log": 0,
            "talk": 0,
            "punish":0
        }
        self._config = {"bot": bot, "users": users, "roles": roles, "channels": channels}
        self.upload_to_file()
