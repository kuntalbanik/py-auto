import requests
import xml.etree.ElementTree as ET

url = "http://192.168.1.131:9000"

xml = """
<ENVELOPE>
 <HEADER>
   <VERSION>1</VERSION>
   <TALLYREQUEST>EXPORT</TALLYREQUEST>
   <TYPE>COLLECTION</TYPE>
   <ID>List of Companies</ID>
 </HEADER>

 <BODY>
   <DESC>
     <STATICVARIABLES>
       <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
     </STATICVARIABLES>
   </DESC>
 </BODY>
</ENVELOPE>
"""

response = requests.post(url, data=xml)

print("RAW RESPONSE:\n")
print(response.text)

root = ET.fromstring(response.text)

companies = []

# COMPANY tag এর NAME attribute থেকে কোম্পানি নাম বের করা
for company in root.findall(".//COMPANY"):

    name = company.attrib.get("NAME")

    if name:
        companies.append(name)

print("\nCompanies Found:\n")

for c in companies:
    print(c)