import os
import re
import sys
import requests
import xml.etree.ElementTree as ET
import csv
from xml_requests_pioneer import (
    ledger_xml_re,
    voucher_xml_sales_re,
    voucher_xml_tmx_re,
    voucher_xml_service_re,
)

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
        print(f"Network Issue Ledger: {e}")
        sys.exit(1)

def get_basic_value(voucher):
    inventory = voucher.findall(".//ALLINVENTORYENTRIES.LIST")
    if inventory:
        return abs(sum(float(i.findtext("AMOUNT", "0")) for i in inventory))

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
            ref_parts = ref.split("/")
            
            # Safe Parsing of Category
            if len(ref_parts) > 4:
                category = ref_parts[3]
            elif len(ref_parts) > 3:
                category = ref_parts[2]
            elif len(ref_parts) > 2:
                category = ref_parts[1]
            else:
                category = ref_parts[-1] if ref_parts else "-"

            # Safe Parsing of Category Type
            if len(ref_parts) < 5:
                cat_type = "Sales"
            else:
                cat_type = ref_parts[2]
                category = ref_parts[3]

            vtype = v.findtext("VOUCHERTYPENAME")
            state = v.findtext("STATENAME")

            if date and len(date) == 8:
                date = f"{date[6:8]}-{date[4:6]}-{date[0:4]}"
            else:
                date = ""

            voucher_total = get_basic_value(v)

            for e in v.findall(".//ALLLEDGERENTRIES.LIST"):
                if e.findtext("ISPARTYLEDGER") != "Yes":
                    continue

                ledger = e.findtext("LEDGERNAME")
                parent = ledger_parent.get(ledger.upper(), "") if ledger else ""

                rows.append([
                    date, number, ref, category, cat_type,
                    vtype, ledger, parent, voucher_total, state
                ])
        return rows
    except Exception as e:
        print(f"Error fetching vouchers: {e}")
        return []

# -----------------------
# MAIN
# -----------------------
if __name__ == "__main__":
    # Step 1: Load ledger
    ledger_parent = fetch_ledger(TALLY_URL, ledger_xml=ledger_xml_re())
    print("Ledgers Loaded:", len(ledger_parent))

    # Clean Date Formats
    input_date_from = input("Ex. 01042024 - From Date: ").strip()
    input_date_to = input("Ex. 30042024 - To Date: ").strip()

    if len(input_date_from) != 8 or len(input_date_to) != 8:
        print("Error: Date must be exactly 8 digits (DDMMYYYY).")
        sys.exit(1)

    FROM_DATE = f"{input_date_from[4:8]}{input_date_from[2:4]}{input_date_from[0:2]}"
    TO_DATE = f"{input_date_to[4:8]}{input_date_to[2:4]}{input_date_to[0:2]}"

    final_rows = []

    # Step 2: Sequential fetch requests (Fixes Multi-Processing serialization errors)
    print("Fetching Sales Vouchers...")
    sales_xml = voucher_xml_sales_re(FROM_DATE, TO_DATE)
    final_rows.extend(fetch_voucher_data(TALLY_URL, sales_xml, ledger_parent))

    print("Fetching TMX Vouchers...")
    tmx_xml = voucher_xml_tmx_re(FROM_DATE, TO_DATE)
    final_rows.extend(fetch_voucher_data(TALLY_URL, tmx_xml, ledger_parent))

    print("Fetching Service Vouchers...")
    service_xml = voucher_xml_service_re(FROM_DATE, TO_DATE)
    final_rows.extend(fetch_voucher_data(TALLY_URL, service_xml, ledger_parent))

    print("Total Rows Compiled:", len(final_rows))

    # -----------------------
    # CSV EXPORT
    # -----------------------
    header = [
        "Date", "Voucher_Number", "Reference", "Category", 
        "Category_Type", "Voucher_Type", "Ledger_Name", 
        "Ledger_Parent", "Amount", "State_Name"
    ]

    output_file = "sales_service_export_pioneer.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(final_rows)

    print(f"CSV Successfully Created: '{output_file}' with {len(final_rows)} rows.")
