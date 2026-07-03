# -*- coding: utf-8 -*-
'''
Required

Sales
SALES THERMAX
Service Bill

'''

import os
import re
import requests
import xml.etree.ElementTree as ET
import csv
from concurrent.futures import ProcessPoolExecutor
from xml_requests import ledger_xml, voucher_xml_service


# from datetime import datetime

# TALLY_URL = "http://127.0.0.1:9000"
TALLY_URL = "http://192.168.1.131:9000"

# -----------------------
# CLEAN XML FUNCTION
# -----------------------
def clean_xml(x):

    x = re.sub(r"&#\d+;", "", x)
    x = re.sub(r"<(/?)[A-Za-z0-9]+:", r"<\1", x)
    x = re.sub(r"[^\x09\x0A\x0D\x20-\x7F]+", "", x)

    return x


# -----------------------
# LEDGER FUNCTION
# -----------------------
def fetch_ledger(tally_url, ledger_xml):

    r = requests.post(tally_url, data=ledger_xml)
    root = ET.fromstring(clean_xml(r.text))

    ledger_parent = {}

    for l in root.findall(".//LEDGER"):
        name = l.get("NAME")
        parent = l.findtext("PARENT")

        if name:
            ledger_parent[name.upper()] = parent

    return ledger_parent


# -----------------------
# VOUCHER FUNCTION
# -----------------------
def fetch_voucher_data(tally_url, voucher_xml, ledger_parent):

    r = requests.post(tally_url, data=voucher_xml)
    root = ET.fromstring(clean_xml(r.text))

    rows = []

    for v in root.findall(".//VOUCHER"):

        date = v.findtext("DATE")
        number = v.findtext("VOUCHERNUMBER")
        ref = v.findtext("REFERENCE", "-/-/-/-")
        category = ref.split("/")[2]
        cat_type = ref.split("/")[3]
        if len(cat_type) > 4:
            cat_type = ""
        vtype = v.findtext("VOUCHERTYPENAME")
        state = v.findtext("STATENAME")

        if date:
            date = f"{date[6:8]}-{date[4:6]}-{date[0:4]}"
        else:
            date = ""

        # voucher_total = abs(float(v.findtext("AMOUNT", "0")))
        
        voucher_total = re.sub(r'[^0-9.]', '', v.findtext("AMOUNT", "0"))

        for e in v.findall(".//ALLLEDGERENTRIES.LIST"):

            if e.findtext("ISPARTYLEDGER") != "Yes":
                continue

            ledger = e.findtext("LEDGERNAME")
            parent = ledger_parent.get(ledger.upper(), "")  # type: ignore

            rows.append(
                [
                    date,
                    number,
                    ref,
                    category,
                    cat_type,
                    vtype,
                    ledger,
                    parent,
                    voucher_total,
                    state,
                ]
            )

    return rows


# -----------------------
# MAIN
# -----------------------


if __name__ == "__main__":

    # Step 1: Load ledger
    ledger_parent = fetch_ledger(TALLY_URL, ledger_xml)
    print("Ledgers Loaded:", len(ledger_parent))

    # Step 2: Parallel voucher fetch
    urls = [TALLY_URL]  # parallel calls

    final_rows = []
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = executor.map(fetch_voucher_data, urls, [voucher_xml_service], [ledger_parent])

    # Step 3: Combine all rows
    for res in results:
        final_rows.extend(res)

    print("Total Rows:", len(final_rows))


    # -----------------------
    # CSV EXPORT
    # -----------------------
    header = [
        "Date",
        "Voucher_Number",
        "Reference",
        "Category",
        "Voucher_Type",
        "Category_Type",
        "Ledger_Name",
        "Ledger_Parent",
        "Amount",
        "State_Name",
    ]

    with open("service_export.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(final_rows)

    print("CSV Created:", len(final_rows), "rows")
