import json


class ConfigManager:
    @staticmethod
    def open_config(config_or_key: str):
        """
        Opens and reads content of configuration file.
        Returns either whole configuration file with "config" input or session key in case
        of "key" input.
        :param config_or_key: choice between whole configuration, string "config" or "key"
        :return: string value of whole file or session key or exception
        """
        with open("Configuration//config.json", "r") as f:
            config = json.load(f)
        if config_or_key == "config":
            return config
        elif config_or_key == "key":
            key = config["race"]["session_key"]
            return key
        else:
            raise ValueError("Wrong input")
