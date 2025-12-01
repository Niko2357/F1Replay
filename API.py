


class API:
    def __init__(self, config):
        self.config = config

    @staticmethod
    def fetch_driver():
        """
        Fetches information by API, gets driver name and team.
        :return: object driver information or exception
        """
        config = open_config("config")
        api = config["race"]["api_drivers"]
        session = config["race"]["session_key"]
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
            return f"Details couldnt be loaded. {e}"

    @staticmethod
    def fetch_session_results():
        """
        Gets information about finished race from API.
        :return: whole API information about race results
        """
        config = open_config("config")
        api = config["race"]["api_session_results"]
        session = open_config("key")
        try:
            response = requests.get(api, params={"session_key": session})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API couldnt be loaded: {e}")
            return []