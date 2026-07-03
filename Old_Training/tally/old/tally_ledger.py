import requests
import xml.etree.ElementTree as ET
import re

TALLY_URL = "http://192.168.1.131:9000"

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

response = requests.post(TALLY_URL, data=xml)

clean = response.text
clean = re.sub(r'&#\d+;', '', clean)
clean = re.sub(r'[^\x09\x0A\x0D\x20-\x7F]', '', clean)

root = ET.fromstring(clean)

for ledger in root.findall(".//LEDGER"):
    
    name = ledger.get("NAME")
    group = ledger.findtext("PARENT")

    print(name, "->", group)

