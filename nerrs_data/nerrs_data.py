"""Main module."""

import os

from zeep import Client as ZeepClient


def getData(station_code, param_name):
    """
    fetch met data based on docs from https://cdmo.baruch.sc.edu/webservices.cfm
    """

    # Initialize the Zeep client
    zeep_client = ZeepClient(wsdl="http://cdmo.baruch.sc.edu/webservices2/requests.cfc?wsdl")

    print(zeep_client.service)  # Lists available operations and their bindings
    
    # Assuming `station_code` and `param_name` are defined
    response = zeep_client.service.exportSingleParamXML(
        station_code,  # Station_Code
        25,  # recs
        param_name  # param
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
