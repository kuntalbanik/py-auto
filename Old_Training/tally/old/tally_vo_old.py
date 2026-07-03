# -*- coding: utf-8 -*-

import requests
import xml.etree.ElementTree as ET
import csv
import re

# ==========================
# Tally Server
# ==========================

TALLY_URL = "http://192.168.1.131:9000"

FROM_DATE = "20240401"
TO_DATE = "20240407"


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
    <SVFROMDATE>{FROM_DATE}</SVFROMDATE>
    <SVTODATE>{TO_DATE}</SVTODATE>
    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
   </STATICVARIABLES>

   <TDL>
    <TDLMESSAGE>

     <COLLECTION NAME="SalesCollection">
      <TYPE>Voucher</TYPE>
      <FILTER>SalesFilter</FILTER>
      <FETCH>*</FETCH>
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


# ==========================
# Send request
# ==========================

print("Requesting Sales vouchers from Tally...")

response = requests.post(TALLY_URL, data=xml_request)

print("Data received from Tally")


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
# Flatten XML
# ==========================

def flatten_xml(elem, parent="", data=None):

    if data is None:
        data = {}

    key = parent + elem.tag

    if elem.text and elem.text.strip():
        data[key] = elem.text.strip()

    for attr, val in elem.attrib.items():
        data[key + "_" + attr] = val

    for child in elem:
        flatten_xml(child, key + "_", data)

    return data


# ==========================
# Extract vouchers
# ==========================

vouchers = []

for v in root.findall(".//VOUCHER"):

    vouchers.append(flatten_xml(v))


print("Total Sales vouchers:", len(vouchers))


# ==========================
# Detect columns
# ==========================

columns = set()

for v in vouchers:
    columns.update(v.keys())

columns = list(columns)


# ==========================
# Save CSV
# ==========================

with open("sales_vouchers_full.csv", "w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(f, fieldnames=columns)

    writer.writeheader()

    for v in vouchers:
        writer.writerow(v)


print("CSV created: sales_vouchers_full.csv")