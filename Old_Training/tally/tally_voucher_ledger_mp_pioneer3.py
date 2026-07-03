import os
import re
import sys
import requests
import xml.etree.ElementTree as ET
import csv

TALLY_URL = "http://192.168.1.131:9000"

# -----------------------
# TALLY XML TEMPLATES
# -----------------------
def ledger_xml_re():
    return """<ENVELOPE>
    <HEADER><VERSION>1</VERSION><TALLYREQUEST>Export</TALLYREQUEST><TYPE>Collection</TYPE><ID>LedgerCollection</ID></HEADER>
    <BODY><DESC><STATICVARIABLES><SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT></STATICVARIABLES>
    <TDL><TDLMESSAGE><COLLECTION NAME="LedgerCollection"><TYPE>Ledger</TYPE><FETCH>NAME,PARENT</FETCH></COLLECTION></TDLMESSAGE></TDL>
    </DESC></BODY></ENVELOPE>"""

def _build_voucher_xml(from_date, to_date, voucher_type_name):
    return f"""<ENVELOPE>
    <HEADER><VERSION>1</VERSION><TALLYREQUEST>Export</TALLYREQUEST><TYPE>Collection</TYPE><ID>SalesCollection</ID></HEADER>
    <BODY><DESC>
    <STATICVARIABLES>
        <SVFROMDATE TYPE="Date">{from_date}</SVFROMDATE>
        <SVTODATE TYPE="Date">{to_date}</SVTODATE>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
    </STATICVARIABLES>
    <TDL><TDLMESSAGE>
        <COLLECTION NAME="SalesCollection">
          <TYPE>Voucher</TYPE>
          <FILTER>SalesFilter</FILTER>
          <FETCH>DATE,VOUCHERNUMBER,REFERENCE,VOUCHERTYPENAME,STATENAME,AMOUNT,ALLLEDGERENTRIES.LIST,ALLINVENTORYENTRIES.LIST,ISPARTYLEDGER,LEDGERNAME</FETCH>
        </COLLECTION>
        <SYSTEM TYPE="Formulae" NAME="SalesFilter">$VoucherTypeName="{voucher_type_name}"</SYSTEM>
    </TDLMESSAGE></TDL>
    </DESC></BODY></ENVELOPE>"""

def voucher_xml_sales_re(f, t): return _build_voucher_xml(f, t, "Sales")
def voucher_xml_tmx_re(f, t): return _build_voucher_xml(f, t, "SALES THERMAX")
def voucher_xml_service_re(f, t): return _build_voucher_xml(f, t, "Service")

# -----------------------
# UTILITIES
# -----------------------
def clean_xml(x):
    x = re.sub(r"&#\d+;", "", x)
    x = re.sub(r"<(/?)[A-Za-z0-9]+:", r"<\1", x)
    x = re.sub(r"[^\x09\x0A\x0D\x20-\x7F]+", "", x)
    return x

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
# VOUCHER PARSING FUNCTION
# -----------------------
def fetch_voucher_data(tally_url, voucher_xml, ledger_parent):
    try:
        r = requests.post(tally_url, data=voucher_xml)
        raw_text = clean_xml(r.text)
        
        # Debugging step: Check if Tally actually sent data records or an empty envelope
        if "<VOUCHER" not in raw_text:
            return []
            
        root = ET.fromstring(raw_text)
        rows = []

        for v in root.findall(".//VOUCHER"):
            date = v.findtext("DATE", "")
            number = v.findtext("VOUCHERNUMBER", "")
            ref = v.findtext("REFERENCE", "-/-/-/-/-/-")
            ref_parts = ref.split("/")
            
            # Safe Parsing of Category
            if len(ref_parts) > 4: category = ref_parts[3]
            elif len(ref_parts) > 3: category = ref_parts[2]
            elif len(ref_parts) > 2: category = ref_parts[1]
            else: category = ref_parts[-1] if ref_parts else "-"

            # Safe Parsing of Category Type
            if len(ref_parts) < 5:
                cat_type = "Sales"
            else:
                cat_type = ref_parts[2]
                category = ref_parts[3]

            vtype = v.findtext("VOUCHERTYPENAME", "")
            state = v.findtext("STATENAME", "")

            if date and len(date) == 8:
                date = f"{date[6:8]}-{date[4:6]}-{date[0:4]}"

            voucher_total = get_basic_value(v)

            # Match entries. Fallback if ISPARTYLEDGER flag tag is missing in response
            ledger_entries = v.findall(".//ALLLEDGERENTRIES.LIST")
            party_found = False

            for e in ledger_entries:
                is_party = e.findtext("ISPARTYLEDGER")
                
                # If Tally tags it explicitly, or if it's the first ledger on a standard invoice
                if is_party == "Yes" or (is_party is None and not party_found):
                    ledger = e.findtext("LEDGERNAME", "")
                    parent = ledger_parent.get(ledger.upper(), "") if ledger else ""
                    
                    rows.append([
                        date, number, ref, category, cat_type,
                        vtype, ledger, parent, voucher_total, state
                    ])
                    party_found = True

            # Ultra fallback if no matching entry loops passed validation
            if not party_found and ledger_entries:
                first_ledger = ledger_entries[0].findtext("LEDGERNAME", "")
                parent = ledger_parent.get(first_ledger.upper(), "") if first_ledger else ""
                rows.append([
                    date, number, ref, category, cat_type,
                    vtype, first_ledger, parent, voucher_total, state
                ])

        return rows
    except Exception as e:
        print(f"Error parsing xml row context: {e}")
        return []

# -----------------------
# MAIN EXECUTION
# -----------------------
if __name__ == "__main__":
    ledger_parent = fetch_ledger(TALLY_URL, ledger_xml=ledger_xml_re())
    print("Ledgers Loaded Mapping Cache:", len(ledger_parent))

    # User Input with formatting safeguards
    input_date_from = input("Ex. 01042024 - From Date: ").strip().replace("-", "").replace("/", "")
    input_date_to = input("Ex. 30042024 - To Date: ").strip().replace("-", "").replace("/", "")

    if len(input_date_from) != 8 or len(input_date_to) != 8:
        print("Error: Input must be exactly 8 digits (DDMMYYYY). Run script again.")
        sys.exit(1)

    # Convert DDMMYYYY -> YYYYMMDD for Tally XML Compatibility
    FROM_DATE = f"{input_date_from[4:8]}{input_date_from[2:4]}{input_date_from[0:2]}"
    TO_DATE = f"{input_date_to[4:8]}{input_date_to[2:4]}{input_date_to[0:2]}"
    
    print(f"Querying Tally with Cleaned Request Window: {FROM_DATE} to {TO_DATE}...")

    final_rows = []

    # Sequential calls to bypass thread processing locks
    sales_xml = voucher_xml_sales_re(FROM_DATE, TO_DATE)
    sales_rows = fetch_voucher_data(TALLY_URL, sales_xml, ledger_parent)
    final_rows.extend(sales_rows)
    print(f"-> Sales Vouchers Extracted: {len(sales_rows)}")

    tmx_xml = voucher_xml_tmx_re(FROM_DATE, TO_DATE)
    tmx_rows = fetch_voucher_data(TALLY_URL, tmx_xml, ledger_parent)
    final_rows.extend(tmx_rows)
    print(f"-> SALES THERMAX Vouchers Extracted: {len(tmx_rows)}")

    service_xml = voucher_xml_service_re(FROM_DATE, TO_DATE)
    service_rows = fetch_voucher_data(TALLY_URL, service_xml, ledger_parent)
    final_rows.extend(service_rows)
    print(f"-> Service Vouchers Extracted: {len(service_rows)}")

    print("Total Compiled Data Rows:", len(final_rows))

    # -----------------------
    # CSV WRITE
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

    print(f"\nSuccess! File written to: '{output_file}' ({len(final_rows)} rows)")
