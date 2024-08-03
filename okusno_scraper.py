import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
import random as r
import time

# Imena datotek
RECEPTI_URLS = "recepti_urls"
RECEPTI = "recepti.csv"
RECEPTI_HTML_PREFIX = "data/recepti_html/"

# Timeout za gettanje strani
GET_TIMEOUT = 3

# Dobimo url naslove prvih 1000 receptov


def get_recepti_urls():
    print("Parsam recepte:")
    f = open("data/" + RECEPTI_URLS, "x")
    # Loopamo cez prvih 50 strani (vsaka stran ima po 20 receptov), da dobimo url naslove vseh receptov
    recepti_iskanje_url = "https://okusno.je/iskanje?t=recipe&sort=score&p="
    for i in range(1, 51):
        page = requests.get(recepti_iskanje_url + str(i), timeout=GET_TIMEOUT)
        soup = BeautifulSoup(page.content, "html.parser")
        for u in soup.find_all("a", href=True):
            if str(u['href']).startswith("/recept/"):
                f.write(u['href'])
                f.write("\n")
        # sprintej progress
        print("[" + str((i/50) * 100) + "%]")
        # spi za nekaj sekund
        time.sleep(r.randrange(1, 3))
    f.close()


# doloci skupne lastnosti vseh receptov in jih zapise v skupen csv
def recept_skupno(soup):
    f = open("data/" + RECEPTI, "a")  # odpremo skupen csv file
    # Najdi avtorja
    avtor = "Brez"
    for a in soup.find_all("a", href=True):
        # print(a)
        if "avtor" in str(a):
            avtor = a.text
            break
    # Najdi tezavnost (zlo hacky)
    tezavnost = 0
    t1 = str(soup.find("div", {"class": "flex flex-row items-center gap-4 difficulty difficulty-large difficulty-1 border-b border-black/10 dark:border-white/10 flex h-full items-center justify-center md:border-b-0 md:border-r md:py-0 md:w-1/4 px-32 py-16 w-full"}))
    t2 = str(soup.find("div", {"class": "flex flex-row items-center gap-4 difficulty difficulty-large difficulty-2 border-b border-black/10 dark:border-white/10 flex h-full items-center justify-center md:border-b-0 md:border-r md:py-0 md:w-1/4 px-32 py-16 w-full"}))
    t3 = str(soup.find("div", {"class": "flex flex-row items-center gap-4 difficulty difficulty-large difficulty-3 border-b border-black/10 dark:border-white/10 flex h-full items-center justify-center md:border-b-0 md:border-r md:py-0 md:w-1/4 px-32 py-16 w-full"}))
    if t1 is not None:
        tezavnost = 1
    elif t2 is not None:
        tezavnost = 2
    elif t3 is not None:
        tezavnost = 3

    # Dolzina priprave + kuhanja
    cas_priprave = 9999  # error values
    cas_kuhanja = 9999
    skupen_cas = 9999
    for a in soup.find_all("span"):
        if a.text == "PRIPRAVA":
            text_priprava = str(a.parent.text).split()
            # convertej ure + minute v minute
            if text_priprava[2] == "min":
                cas_priprave = int(text_priprava[1])
            else:
                cas_priprave = int(text_priprava[1])*60 + int(text_priprava[3])
        if a.text == "KUHANJE":
            text_kuhanje = str(a.parent.text).split()
            # enako za cas kuhanja
            if text_kuhanje[2] == "min":
                cas_kuhanja = int(text_kuhanje[1])
            else:
                cas_kuhanja = int(text_kuhanje[1])*60 + int(text_kuhanje[3])

    skupen_cas = min(cas_priprave+cas_kuhanja, 9999)

    # dolzino navodil (proxy za tezavnost)
    dolzina_navodil = 0
    for a in soup.find_all("div", {"class": "flex relative p-16 transition hover:bg-[rgba(0,0,0,.02)]"}):
        dolzina_navodil += len(str(a.text))

    f.write(str(avtor) + " , " + str(tezavnost) + " , " + str(cas_priprave) + " , " +
            str(cas_kuhanja) + " , " + str(skupen_cas) + " , " + str(dolzina_navodil) + "\n")
    f.close()

# doloci sestavine recepta in jih zapise v lasnto datoteko


def recept_sestavine(soup):
    return False


# gre cez vse recepte in jih sparsa
def recepti_parser():
    print("Parsam recepte:")
    f = open("data/" + RECEPTI, "w")
    f.write(
        "Avtorji, Tezavnost, Cas priprave, Cas kuhanja, Skupen cas, Dolzina navodil\n")
    f.close()
    with open("data/" + RECEPTI_URLS, encoding="UTF8") as file:
        cnt = 1  # stevec progressa
        for line in file:
            url = "https://okusno.je" + line.rstrip()
            filename = line.rstrip().removeprefix("/recept/") + ".html"
            # preverimo ce ta datoteka ze obstaja in ce, jo preberemo iz diska namesto da po nepotrebnem posiljamo request
            if os.path.exists(RECEPTI_HTML_PREFIX + filename) == False:
                page = requests.get(url, timeout=GET_TIMEOUT)
                f = open(RECEPTI_HTML_PREFIX + filename, "w")
                f.write(page.text)
                f.close()
            html_doc = open(RECEPTI_HTML_PREFIX + filename, "rb").read()
            soup = BeautifulSoup(html_doc, "html.parser")
            # sparsamo recept, skupne lasntosti zapisemo v skupen csv, sestavine pa v lastno datoteko
            recept_skupno(soup)
            recept_sestavine(soup)
            # sprintej progress
            print("[" + str((cnt/1000) * 100) + "%]")
            cnt += 1
            # spi za nekaj sekund
            time.sleep(r.randrange(1, 3))
            if cnt > 10:
                break


def main():
    if os.path.exists("data/" + RECEPTI_URLS) == False:
        get_recepti_urls()
    recepti_parser()


main()
