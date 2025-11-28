import requests
import json
from multiprocessing import Process, Manager


def open_config(config_or_key: str):
    """
    Opens and reads content of configuration file.
    Returns either whole configuration file with "config" input or session key in case
    of "key" input
    :param config_or_key: choice between whole configuration, string "config" or "key"
    :return: string value of whole file or session key or exception
    """
    with open("config.json", "r") as f:
        config = json.load(f)
    if config_or_key == "config":
        return config
    elif config_or_key == "key":
        key = config["race"]["session_key"]
        return key
    else:
        raise ValueError("Wrong input")


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
