"""
exportAllParamsDateRangeXML

Returns all parameters with DateTimeStamps greater than the mindate and less than or equal to the maxdate.

Arguments

Station_Code
mindate
maxdate
Parameter tested (Max: 1000 records)
"""

import pandas as pd
from suds.client import Client
import xml.etree.ElementTree as ET

def exportAllParamsDateRange(stationCode, minDate, maxDate, paramTested):
    soapClient = Client(
        "http://cdmo.baruch.sc.edu/webservices2/requests.cfc?wsdl",
        timeout=90,
        retxml=True
    )

    # Get the station codes SOAP request example.
    data_xml = soapClient.service.exportAllParamsDateRangeXMLNew(
        stationCode,  # Station_Code
        minDate,
        maxDate,
        paramTested
    )
    data_tree = ET.fromstring(data_xml)
    #print(
    #    "data:\n",
    #    data_xml.decode()
    #)

    # Register namespaces
    namespaces = {
        'soapenv': "http://schemas.xmlsoap.org/soap/envelope/",
        'ns1': "http://webservices2",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'ns2': "http://xml.apache.org/xml-soap"
    }
    
    # Initialize a list to store records
    records = []

    # Extract data
    for data in data_tree.iter(tag='data'):
        record = {}
        for elem in data:
            record[elem.tag] = elem.text
        records.append(record)

    # Convert to DataFrame
    df = pd.DataFrame(records)

    return(df)
