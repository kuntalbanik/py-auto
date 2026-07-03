# -*- coding: utf-8 -*-

import requests
import xml.etree.ElementTree as ET
import csv
import re


'''
Required

Sales
SALES THERMAX
Service Bill

'''



# ==========================
# Tally Server
# ==========================

TALLY_URL = "http://192.168.1.131:9000"
# TALLY_URL = "http://127.0.0.1:9000"

FROM_DATE = "20240401"
TO_DATE = "20240630"


# ==========================
# XML Request (Sales only)
# ==========================

xml_request = f"""
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
		VOUCHERREFERENCE,
		VOUCHERNUMBER,
		VOUCHERTYPENAME,
		PARTYLEDGERNAME,
		NARRATION,
		AMOUNT,
		DATE,
		STATENAME,
		PLACEOFSUPPLY,
		VCHENTRYMODE,
		ALLLEDGERENTRIES.LEDGERNAME,
		ALLLEDGERENTRIES.LIST,
		ALLLEDGERENTRIES.PARENT,
		LEDGERNAME,
		ALLINVENTORYENTRIES.LIST,
		STOCKITEMNAME,
		BILLEDQTY,
		RATE,
		VALUE,
        ALLLEDGERENTRIES.LIST.LEDGERNAME,
       ALLLEDGERENTRIES.LIST.AMOUNT,
       ALLLEDGERENTRIES.LIST.LEDGERNAME:LEDGERPARENT
	  </FETCH>
     </COLLECTION>
	 <SYSTEM TYPE="Formulae" NAME="SalesFilter">
      $VoucherTypeName = "Sales"
     </SYSTEM>

    </TDLMESSAGE>
   </TDL>

  </DESC>
 </BODY>
</ENVELOPE>
"""


xml = """
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
      <FETCH>
       NAME,
       PARENT
      </FETCH>
     </COLLECTION>

    </TDLMESSAGE>
   </TDL>

  </DESC>
 </BODY>
</ENVELOPE>
"""



# ==========================
# Send request
# ==========================

print("Requesting Sales vouchers from Tally...")

response = requests.post(TALLY_URL, data=xml_request)

print("Data received from Tally")




'''

# request tally
response = requests.post(TALLY_URL, data=xml)

# clean xml
clean = re.sub(r'[^\x09\x0A\x0D\x20-\x7F]+','',response.text)

root = ET.fromstring(clean)


# read ledgers
for ledger in root.findall(".//LEDGER"):

    name = ledger.get("NAME")          # ledger name
    group = ledger.findtext("PARENT")  # ledger group

    print(name, "->", group)
'''

# ==========================
# XML CLEANING BLOCK
# ==========================

raw_xml = response.text

# remove invalid XML entities
clean_xml = re.sub(r'&#\d+;', '', raw_xml)

# remove non printable characters
clean_xml = re.sub(r'[^\x09\x0A\x0D\x20-\x7F]+', '', clean_xml)

# remove namespace prefixes مثل UDF:
clean_xml = re.sub(r'<(/?)[A-Za-z0-9]+:', r'<\1', clean_xml)


# ==========================
# Parse XML safely
# ==========================

try:

    root = ET.fromstring(clean_xml)

except Exception as e:

    print("XML parse error:", e)
    print("\nXML preview:\n")
    print(clean_xml[:2000])
    exit()
	

# ==========================
# Extract vouchers
# ==========================

separator = "-"

vouchers = []

# Define header OUTSIDE loop
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

ledger_groups = {}




for v in root.findall(".//VOUCHER"):

    if v.findtext("AMOUNT") != None:
        amt = abs(float(v.findtext("AMOUNT"))) # type: ignore
        # amt = v.findtext("AMOUNT")
    else:
        amt = None
		
    if v.findtext("DATE") != None:
        number_string = v.findtext("DATE")
        part1 = number_string[0:4] # type: ignore # First 4 characters
        part2 = number_string[4:6] # type: ignore # Next 2 characters (from index 4 up to 6)
        part3 = number_string[6:8] # type: ignore # Last 2 characters (from index 6 up to 8)
        	
        date = part3+"-"+part2+"-"+part1
    else:
        date = ""

    # ledger = v.findtext("LEDGERNAME")
    # group = v.findtext("LEDGERPARENT")

    # for e in v.findall(".//ALLLEDGERENTRIES.LIST"):

    row = [
        date,
        v.findtext("VOUCHERNUMBER"),
        v.findtext("REFERENCE"),
        v.findtext("VCHENTRYMODE"),
        v.findtext("LEDGERNAME"),
        v.findtext("LEDGERPARENT"),
        amt,
        v.findtext("STATENAME"),
        v.findtext("PLACEOFSUPPLY")
    ]

    vouchers.append(row)

print("Total Sales vouchers:", len(vouchers))



# ==========================
# Save CSV
# ==========================

with open("sales_vouchers_full.csv", "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    # write header
    writer.writerow(header)

    # write voucher rows
    writer.writerows(vouchers)

print("CSV created: sales_vouchers_full.csv")
