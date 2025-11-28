# F1Replay
Vizualizes F1 race results by fetching API from OpenF1 website. Uses multiprocessing for finishing results effectively

## Requirements 
* **Python 3.9**
* Libraries: [here](##Used-Libraries)
* Internet connection

## Used Libraries
* OpenF1 API - external Data fetch (REST API)
* Requests - python library
* Multiprocessing - python library

## Execution
* Install libraries:
    ```bash
    pip install requests
    ```
    
* Ensure [config.json](https://github.com/Niko2357/F1Replay/blob/main/F1Replay/config.json) in same directory as [main.py](https://github.com/Niko2357/F1Replay/blob/main/F1Replay/main.py)
  
* Execute:
     ```bash
    python F1Replay.py
    ```

## Program Configuration
This project is using [config.json](https://github.com/Niko2357/F1Replay/blob/main/F1Replay/config.json) file.
- session_key
  -  four place number
  -  unique race identifier
  -  choice of different race sessions (need to exist)

- api_driver and api_session_resultes
  - API URL endpoint

## Error Handling
The application includes basic error handling for common failure points.
* Configuration Error
  * *ValueError*: Occurs if an invalid input is passed to open_config. Resolution: Check the calling code.
* API Failure
  * *requests.exceptions.RequestException*: Connection or HTTP error (e.g., 404, 500) during data fetching. Resolution: Verify internet connection, session_key validity, and OpenF1 API status.
* No Data Returned
  * *return "It doesnt work"*: APIs return empty lists/dictionaries. Resolution: Check the validity of the session_key.

## Version and Issues
* Version: 1.0.0

## Licencing and Dependencies
MIT License: [Licence](https://github.com/Niko2357/F1Replay/blob/main/LICENSE)

OpenF1: The application's functionality is entirely dependent on the availability and data format provided by the OpenF1 API. The project author is not liable for service interruptions or changes in the OpenF1 data structure.


## Author
Name: Nikola 
Surname: Poláchová
Subject: Programming 
Year: 2025
