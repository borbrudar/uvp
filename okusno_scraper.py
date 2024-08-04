import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
import random as r
import time
import utility as ut


# Imena datotek
RECEPTI_URLS = "recepti_urls"
RECEPTI = "recepti.csv"
RECEPTI_HTML_PREFIX = "data/recepti_html/"
RECEPTI_SESTAVINE_PREFIX = "data/recepti_sestavine/"

# Dobimo url naslove prvih 1000 receptov

def get_recepti_urls():
    print("Parsam url-je receptov:")
    f = open("data/" + RECEPTI_URLS, "x")
    # Loopamo cez prvih 50 strani (vsaka stran ima po 20 receptov), da dobimo url naslove vseh receptov
    recepti_iskanje_url = "https://okusno.je/iskanje?t=recipe&sort=score&p="
    for i in range(1, 51):
        page = requests.get(recepti_iskanje_url + str(i), timeout=ut.GET_TIMEOUT)
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

    arr = [avtor, tezavnost, cas_priprave,
           cas_kuhanja, skupen_cas, dolzina_navodil]
    arr += recept_hranilne(soup)
    f.write(ut.arr_to_csv(arr))
    f.close()


# doloci sestavine recepta in jih zapise v lastno datoteko
def recept_sestavine(soup, filename):
    f = open(RECEPTI_SESTAVINE_PREFIX + filename, "w")
    f.write("Ime sestavine, Kolicina, Enota\n")
    # najprej ugotovimo za koliko oseb je recept
    stevilo_oseb = 1
    for a in soup.find_all("span"):
        if a.text == "Sestavine za":
            sp = str(a.parent).split()
            for i in sp:
                if "placeholder=" in i:
                    stevilo_oseb = int(i.removeprefix(
                        "placeholder=\"").removesuffix("\""))
                    break
            break

    # nato gremo cez vse sestavine in popravimo kolicine glede na stevilo oseb
    for a in soup.find_all("div", {"class": "w-2/3 md:4/5 lg:w-2/3 p-8 leading-normal flex items-center"}):
        ime_sestavine = a.string
        enota = "kos"
        # obcasno se zgodi da sestavine nima enote (v tem primeru defaultamo na 1)
        if "ingredientQuantity" in str(a.parent):
            c = a.parent.find("span", {"class", "ingredientQuantity"})
            kolicina = float(c.string)/stevilo_oseb
            # najdemo enoto, ce obstaja
            if "<span>" in str(c.parent):
                for t in c.parent.find_all("span", class_=None):
                    enota_tmp = str(t).removeprefix(
                        "<span>").removesuffix("</span>").strip()
                    # enote standariziramo na g in l
                    enota,kolicina = ut.pretvori_enote(enota_tmp,enota,kolicina)
        else:
            kolicina = 1
        f.write(ut.arr_to_csv([ime_sestavine, kolicina, enota]))
    f.close()


# pomozna funkija, ki pridobi hranilne kolicine
def get_hranilno(hranilna, row):
    r = 0
    row = str(row)
    while row.startswith(hranilna) == False and len(row) > len(hranilna):
        row = row[1:]
    vals = row.removeprefix(hranilna).split()
    # poseben primer za ogljikove hidrate in mascobe (quirk tabele)
    for i in vals:
        try:
            if i.startswith("sladkorji"):
                i = i.removeprefix("sladkorji")
            if i.startswith("kisline"):
                i = i.removeprefix("kisline")
            r = float(i)
            break
        except ValueError:
            continue
    return r


# hranilne vrednosti na 100g jedi
def recept_hranilne(soup):
    table = soup.find("table").text
    en_vrednost = get_hranilno("Energijske vrednosti", table)
    beljakovine = get_hranilno("Beljakovine", table)
    ogl = get_hranilno("Ogljikovi", table)
    masc = get_hranilno("Maščobe", table)
    vlak = get_hranilno("Vlaknine", table)
    vitd = get_hranilno("Vitamin D", table)
    return [en_vrednost, beljakovine, ogl, masc, vlak, vitd]


# gre cez vse recepte in jih sparsa
def recepti_parser():
    print("Parsam recepte:")
    csv = open("data/" + RECEPTI, "w")
    csv.write(
        "Avtorji, Tezavnost, Cas priprave, Cas kuhanja, Skupen cas, Dolzina navodil, Energijska vrednost, Beljakovine, Ogljikovi hidrati, Mascobe, Vlaknine, Vitamin D\n")
    csv.close()
    data_in =  open("data/" + RECEPTI_URLS, encoding="UTF8")
    cnt = 1  # stevec progressa
    for line in data_in:
        url = "https://okusno.je" + line.rstrip()
        filename = line.rstrip().removeprefix("/recept/")
        try:
            ut.get_spletno_stran(url,RECEPTI_HTML_PREFIX + filename + ".html")
        except:
            cnt += 1
            print("[SKIPPED]")
            continue        
        html_doc = open(RECEPTI_HTML_PREFIX +
                        filename + ".html", "rb").read()
        soup = BeautifulSoup(html_doc, "html.parser")
        # sparsamo recept, skupne lasntosti zapisemo v skupen csv, sestavine/hranilne vrednosti pa v lastne datoteke
        recept_skupno(soup)
        recept_sestavine(soup, filename + ".csv")
        # sprintej progress
        print("[" + str((cnt/1000) * 100) + "%]")
        cnt += 1

def main():
    if os.path.exists("data/" + RECEPTI_URLS) == False:
        get_recepti_urls()
    recepti_parser()


main()
