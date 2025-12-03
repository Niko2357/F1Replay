from multiprocessing import Process, Manager
from Configuration.API import API


class Analysis:
    @staticmethod
    def process_final_result(driver_num, timing_data, driver_details, shared_output_list):
        """
        Sorts out information about race into one line.
        :param driver_num: Number of driver, racing number.
        :param timing_data: Contains all final results.
        :param driver_details: Dictionary containing driver information.
        :param shared_output_list: Shared list.
        """
        cur_data = timing_data.get(driver_num, None)
        if cur_data:
            r_position = cur_data.get("position")
            try:
                position = int(r_position)
            except (ValueError, TypeError):
                position = 99
            calculated_gap = cur_data.get("gap_to_leader")
            laps = cur_data.get("number_of_laps", "-")
            gap_to = "---"
            if cur_data.get("dsq") is True:
                status = "DSQ"
            elif cur_data.get("dnf") is True:
                status = "DNF"
            elif cur_data.get("dns") is True:
                status = "DNS"
            else:
                status = "Finished"

            if calculated_gap is not None:
                try:
                    gap_float = float(calculated_gap)
                    if 99 > position > 1 and gap_float > 0:
                        gap_to = f"{gap_float:+.3f}"
                    else:
                        gap_to = "---"
                except (ValueError, TypeError):
                    gap_to = "---"
            elif position == 1:
                gap_to = "---"

            details = driver_details.get(driver_num, {"name": "Unknown", "team": "N/A"})
            driver_name = details.get("name") or "Unknown"
            driver_team = details.get("team") or "N/A"
            output = {
                "Position": position,
                "Driver": driver_name,
                "Team": driver_team,
                "Gap_to_Leader": gap_to,
                "Laps": laps,
                "Status": status
            }
            shared_output_list.append((position, output))

    @staticmethod
    def parallel(session: str):
        """
        Makes table with results of race, standings of drivers.
        :return: A list of dictionaries with sorted results or error messages.
        """
        driver_details = API.fetch_driver(session)
        if not driver_details:
            return "It doesn't work"

        final_results = API.fetch_session_results(session)
        if not final_results:
            return "It doesn't work"

        results_map = {}
        for r in final_results:
            if isinstance(r, dict):
                driver_num = r.get("driver_number")
                if driver_num is not None:
                    results_map[driver_num] = r

        with Manager() as manager:
            shared_timing_data = manager.dict()
            shared_output_list = manager.list()
            processes = []

            for driver_num, result_data in results_map.items():
                shared_timing_data[driver_num] = result_data.copy()
                shared_timing_data[driver_num]["gap_to_leader"] = result_data.get("gap_to_leader")
            for driver_num in results_map.keys():
                if driver_num in driver_details:
                    p = Process(target=Analysis.process_final_result, args=(
                        driver_num,
                        shared_timing_data,
                        driver_details,
                        shared_output_list
                    ))
                    processes.append(p)
                    p.start()
            for p in processes:
                p.join()

            output_data = list(shared_output_list)
            output_data.sort(key=lambda x: x[0])
            final_standings = [data for position, data in output_data]
            return final_standings
