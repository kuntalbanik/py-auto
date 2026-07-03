import requests
import xml.etree.ElementTree as ET
import csv
import re

# from datetime import datetime

# TALLY_URL = "http://127.0.0.1:9000"
TALLY_URL = "http://192.168.1.131:9000"

FROM_DATE = "20240401"
TO_DATE = "20240630"


def clean_xml(x):

    x = re.sub(r"&#\d+;", "", x)
    x = re.sub(r"<(/?)[A-Za-z0-9]+:", r"<\1", x)
    x = re.sub(r"[^\x09\x0A\x0D\x20-\x7F]+", "", x)

    return x


# -----------------------
# LOAD LEDGER MASTER
# -----------------------
ledger_xml = """
<ENVELOPE>
 <HEADER>
  <VERSION>1</VERSION>
  <TALLYREQUEST>Export</TALLYREQUEST>
  <TYPE>Collection</TYPE>
  <ID>LedgerCollection</ID>
 </HEADER>

 <BODY>
  <DESC>
   <STATICVARIABLES>
    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
   </STATICVARIABLES>

   <TDL>
    <TDLMESSAGE>

     <COLLECTION NAME="LedgerCollection">
      <TYPE>Ledger</TYPE>
      <FETCH>NAME,PARENT</FETCH>
     </COLLECTION>

    </TDLMESSAGE>
   </TDL>

  </DESC>
 </BODY>
</ENVELOPE>
"""

r = requests.post(TALLY_URL, data=ledger_xml)

root = ET.fromstring(clean_xml(r.text))

ledger_parent = {}

for l in root.findall(".//LEDGER"):

    name = l.get("NAME")
    parent = l.findtext("PARENT")

    if name:
        ledger_parent[name.upper()] = parent

print("Ledgers Loaded:", len(ledger_parent))


# -----------------------
# LOAD SALES VOUCHERS
# -----------------------
voucher_xml = f"""
<ENVELOPE>
 <HEADER>
  <VERSION>1</VERSION>
  <TALLYREQUEST>Export</TALLYREQUEST>
  <TYPE>Collection</TYPE>
  <ID>SalesCollection</ID>
 </HEADER>

 <BODY>
  <DESC>

   <STATICVARIABLES>
    <SVFROMDATE TYPE="Date">{FROM_DATE}</SVFROMDATE>
    <SVTODATE TYPE="Date">{TO_DATE}</SVTODATE>
    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
   </STATICVARIABLES>

   <TDL>
    <TDLMESSAGE>

     <COLLECTION NAME="SalesCollection">
      <TYPE>Voucher</TYPE>
      <FILTER>SalesFilter</FILTER>

      <FETCH>
        DATE,
        VOUCHERNUMBER,
        REFERENCE,
        VOUCHERTYPENAME,
        STATENAME,
        PLACEOFSUPPLY,
        AMOUNT,
        ALLLEDGERENTRIES.LIST,
        ISPARTYLEDGER
      </FETCH>

     </COLLECTION>

     <SYSTEM TYPE="Formulae" NAME="SalesFilter">
      $VoucherTypeName="Sales"
     </SYSTEM>

    </TDLMESSAGE>
   </TDL>

  </DESC>
 </BODY>
</ENVELOPE>
"""

r = requests.post(TALLY_URL, data=voucher_xml)

root = ET.fromstring(clean_xml(r.text))


# -----------------------
# EXTRACT DATA
# -----------------------
rows = []

for v in root.findall(".//VOUCHER"):

    date = v.findtext("DATE")
    number = v.findtext("VOUCHERNUMBER")
    ref = v.findtext("REFERENCE", "-/-/-/-")
    category = ref.split("/")[2]
    vtype = v.findtext("VOUCHERTYPENAME")
    state = v.findtext("STATENAME")
    # supply = v.findtext("PLACEOFSUPPLY")

    # ledger = v.findtext("PARTYLEDGERNAME")

    if date != None:
        number_string = date
        part1 = number_string[0:4]  # type: ignore # First 4 characters
        part2 = number_string[4:6]  # type: ignore # Next 2 characters (from index 4 up to 6)
        part3 = number_string[6:8]  # type: ignore # Last 2 characters (from index 6 up to 8)

        date = part3 + "-" + part2 + "-" + part1
    else:
        date = ""

    voucher_total = abs(float(v.findtext("AMOUNT", "0")))
    # voucher_total = v.findtext("AMOUNT", "0")

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
                vtype,
                ledger,
                parent,
                voucher_total,
                state,
                # supply
            ]
        )


# -----------------------
# WRITE CSV
# -----------------------
header = [
    "Date",
    "Voucher_Number",
    "Reference",
    "Category",
    "Voucher_Type",
    "Ledger_Name",
    "Ledger_Parent",
    "Amount",
    "State_Name",
    # "Place_To_Supply"
]

with open("sales_export.csv", "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow(header)
    writer.writerows(rows)


print("CSV Created:", len(rows), "rows")
