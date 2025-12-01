from multiprocessing import Process, Manager
from Configuration.API import API


class Analysis:
    @staticmethod
    def process_final_result(driver_num, timing_data, driver_details, shared_output_list):
        """
        Sorts out information about race into one line.
        :param driver_num: number of driver, racing number
        :param timing_data: contains all final results
        :param driver_details: dictionary containing driver information
        :param shared_output_list: shared list
        :return:
        """
        cur_data = timing_data.get(driver_num, None)
        if cur_data:
            position = cur_data.get("position", 99)
            calculated_gap = cur_data.get("gap_to_leader")
            laps = cur_data.get("number_of_laps", "-")
            gap_to = ""
            status = ""
            if cur_data.get("dsq") is True:
                status = "DSQ"
            elif cur_data.get("dnf") is True:
                status = "DNF"
            elif cur_data.get("dns") is True:
                status = "DNS"
            else:
                status = "Finished"

            if position > 1 and calculated_gap is not None:
                gap_to = f"{calculated_gap:+.3f}" if calculated_gap > 0 else "---"
            elif position == 1:
                gap_to = "---"

            details = driver_details.get(driver_num, {"name": f"Driver {driver_num}", "team": "N/A"})
            output_line = (
                f"{position:<10} | {details['name']:<20} | {details['team']:<15} | "
                f"{gap_to:<18} | {laps:<5} |  {status}"
            )
            shared_output_list.append((position, output_line))

    @staticmethod
    def parallel():
        """
        Makes table with results of race, standings of drivers.
        :return: error messages
        """
        driver_details = API.fetch_driver()
        if not driver_details:
            return "It doesnt work"

        final_results = API.fetch_session_results()
        if not final_results:
            return "It doesnt work"

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

            print("\nRace Results")
            print("-" * 100)
            output_data = list(shared_output_list)
            output_data.sort(key=lambda x: x[0])
            print(
                f"{'Position':<10} | {'Driver':<20} | {'Team':<15} | {'Gap to Leader (s)':<18} | {'Laps':<5} | {'Case'}")
            print("-" * 100)
            for position, line in output_data:
                print(line)

            print("-" * 100)
