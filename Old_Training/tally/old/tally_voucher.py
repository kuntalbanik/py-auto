import requests
import re

# TALLY_URL = "http://192.168.1.131:9000"
TALLY_URL = "http://127.0.0.1:9000"

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
       PARENT,
       GUID
      </FETCH>

     </COLLECTION>

    </TDLMESSAGE>
   </TDL>

  </DESC>
 </BODY>
</ENVELOPE>
"""

r = requests.post(TALLY_URL,data=xml)

clean = re.sub(r'[^\x09\x0A\x0D\x20-\x7F]+','',r.text)

print(clean[:2000])