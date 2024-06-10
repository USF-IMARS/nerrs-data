"""Main module."""

import xml.etree.ElementTree as ET

import pandas as pd
from suds.client import Client


def getData(station_code, param_name):
    """
    fetch met data based on docs from https://cdmo.baruch.sc.edu/webservices.cfm
    """
    soapClient = Client("http://cdmo.baruch.sc.edu/webservices2/requests.cfc?wsdl", timeout=90, retxml=True)

    # Get the station codes SOAP request example.
    data_xml = soapClient.service.exportSingleParamXML(
        station_code,  # Station_Code
        25,  # Number of records to retrieve TODO: make this inf?
        param_name,  # parameter
    )
    data_tree = ET.fromstring(data_xml)
    print("data:\n", data_xml.decode().replace("\t", "").replace("\n", "").replace(" ", ""))
    print(data_tree.tag)

    # === extract the rows from the xml
    data_rows = []
    # Iterate through each row ('r' tag) and extract the 'cv' attribute values
    for row in data_tree.iter(tag='r'):
        data_row = [col.attrib['v'] for col in row.iter(tag='c')]
        # Append if data row contains exactly two elements (date and value)
        if len(data_row) == 2:
            data_rows.append(data_row)

    data_rows = data_rows[1:]  # rm duplicated header row

    # Convert the extracted data into a pandas DataFrame
    df = pd.DataFrame(data_rows, columns=['DateTimeStamp', 'Sal'])
    
    # Convert the 'date' column to datetime format
    df['DateTimeStamp'] = pd.to_datetime(df['DateTimeStamp'], format='%m/%d/%Y')
    
    # Convert to RFC3339 format
    df['DateTimeStamp'] = df['DateTimeStamp'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    return df


# test
# getData("acespwq", "Sal")
