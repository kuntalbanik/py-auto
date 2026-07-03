# -*- coding: utf-8 -*-
"""
Required

Sales
SALES THERMAX
Service Bill

"""

import os
import re
import sys
import requests
import xml.etree.ElementTree as ET
import csv
from concurrent.futures import ProcessPoolExecutor
from xml_requests_pre_odi import (
    ledger_xml_re,
    voucher_xml_sales_re,
    voucher_xml_tmx_re,
    voucher_xml_service_re,
)


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

    try:
        r = requests.post(tally_url, data=ledger_xml)
        root = ET.fromstring(clean_xml(r.text))
        ledger_parent = {}

        for l in root.findall(".//LEDGER"):
            name = l.get("NAME")
            parent = l.findtext("PARENT")

            if name:
                ledger_parent[name.upper()] = parent
        return ledger_parent
    except Exception as e:
        print("Network Issue")


def get_basic_value(voucher):
    inventory = voucher.findall(".//ALLINVENTORYENTRIES.LIST")

    if inventory:
        return abs(sum(float(i.findtext("AMOUNT", "0")) for i in inventory))

    # fallback (ledger-based)
    total = 0.0
    for l in voucher.findall(".//ALLLEDGERENTRIES.LIST"):
        if l.findtext("ISPARTYLEDGER") == "Yes":
            continue
        total += float(l.findtext("AMOUNT", "0"))

    return abs(total)


# -----------------------
# VOUCHER FUNCTION
# -----------------------
def fetch_voucher_data(tally_url, voucher_xml, ledger_parent):
    try:
        r = requests.post(tally_url, data=voucher_xml)
        root = ET.fromstring(clean_xml(r.text))

        rows = []

        for v in root.findall(".//VOUCHER"):

            date = v.findtext("DATE")
            number = v.findtext("VOUCHERNUMBER")
            ref = v.findtext("REFERENCE", "-/-/-/-/-/-")
            category = ref.split("/")[2]

            # Category Type
            if len(ref.split("/")) < 5:
                cat_type = "Sales"
            elif len(ref.split("/")) > 4:
                cat_type = category
                category = ref.split("/")[3]
            else:
                cat_type = ""
            # End Category Type

            vtype = v.findtext("VOUCHERTYPENAME")
            state = v.findtext("STATENAME")

            if date:
                date = f"{date[6:8]}-{date[4:6]}-{date[0:4]}"
            else:
                date = ""

            # voucher_total = abs(float(v.findtext("AMOUNT", "0")))
            voucher_total = get_basic_value(v)

            # voucher_total = re.sub(r"[^0-9.]", "", v.findtext("AMOUNT", "0"))

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
    except Exception as e:
        print("Network Issue")
        sys.exit(1)


# -----------------------
# MAIN
# -----------------------


if __name__ == "__main__":

    # Step 1: Load ledger
    ledger_parent = fetch_ledger(TALLY_URL, ledger_xml=ledger_xml_re())
    try:
        print("Ledgers Loaded:", len(ledger_parent))  # type: ignore
    except Exception as e:
        print("Ledgers Loaded : 0")

    input_date_from = input("Ex. 01042024 - From Date: ")
    input_date_to = input("Ex. 30042024 - To Date: ")

    FROM_DATE = f"{input_date_from[4:8]}{input_date_from[2:4]}{input_date_from[0:2]}"
    TO_DATE = f"{input_date_to[4:8]}{input_date_to[2:4]}{input_date_to[0:2]}"
    if len(FROM_DATE) > 8 or len(TO_DATE) > 8:
        print("Wrong date format")
    # FROM_DATE = "20240401"
    # TO_DATE = "20240630"

    # Step 2: Parallel voucher fetch
    urls = [TALLY_URL]  # parallel calls

    final_rows = []
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = executor.map(
            fetch_voucher_data,
            urls,
            [voucher_xml_sales_re(FROM_DATE, TO_DATE)],
            [ledger_parent],
        )

    # Step 3: Combine all rows
    for res in results:
        final_rows.extend(res)  # type: ignore

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        results2 = executor.map(
            fetch_voucher_data,
            urls,
            [voucher_xml_tmx_re(FROM_DATE, TO_DATE)],
            [ledger_parent],
        )

    # Step 3: Combine all rows
    for res in results2:
        final_rows.extend(res)  # type: ignore

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        results3 = executor.map(
            fetch_voucher_data,
            urls,
            [voucher_xml_service_re(FROM_DATE, TO_DATE)],
            [ledger_parent],
        )

    # Step 3: Combine all rows
    for res in results3:
        final_rows.extend(res)  # type: ignore

    print("Total Rows:", len(final_rows))

    # -----------------------
    # CSV EXPORT
    # -----------------------
    header = [
        "Date",
        "Voucher_Number",
        "Reference",
        "Category",
        "Category_Type",
        "Voucher_Type",
        "Ledger_Name",
        "Ledger_Parent",
        "Amount",
        "State_Name",
    ]

    with open("sales_service_export_pre_odi.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(final_rows)

    print("CSV Created:", len(final_rows), "rows")
