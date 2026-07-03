# -*- coding: utf-8 -*-

import requests
import xml.etree.ElementTree as ET
import csv
import re

TALLY_URL = "http://192.168.1.131:9000"

FROM_DATE = "20240401"
TO_DATE = "20240630"


# -------------------------
# CLEAN XML
# -------------------------
# def clean_xml(x):

#     x = re.sub(r'&#\d+;', '', x)
#     x = re.sub(r'[^\x09\x0A\x0D\x20-\x7F]+', '', x)

#     return x


def clean_xml(x):

    # remove invalid numeric references
    x = re.sub(r'&#\d+;', '', x)

    # remove namespace prefixes like UDF:
    x = re.sub(r'<(/?)[A-Za-z0-9]+:', r'<\1', x)

    # remove invalid characters
    x = re.sub(r'[^\x09\x0A\x0D\x20-\x7F]+', '', x)

    return x





# -------------------------
# STEP 1
# LOAD LEDGER PARENT
# -------------------------
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

r = requests.post(TALLY_URL,data=ledger_xml)

root = ET.fromstring(clean_xml(r.text))

ledger_parent = {}

for l in root.findall(".//LEDGER"):

    name = l.get("NAME")
    parent = l.findtext("PARENT")

    if name:
        ledger_parent[name.upper()] = parent


print("Ledgers Loaded:",len(ledger_parent))


# -------------------------
# STEP 2
# SALES VOUCHERS
# -------------------------
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
        VCHENTRYMODE,
        STATENAME,
        PLACEOFSUPPLY,
        ALLLEDGERENTRIES.LIST
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

r = requests.post(TALLY_URL,data=voucher_xml)

root = ET.fromstring(clean_xml(r.text))


# -------------------------
# STEP 3
# EXTRACT DATA
# -------------------------
rows = []

for v in root.findall(".//VOUCHER"):

    date = v.findtext("DATE")
    number = v.findtext("VOUCHERNUMBER")
    ref = v.findtext("REFERENCE")
    vtype = v.findtext("VCHENTRYMODE")
    state = v.findtext("STATENAME")
    supply = v.findtext("PLACEOFSUPPLY")

    for e in v.findall(".//ALLLEDGERENTRIES.LIST"):

        ledger = e.findtext("LEDGERNAME")
        amount = e.findtext("AMOUNT")

        parent = ledger_parent.get(ledger.upper(),"") # type: ignore

        rows.append([
            date,
            number,
            ref,
            vtype,
            ledger,
            parent,
            amount,
            state,
            supply
        ])


# -------------------------
# STEP 4
# SAVE CSV
# -------------------------
header = [
"Date",
"Voucher_Number",
"Reference",
"Voucher_Type",
"Ledger_Name",
"Ledger_Parent",
"Amount",
"State_Name",
"Place_To_Supply"
]


with open("sales_voucher_export.csv","w",newline="",encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow(header)

    writer.writerows(rows)


print("CSV Created Successfully")