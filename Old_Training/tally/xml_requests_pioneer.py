# -*- coding: utf-8 -*-

# FROM_DATE = "20240401"
# TO_DATE = "20260331"
# FROM_DATE = input("Ex. 20240401 - From : ")
# TO_DATE = input("Ex. 20240430 - To : ")

# -----------------------
# LOAD LEDGER MASTER
# -----------------------

def ledger_xml_re():
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
    return ledger_xml


# -----------------------
# LOAD SALES VOUCHERS
# -----------------------

# Sales

def voucher_xml_sales_re(from_date, to_date):
    voucher_xml_sales = f"""
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
        <SVFROMDATE TYPE="Date">{from_date}</SVFROMDATE>
        <SVTODATE TYPE="Date">{to_date}</SVTODATE>
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
            DISPATCHFROMSTATENAME,
            AMOUNT,
            ALLLEDGERENTRIES.LIST,
            ALLINVENTORYENTRIES.LIST,
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
    return voucher_xml_sales


# SALES THERMAX

def voucher_xml_tmx_re(from_date, to_date):
    voucher_xml_tmx = f"""
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
        <SVFROMDATE TYPE="Date">{from_date}</SVFROMDATE>
        <SVTODATE TYPE="Date">{to_date}</SVTODATE>
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
          $VoucherTypeName="SALES THERMAX"
        </SYSTEM>

        </TDLMESSAGE>
      </TDL>

      </DESC>
    </BODY>
    </ENVELOPE>
    """
    return voucher_xml_tmx

# Service Bill
def voucher_xml_service_re(from_date, to_date):
    voucher_xml_service = f"""
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
        <SVFROMDATE TYPE="Date">{from_date}</SVFROMDATE>
        <SVTODATE TYPE="Date">{to_date}</SVTODATE>
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
          $VoucherTypeName="Service"
        </SYSTEM>

        </TDLMESSAGE>
      </TDL>

      </DESC>
    </BODY>
    </ENVELOPE>
    """
    return voucher_xml_service
