"""Main module."""

import xml.etree.ElementTree as ET

import pandas as pd
from suds.client import Client


def exportStationCodes():
    """
    https://cdmo.baruch.sc.edu/webservices.cfm

    exportStationCodesXML

    Returns the following XML data:
      NERR_Site_ID, Station_Code, Station_Name,
      Latitude/Longitude (in degrees), Latitude (in decimal), Longitude (in decimal),
      Active Status, Active Dates,
      State, Reserve_Name,
      the parameters reported for all stations, and a Real Time bit.

    Arguments
      None
    """
    soapClient = Client("http://cdmo.baruch.sc.edu/webservices2/requests.cfc?wsdl", timeout=90, retxml=True)

    # Get the station codes SOAP request example.
    data_xml = soapClient.service.exportStationCodesXML()
    data_tree = ET.fromstring(data_xml)

    # === extract the rows from the xml
    data_rows = []
    # Iterate through each row ('r' tag) and extract the 'cv' attribute values
    for row in data_tree.iter(tag='r'):
        data_row = [col.attrib['v'] for col in row.iter(tag='c')]
        data_rows.append(data_row)

    # Convert the extracted data into a pandas DataFrame
    df = pd.DataFrame(data_rows[1:], columns=data_rows[0])

    return df
