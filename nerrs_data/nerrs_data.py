"""Main module."""

import os

import requests
from suds.client import Client

from suds.xsd.doctor import Import, ImportDoctor


def getData(station_code, param_name):
    """
    fetch met data based on docs from https://cdmo.baruch.sc.edu/webservices.cfm
    """
    target_namespace = 'http://xml.apache.org/xml-soap'
    # use the import doctor to check the wsdl
    schema_import = Import('http://schemas.xmlsoap.org/soap/encoding/', location='http://schemas.xmlsoap.org/soap/encoding/')
    schema_import.filter.add(target_namespace)

    # Create a Doctor instance with the import
    doctor = ImportDoctor(schema_import)

    # Initialize the client with the Doctor
    soapClient = Client(
        "http://cdmo.baruch.sc.edu/webservices2/requests.cfc?wsdl",
        timeout=90,
        retxml=False,
        doctor=doctor
    )




    soapClient = Client("http://cdmo.baruch.sc.edu/webservices2/requests.cfc?wsdl", timeout=90, retxml=False)

    # Get the station codes SOAP request example.
    param_data = soapClient.service.exportSingleParamXML(
        station_code,  # Station_Code
        25,  # Number of records to retrieve TODO: make this inf?
        param_name,  # parameter
    )
    print("data:\n", param_data)

    # write the data to a csv file
    param_data.to_csv("./datafile.csv")

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
