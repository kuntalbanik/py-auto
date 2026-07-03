# -*- coding: utf-8 -*-

import requests
import xml.etree.ElementTree as ET

# ===================================
# Tally Server
# ===================================

TALLY_URL = "http://192.168.1.131:9000"


# ===================================
# Function: Send XML Request
# ===================================

def send_request(xml):

    headers = {"Content-Type": "application/xml"}

    response = requests.post(TALLY_URL, data=xml.encode("utf-8"), headers=headers)

    return response.text


# ===================================
# STEP 1 : Detect Current Company
# ===================================

company_xml = """
<ENVELOPE>
 <HEADER>
  <VERSION>1</VERSION>
  <TALLYREQUEST>Export</TALLYREQUEST>
  <TYPE>Collection</TYPE>
  <ID>List of Companies</ID>
 </HEADER>

 <BODY>
  <DESC>
   <TDL>
    <TDLMESSAGE>
     <COLLECTION NAME="List of Companies">
      <TYPE>Company</TYPE>
      <FETCH>Name</FETCH>
     </COLLECTION>
    </TDLMESSAGE>
   </TDL>
  </DESC>
 </BODY>
</ENVELOPE>
"""

company_response = send_request(company_xml)

root = ET.fromstring(company_response)

companies = []

for comp in root.findall(".//COMPANY"):
    name = comp.attrib.get("NAME")
    if name:
        companies.append(name)

print("\nCompanies detected:\n")

for c in companies:
    print(c)


# ===================================
# STEP 2 : Detect Voucher Types
# ===================================

voucher_xml = """
<ENVELOPE>
 <HEADER>
  <VERSION>1</VERSION>
  <TALLYREQUEST>Export</TALLYREQUEST>
  <TYPE>Collection</TYPE>
  <ID>VoucherTypes</ID>
 </HEADER>

 <BODY>
  <DESC>

   <TDL>
    <TDLMESSAGE>

     <COLLECTION NAME="VoucherTypes">
      <TYPE>VoucherType</TYPE>
      <FETCH>Name</FETCH>
     </COLLECTION>

    </TDLMESSAGE>
   </TDL>

  </DESC>
 </BODY>
</ENVELOPE>
"""

voucher_response = send_request(voucher_xml)

root = ET.fromstring(voucher_response)

voucher_types = []

for v in root.findall(".//VOUCHERTYPE"):
    name = v.attrib.get("NAME")
    if name:
        voucher_types.append(name)

print("\nVoucher Types detected:\n")

for v in voucher_types:
    print(v)