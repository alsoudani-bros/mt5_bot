import xml.etree.ElementTree as Xet
import pandas as pd
import os
import sys
from bs4 import BeautifulSoup

def from_xml_to_csv(XML_file_name, csv_file_name):
    
    cols = ["name", "phone", "email", "date", "country"]
    rows = []
    
    # Parsing the XML file
    xmlparse = Xet.parse(XML_file_name)
    root = xmlparse.getroot()
    for i in root:
        name = i.find("name").text
        phone = i.find("phone").text
        email = i.find("email").text
        date = i.find("date").text
        country = i.find("country").text
    
        rows.append({"name": name,
                    "phone": phone,
                    "email": email,
                    "date": date,
                    "country": country})
    
    df = pd.DataFrame(rows, columns=cols)
    
    # Writing dataframe to csv
    df.to_csv(csv_file_name)
    
def from_html_to_csv(HTML_file_name, csv_file_name):
    data = []
    
    # for getting the header from
    # the HTML file
    list_header = []
    soup = BeautifulSoup(open(HTML_file_name),'html.parser')
    header = soup.find_all("table")[0].find("tr")
    
    for items in header:
        try:
            list_header.append(items.get_text())
        except:
            continue
    
    # for getting the data
    HTML_data = soup.find_all("table")[0].find_all("tr")[1:]
    
    for element in HTML_data:
        sub_data = []
        for sub_element in element:
            try:
                sub_data.append(sub_element.get_text())
            except:
                continue
        data.append(sub_data)
    
    # Storing the data into Pandas
    # DataFrame
    dataFrame = pd.DataFrame(data = data, columns = list_header)
    
    # Converting Pandas DataFrame
    # into CSV file
    dataFrame.to_csv('Geeks.csv')
