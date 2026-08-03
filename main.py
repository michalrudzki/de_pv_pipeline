#from lib import packages
from bs4 import BeautifulSoup
import requests
import json

page_url =  'https://pvmonitor.pl/inst_sumaax.php?i=0&id=14644&rodz=1&od=2026-08-02&do=2026-08-02#/sumapv' #'https://miroslawmamczur.pl/'
page = requests.get(page_url)
soup = BeautifulSoup(page.content, 'html.parser')  # note: bs4 can use lxml under the hood which makes it really fast!
 
# find single element by node name
#print(soup.find("title").text)
# find multiple using find_all and attribute matching
#print(soup.prettify())
#for element in soup.find_all("div", class_="count green")[:5]:
#    print(element.text)

#for element in soup.find_all("span", class_="count_top")[:5]:
#    print(element.text)

dict_mesurements = {}
for value, mesure in zip(soup.find_all("div", class_="count green")[:5], soup.find_all("span", class_="count_top")[:5]):
    dict_mesurements[mesure.text]=value.text

# Directly from the dictionary
with open('json_data.json', 'w') as outfile:
    json.dump(dict_mesurements, outfile)

with open('json_data.json', 'r') as json_file:
    data = json.load(json_file)

print(data)

#list_all_p = soup.find("div", string="58,00")
#print(f'znalazłem {len(list_all_p)} linków')
#print(list_all_p)