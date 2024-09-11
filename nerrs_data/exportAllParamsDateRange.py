"""
exportAllParamsDateRangeXML

Returns all parameters with DateTimeStamps greater than the mindate and less than or equal to the maxdate.

Arguments

Station_Code
mindate
maxdate
Parameter tested (Max: 1000 records)
"""
import numpy as np
import pandas as pd
from suds.client import Client
import xml.etree.ElementTree as ET

def exportAllParamsDateRange(stationCode, minDate, maxDate, paramTested=None, qcFilter=True):
    print('init SOAP client...')
    soapClient = Client(
        "http://cdmo.baruch.sc.edu/webservices2/requests.cfc?wsdl",
        timeout=90,
        retxml=True
    )
    print('submitting request...')
    # Get the station codes SOAP request example.
    data_xml = soapClient.service.exportAllParamsDateRangeXMLNew(
        stationCode,  # Station_Code
        minDate,
        maxDate,
        paramTested
    )
    print('parsing xml...')
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

    print('exporting as dataframe...')
    # Convert to DataFrame
    df = pd.DataFrame(records)

    if(qcFilter):
        print('filtering out qc <= 1 (suspect)...')
        # Loop through the columns to find pairs
        for col in df.columns:
            if col.startswith('F_'):
                # ensure flag vals are int & set empty flags to '4' (see key below)
                df[col] = df[col].fillna(4).astype(int)
                # Get the base column name by removing '_qc'
                base_col = col[2:] 
                if base_col in df.columns:
                    # Set the corresponding base column value to NaN using qc vals
                    # % QC Flag vals.
                    # % -5       Outside High Sensor Range
                    # % -4       Outside Low Sensor Range
                    # % -3       Data Rejected due to QAQC
                    # % -2       Missing Data
                    # % -1       Optional SWMP Supported Parameter
                    # %  0       Data Passed Initial QAQC Checks
                    # %  1       Suspect Data
                    # %  2       Open - reserved for later flag
                    # %  3       Calculated data: non-vented depth/level sensor correction
                    #            for changes in barometric pressure
                    # %  4       Historical Data:  Pre-Auto QAQC
                    # %  5       Corrected Data
                    # throw out -5 through -2
                    df.loc[df[col] <= -2, base_col] = np.nan    
                    # throw out 1
                    df.loc[df[col] == 1, base_col] = np.nan
                    
        # Remove all columns that end with '_qc'
        df_cleaned = df.drop([col for col in df.columns if col.endswith('_qc')], axis=1)
    else:
        print('skipping qc filter...')
    return(df)
