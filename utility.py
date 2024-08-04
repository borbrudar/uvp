import requests
import time,os,random as r

# Timeout za gettanje strani
GET_TIMEOUT = 10

# helper funkcija za pomoc pri zapisu v csv
def arr_to_csv(arr):
    r = str()
    for i in arr:
        r += str(i).replace(",", ";")  # robustnost
        r += ","
    r = r.removesuffix(",") + "\n"
    return r

def pretvori_enote(enota_tmp,enota,kolicina):
    # enote standariziramo na g in l
    if enota_tmp == "g":
        enota = "g"
    elif enota_tmp == "l":
        enota = "l"
    elif enota_tmp == "kg":
        enota = "g"
        kolicina *= 1000
    elif enota_tmp == "mg":
        enota = "g"
        kolicina /= 1000
    elif enota_tmp == "dl":
        enota = "l"
        kolicina /= 10
    elif enota_tmp == "ml":
        enota = "l"
        kolicina /= 1000
    return (enota,kolicina)
        
        
def get_spletno_stran(url,path):
    # preverimo ce ta datoteka ze obstaja in ce, jo preberemo iz diska namesto da po nepotrebnem posiljamo request 
    if os.path.exists(path): return
    page = requests.get(url, timeout=GET_TIMEOUT)
    if page.ok == False: 
        print("Error getting page")
        print(url)
        raise Exception("BAD URL")
    f = open(path, "w", encoding="UTF8")
    f.write(page.text)
    f.close()
    # spi za nekaj sekund
    time.sleep(r.randrange(3, 5))