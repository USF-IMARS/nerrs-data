"""Main module."""

import os

import pandas as pd
import requests
from suds.client import Client
import xml.etree.ElementTree as ET

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
    print(df)
    
    # write the data to a csv file
    df.to_csv("./datafile.csv")

    exit()
    
    # === upload the data

    UPLOADER_HOSTNAME = os.environ["UPLOADER_HOSTNAME"]
    if UPLOADER_HOSTNAME.endswith('/'):  # rm possible trailing /
        UPLOADER_HOSTNAME = UPLOADER_HOSTNAME[:-1]
    UPLOADER_ROUTE = UPLOADER_HOSTNAME + "/submit/sat_image_extraction"

    url = UPLOADER_ROUTE  # Replace this with your actual URL
    data = {
        'measurement': 'nerrs_met_data',
        'tag_set': 'station_code=SPOT30987C',
        'fields': 'Sal',
        'time_column': 'utc_timestamp',
    }

    files = {'file': ('datafile.csv', open('./datafile.csv', 'rb'))}

    response = requests.post(url, data=data, files=files)

    if response.status_code == 200:
        print("Upload successful")
    else:
        print(f"Upload failed with status code {response.status_code}")
        print(response.text)
        raise ValueError(response.text)


getData("acespwq", "Sal")
