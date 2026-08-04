#from lib import packages
from bs4 import BeautifulSoup
import requests
import csv
import datetime
from random import randint
from time import sleep

now = datetime.datetime.now() - datetime.timedelta(days=1)
_date = now.strftime("%Y-%m-%d")

list_of_users=[]
with open("data/list_of_users.csv", newline='') as myFile:
    csvReader = csv.reader(myFile)
    
    # Loop through each row in the CSV file
    for i, row in enumerate(csvReader):
        if i == 0:
            continue
        list_of_users.append(row)  # Prints each row as a list of values

i=0
for user in list_of_users:
    id=user[0]
    page_url =  f'https://pvmonitor.pl/inst_sumaax.php?i=0&id={id}&rodz=1&od={_date}&do={_date}#/sumapv' 
    print(page_url)

    sleep(randint(1,3)) # sleep random time
    page = requests.get(page_url)
    soup = BeautifulSoup(page.content, 'html.parser')  # note: bs4 can use lxml under the hood which makes it really fast!

    dict_mesurements = {}
    dict_mesurements['idinst']=id
    for value, mesure in zip(soup.find_all("div", class_="count green")[:5], soup.find_all("span", class_="count_top")[:5]):
        dict_mesurements[mesure.text]=float(value.text.replace(',', '.'))

    col_names = list(dict_mesurements.keys())
    
    with open(f'data/pv_production{_date}.csv', 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=col_names)
        if i == 0:
            writer.writeheader()
        writer.writerow(dict_mesurements)

    i+=1

'''
for k, v in dict_mesurements.items():
    print(k, v)

# Directly from the dictionary
with open('data/json_data.json', 'w') as outfile:
    json.dump(dict_mesurements, outfile)

with open('data/json_data.json', 'r') as json_file:
    data = json.load(json_file)

print(data)
'''
