import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
import random as r
import time
import utility as ut
import paths as p


# Dobimo url naslove prvih 1000 receptov


def get_recepti_urls():
    print("Parsam url-je receptov:")
    f = open(p.URLS_PATH, "x")
    # Loopamo cez prvih 50 strani (vsaka stran ima po 20 receptov), da dobimo url naslove vseh receptov
    recepti_iskanje_url = "https://okusno.je/iskanje?t=recipe&sort=score&p="
    for i in range(1, 51):
        page = requests.get(recepti_iskanje_url + str(i), timeout=ut.GET_TIMEOUT)
        soup = BeautifulSoup(page.content, "html.parser")
        for a in soup.find_all("a", href=True):
            if str(a["href"]).startswith("/recept/"):
                f.write(a["href"])
                f.write("\n")
        # sprintej progress
        print("[" + str((i / 50) * 100) + "%]")
        # spi za nekaj sekund
        time.sleep(r.randrange(1, 3))
    f.close()


def get_stevilo_oseb(soup):
    stevilo_oseb = 1
    for span in soup.find_all("span"):
        if span.text == "Sestavine za":
            sp = str(span.parent).split()
            for i in sp:
                if "placeholder=" in i:
                    stevilo_oseb = int(
                        i.removeprefix('placeholder="').removesuffix('"')
                    )
                    return stevilo_oseb
    return stevilo_oseb


# doloci skupne lastnosti vseh receptov in jih zapise v skupen csv
def recept_skupno(soup, filename):
    f = open(p.RECEPTI_PATH, "a")  # odpremo skupen csv file
    # najdemo ime jedi
    ime = soup.find(
        "h1",
        {
            "class": "font-bold text-secondary dark:text-white text-20 md:text-28 leading-normal pt-0 p-16 md:pb-0 md:p-32 pb-0 bg-white dark:bg-slate-800 rounded-t-lg"
        },
    ).text
    # Najdi avtorja
    avtor = "Brez"
    for a in soup.find_all("a", href=True):
        # print(a)
        if "avtor" in str(a):
            avtor = a.text
            break
    # Dolzina priprave + kuhanja
    cas_priprave = 9999  # error values
    cas_kuhanja = 9999
    skupen_cas = 9999
    for span in soup.find_all("span"):
        if span.text == "PRIPRAVA":
            text_priprava = str(span.parent.text).split()
            # convertej ure + minute v minute
            if text_priprava[2] == "min":
                cas_priprave = int(text_priprava[1])
            else:
                cas_priprave = int(text_priprava[1]) * 60 + int(text_priprava[3])
        if span.text == "KUHANJE":
            text_kuhanje = str(span.parent.text).split()
            # enako za cas kuhanja
            if text_kuhanje[2] == "min":
                cas_kuhanja = int(text_kuhanje[1])
            else:
                cas_kuhanja = int(text_kuhanje[1]) * 60 + int(text_kuhanje[3])

    skupen_cas = min(cas_priprave + cas_kuhanja, 9999)

    # dolzino navodil (proxy za tezavnost)
    dolzina_navodil = 0
    for div in soup.find_all(
        "div", {"class": "flex relative p-16 transition hover:bg-[rgba(0,0,0,.02)]"}
    ):
        dolzina_navodil += len(str(div.text))
    # st oseb
    st_oseb = get_stevilo_oseb(soup)
    # dobimo se hranilne snovi in zapisemo v csv
    arr = [ime, avtor, cas_priprave, cas_kuhanja, skupen_cas, dolzina_navodil, st_oseb]
    arr += recept_hranilne(soup)
    arr.append(filename)
    f.write(ut.arr_to_csv(arr))
    f.close()


# doloci sestavine recepta in jih zapise v lastno datoteko
def recept_sestavine(soup, filename):
    f = open(p.SESTAVINE_PREFIX + filename, "w")
    f.write("Ime sestavine,Kolicina,Enota\n")
    # najprej ugotovimo za koliko oseb je recept
    stevilo_oseb = get_stevilo_oseb(soup)

    # nato gremo cez vse sestavine in popravimo kolicine glede na stevilo oseb
    for div in soup.find_all(
        "div", {"class": "w-2/3 md:4/5 lg:w-2/3 p-8 leading-normal flex items-center"}
    ):
        ime_sestavine = div.string
        enota = "kos"
        # obcasno se zgodi da sestavine nima enote (v tem primeru defaultamo na 1)
        if "ingredientQuantity" in str(div.parent):
            c = div.parent.find("span", {"class", "ingredientQuantity"})
            kolicina = float(c.string) / stevilo_oseb
            # najdemo enoto, ce obstaja
            if "<span>" in str(c.parent):
                for t in c.parent.find_all("span", class_=None):
                    enota_tmp = (
                        str(t).removeprefix("<span>").removesuffix("</span>").strip()
                    )
                    # enote standariziramo na g in l
                    enota, kolicina = ut.pretvori_enote(enota_tmp, enota, kolicina)
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
    csv = open(p.RECEPTI_PATH, "w")
    csv.write(
        "Ime jedi,Avtor,Cas priprave,Cas kuhanja,Skupen cas,Dolzina navodil,Stevilo oseb,Energijska vrednost,Beljakovine,Ogljikovi hidrati,Mascobe,Vlaknine,Vitamin D,CSV\n"
    )
    csv.close()
    data_in = open(p.URLS_PATH, encoding="UTF8")
    cnt = 1  # stevec progressa
    for line in data_in:
        url = "https://okusno.je" + line.rstrip()
        filename = line.rstrip().removeprefix("/recept/")
        try:
            ut.get_spletno_stran(url, p.RECEPTI_HTML_PREFIX + filename + ".html")
        except:  # error handling ce ne moremo dobiti strani
            cnt += 1
            print("[SKIPPED]")
            continue
        html_doc = open(p.RECEPTI_HTML_PREFIX + filename + ".html", "rb").read()
        soup = BeautifulSoup(html_doc, "html.parser")
        # sparsamo recept, skupne lasntosti zapisemo v skupen csv, sestavine/hranilne vrednosti pa v lastne datoteke
        ime = recept_skupno(soup, filename)
        recept_sestavine(soup, filename + ".csv")
        # sprintej progress
        print("[" + str((cnt / 1000) * 100) + "%]")
        cnt += 1


def main():
    if os.path.exists(p.URLS_PATH) == False:
        get_recepti_urls()
    recepti_parser()


main()
