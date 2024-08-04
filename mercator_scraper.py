import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
import random as r
import time
import utility as ut

IZDELKI = "data/izdelki.csv"
IZDELKI_HTML = "data/izdelki_html/"

def parse_izdelke(soup):
    # najdemo vse produkte
    csv = open(IZDELKI,'a')
    for izdelek in soup.find_all("ajax-add-to-cart", {"class" : "custom-element ajax-add-to-cart expand-add-to-cart__ajax-add-to-cart"}):
        izdelek = izdelek.find("button")
        cena = izdelek["data-price"]
        znamka = izdelek["data-brand"]
        akcija = izdelek["data-promo-price"]
        kolicina = float(izdelek["data-quantity"])
        ime = izdelek["data-name"].strip().split(",")[0]
        enota = "kos"
        # last je zadnji element imena (enota, ce je)
        last = str(izdelek["data-name"].strip().split(",")[-1]).split()
        if len(last) > 0: last = last[-1]
        else: last = "kos"
        enota,kolicina = ut.pretvori_enote(last,enota,kolicina)
        # appendamo izdelke v csv datoteko
        csv.write(ut.arr_to_csv([ime,znamka,cena,akcija,kolicina,enota]))


def main():
    # sparsamo vse izdelke na voljo v mercatorjevi spletni trgovini 
    base_url = "https://www.mercatoronline.si/sl/search?ipp=75&page="
    cnt = 1
    csv = open(IZDELKI,'w')
    csv.write("Ime izdelka, Znamka, Cena, Promocijska cena, Kolicina, Enota\n")
    csv.close()
    for i in range(1,207): # 207
        filename = "izdelki" + str(i) + ".html"
        ut.get_spletno_stran(base_url + str(i), IZDELKI_HTML + filename)
        html_doc = open(IZDELKI_HTML + filename, "rb").read()
        soup = BeautifulSoup(html_doc, "html.parser")
        parse_izdelke(soup)
        # sprintej progress
        print("[" + str((cnt/206) * 100) + "%]")
        cnt += 1
        
    
main()