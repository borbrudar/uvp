import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
import random as r
import time

# Imena datotek
RECEPTI_URLS = "recepti_urls"
# Dobimo url naslove prvih 1000 receptov
def get_recepti_urls():
    print("Parsam recepte:")
    f = open("data/" + RECEPTI_URLS, "x") 
    # Loopamo cez prvih 50 strani (vsaka stran ima po 20 receptov), da dobimo url naslove vseh receptov
    recepti_iskanje_url = "https://okusno.je/iskanje?t=recipe&sort=score&p="
    for i in range(1,51):
        page = requests.get(recepti_iskanje_url + str(i),3)
        soup = BeautifulSoup(page.content, "html.parser")
        for u in soup.find_all("a",href=True):
            if str(u['href']).startswith("/recept/"):
                f.write(u['href'])
                f.write("\n")
        # sprintej progress
        print("[" + str((i/50) * 100) + "%]")
        # spi za nekaj sekund
        time.sleep(r.randrange(1,3))      
    f.close()
    
#def recepti_parser():
#    f = open("data/" + RECEPTI_URLS,"r")

def main():
    if os.path.exists("data/" + RECEPTI_URLS) == False:
        get_recepti_urls()
    
    
    
main()