import os
import re
import sys
import requests
import xml.etree.ElementTree as ET
import csv

# Target Tally instance endpoint
TALLY_URL = "http://192.168.1.131:9000"

# -----------------------
# TALLY XML REQUESTS
# -----------------------
def ledger_xml_re():
    """Generates XML request to fetch all ledgers and their parent groups."""
    return """<ENVELOPE>
    <HEADER><VERSION>1</VERSION><TALLYREQUEST>Export</TALLYREQUEST><TYPE>Collection</TYPE><ID>LedgerCollection</ID></HEADER>
    <BODY><DESC><STATICVARIABLES><SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT></STATICVARIABLES>
    <TDL><TDLMESSAGE><COLLECTION NAME="LedgerCollection"><TYPE>Ledger</TYPE><FETCH>NAME,PARENT</FETCH></COLLECTION></TDLMESSAGE></TDL>
    </DESC></BODY></ENVELOPE>"""

def voucher_xml_receipt_re(from_date, to_date):
    """
    Generates XML request for Receipts. 
    Uses $$IsReceipt to catch all variations of receipt voucher types safely.
    """
    return f"""<ENVELOPE>
    <HEADER>
      <VERSION>1</VERSION>
      <TALLYREQUEST>Export</TALLYREQUEST>
      <TYPE>Collection</TYPE>
      <ID>ReceiptCollection</ID>
    </HEADER>
    <BODY>
      <DESC>
      <STATICVARIABLES>
        <SVFROMDATE TYPE="Date">{from_date}</SVFROMDATE>
        <SVTODATE TYPE="Date">{to_date}</SVTODATE>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>
      <TDL>
        <TDLMESSAGE>
        <COLLECTION NAME="ReceiptCollection">
          <TYPE>Voucher</TYPE>
          <FILTER>ReceiptFilter</FILTER>
          <FETCH>
            DATE,
            VOUCHERNUMBER,
            REFERENCE,
            VOUCHERTYPENAME,
            STATENAME,
            ALLLEDGERENTRIES.LIST,
            ISPARTYLEDGER
          </FETCH>
        </COLLECTION>
        <SYSTEM TYPE="Formulae" NAME="ReceiptFilter">
          $$IsReceipt:$VoucherTypeName
        </SYSTEM>
        </TDLMESSAGE>
      </TDL>
      </DESC>
    </BODY>
    </ENVELOPE>"""

# -----------------------
# CLEAN XML & PARSING UTILITIES
# -----------------------
def clean_xml(x):
    """Removes special character entities and tags that break ElementTree parsing."""
    x = re.sub(r"&#\d+;", "", x)
    x = re.sub(r"<(/?)[A-Za-z0-9]+:", r"<\1", x)
    x = re.sub(r"[^\x09\x0A\x0D\x20-\x7F]+", "", x)
    return x

def fetch_ledger(tally_url):
    """Fetches and creates a dictionary mapping uppercase ledger names to their parents."""
    try:
        r = requests.post(tally_url, data=ledger_xml_re())
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

# -----------------------
# CORE DATA EXTRACTION
# -----------------------
def fetch_receipt_data(tally_url, voucher_xml, ledger_parent):
    try:
        r = requests.post(tally_url, data=voucher_xml)
        raw_text = clean_xml(r.text)
        
        # --- BREAKPOINT DEBUG LOGGER ---
        print("\n=== TALLY RAW RESPONSE DIAGNOSTIC ===")
        print("Response XML Size:", len(raw_text), "characters")
        print("Snippet (First 350 chars):")
        print(raw_text[:350].strip())
        print("=====================================\n")

        if "<VOUCHER" not in raw_text:
            print("Notice: No <VOUCHER> elements found in Tally's response data.")
            return []
            
        root = ET.fromstring(raw_text)
        rows = []

        for v in root.findall(".//VOUCHER"):
            date = v.findtext("DATE", "")
            number = v.findtext("VOUCHERNUMBER", "")
            ref = v.findtext("REFERENCE", "-")
            vtype = v.findtext("VOUCHERTYPENAME", "Receipt")
            state = v.findtext("STATENAME", "")

            # Reformat Tally's YYYYMMDD string format out into DD-MM-YYYY
            if date and len(date) == 8:
                date = f"{date[6:8]}-{date[4:6]}-{date[0:4]}"

            ledger_entries = v.findall(".//ALLLEDGERENTRIES.LIST")
            
            # Robust extraction strategy: look for explicit ledger entries
            for e in ledger_entries:
                is_party = e.findtext("ISPARTYLEDGER")
                ledger = e.findtext("LEDGERNAME", "")
                
                # Extract value. Tally stores receipts as negative credits inside lists
                amount = abs(float(e.findtext("AMOUNT", "0")))

                # Capture entry if explicitly labeled party ledger, or fallback if flag is omitted 
                if is_party == "Yes" or (is_party is None and amount > 0):
                    if ledger:
                        parent = ledger_parent.get(ledger.upper(), "Not Found")
                        rows.append([
                            date, number, ref, vtype, ledger, parent, amount, state
                        ])
                    
        return rows
    except Exception as e:
        print(f"Error encountered parsing XML elements: {e}")
        return []

# -----------------------
# EXECUTION ENTRYPOINT
# -----------------------
if __name__ == "__main__":
    print("Connecting to Tally to cache Account Ledger definitions...")
    ledger_parent = fetch_ledger(TALLY_URL)
    print("Ledgers Loaded Mapping Cache:", len(ledger_parent))

    # Input handlers with defensive stripping routines against formatting inputs
    input_date_from = input("Ex. 01052026 - From Date: ").strip().replace("-", "").replace("/", "")
    input_date_to = input("Ex. 08062026 - To Date: ").strip().replace("-", "").replace("/", "")

    if len(input_date_from) != 8 or len(input_date_to) != 8:
        print("Error: Input must be exactly 8 digits format (DDMMYYYY). Please restart script.")
        sys.exit(1)

    # Reconstruct input dates safely to form YYYYMMDD required by Tally XML properties
    FROM_DATE = f"{input_date_from[4:8]}{input_date_from[2:4]}{input_date_from[0:2]}"
    TO_DATE = f"{input_date_to[4:8]}{input_date_to[2:4]}{input_date_to[0:2]}"
    
    print(f"Submitting query window to Tally Server: {FROM_DATE} to {TO_DATE}...")

    receipt_xml = voucher_xml_receipt_re(FROM_DATE, TO_DATE)
    final_rows = fetch_receipt_data(TALLY_URL, receipt_xml, ledger_parent)

    print("Total Receipt Rows Compiled:", len(final_rows))

    # -----------------------
    # CSV OUTPUT MANAGEMENT
    # -----------------------
    header = [
        "Date", "Receipt_Number", "Reference", "Voucher_Type", 
        "Party_Ledger_Name", "Ledger_Parent", "Amount_Received", "State_Name"
    ]

    output_file = "receipt_vouchers_export.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(final_rows)

    print(f"\nExecution Complete! File saved: '{output_file}' with {len(final_rows)} records.")
