#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#


from util import expand_ip_range
from scanner import scan_network, save_results_to_file

if __name__ == "__main__":
    ip_range = "192.168.1.1-254"
    max_threads = 125

    network_iplist = expand_ip_range(ip_range)
    network_result = scan_network(network_iplist, max_threads)
    save_results_to_file(network_result)
