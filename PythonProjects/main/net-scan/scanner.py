#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from util import ping_host, expand_ip_range


def scan_network(ip_list: list, max_threads: int) -> dict:
    results = {}

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_ip = {executor.submit(ping_host, ip): ip for ip in ip_list}

        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                status = "up" if future.result() else "down"
                if str(status) == "up":
                    results[ip] = status
            except Exception:
                status = "Error"

    return results


# save to json file
def save_results_to_file(results: dict, filename: str = "scan_result.json"):
    with open(filename, "w") as f:
        json.dump(results, f, indent=4)
