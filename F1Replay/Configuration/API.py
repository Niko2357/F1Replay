import requests
from Configuration.ConfigManager import ConfigManager


class API:
    @staticmethod
    def race_config():
        config = ConfigManager.open_config("config")
        return config["race"]

    @staticmethod
    def fetch_driver(session: str):
        """
        Fetches information by API, gets driver name and team.
        :param session: Identification key of race.
        :return: Object driver information or exception.
        """
        config = API.race_config()
        api = config["api_drivers"]
        try:
            response = requests.get(api, params={"session_key": session})
            response.raise_for_status()
            drivers = response.json()
            details = {}
            for driver in drivers:
                details[driver["driver_number"]] = {
                    "name": f"{driver.get('first_name', '')} {driver.get('last_name', '')}",
                    "team": driver.get("team_name", "N/A")
                }
            return details
        except Exception as e:
            return f"Details couldn't be loaded. {e}"

    @staticmethod
    def fetch_session_results(session: str):
        """
        Gets information about finished race from API.
        :param session: Identification key of race.
        :return: whole API information about race results.
        """
        config = API.race_config()
        api = config["api_session_results"]
        try:
            response = requests.get(api, params={"session_key": session})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"API couldn't be loaded: {e}"
>>>>>>> master
