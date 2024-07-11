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

def exportStationCodesDictFor(nerr_site_id):
    df = exportStationCodes()
    df = df.drop(columns=['Lat_Long', 'latitude', 'longitude'])
    # view uniques like:
    # df['state'].unique()

    # === subset however you want:
    # df = df[df['reserve_name'] == 'Sapelo Island']
    # or
    # df = df[df['state'] == 'ga']
    # or
    df = df[df['NERR_SITE_ID'] == nerr_site_id]

    # === build the dict for the selection
    for station_type in ['nut', 'met', 'wq']:
        print(f"\n# list of stations for {station_type}")
        print("stations = [")
        
        df_subset = df[df['Station_Code'].str.endswith(station_type)]

        for i,row in df_subset.iterrows():
            row['params_reported'] = row['params_reported'].split(',')
            print("    ", row.to_json(), ',')

        print("]")
        #params_dict = {
        #    row['Station_Code']: row['params_reported'].split(',') for index, row in df_subset.iterrows()
        #}
        #print('\n', station_type, ' = ', params_dict)
