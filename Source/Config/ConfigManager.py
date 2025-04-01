import yaml
import os

class ConfigManager:
    _Instance = None  # 单例实例

    def __new__(cls, *args, **kwargs):
        if not cls._Instance:
            cls._Instance = super(ConfigManager, cls).__new__(cls)
        return cls._Instance

    def __init__(self):
        self.ConfigData = {}
        self.ConfigPath = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")), "Config/Settings.yaml")
        self.LoadConfig()

    def LoadConfig(self):
        if not os.path.exists(self.ConfigPath):
            print(f"[警告] 配置文件不存在：{self.ConfigPath}")
            return
        with open(self.ConfigPath, "r", encoding="utf-8") as f:
            self.ConfigData = yaml.safe_load(f)

    def GetString(self, Key, Default=""):
        return str(self.ConfigData.get(Key, Default))

    def GetBool(self, Key, Default=False):
        return bool(self.ConfigData.get(Key, Default))

    def GetInt(self, Key, Default=0):
        return int(self.ConfigData.get(Key, Default))

    def GetFloat(self, Key, Default=0.0):
        return float(self.ConfigData.get(Key, Default))


if __name__ == "__main__":
    Config = ConfigManager()
    print("EnableTTS:", Config.GetBool("EnableTTS", False))
    print("EnableParse:", Config.GetBool("EnableParse", False))
    print("ModelUrl:", Config.GetString("ModelUrl"))
