from bs4 import BeautifulSoup
import utility as ut
import paths as p


def parse_izdelke(soup):
    csv = open(p.IZDELKI_PATH, "a")
    # najdemo vse produkte
    for izdelek in soup.find_all(
        "ajax-add-to-cart",
        {
            "class": "custom-element ajax-add-to-cart expand-add-to-cart__ajax-add-to-cart"
        },
    ):
        izdelek = izdelek.find("button")
        # zelene lastnosti so conveniently atributi istega elementa
        cena = izdelek["data-price"]
        znamka = izdelek["data-brand"]
        akcija = izdelek["data-promo-price"]
        kolicina = float(izdelek["data-quantity"])
        ime = (
            izdelek["data-name"].strip().split(",")[0]
        )  # ponavadi poleg imena dobimo se znamko in/ali kolicino
        enota = "kos"
        # last je zadnji element imena (enota, ce je)
        last = str(izdelek["data-name"].strip().split(",")[-1]).split()
        if len(last) > 0:
            last = last[-1]
        else:
            last = "kos"
        enota, kolicina = ut.pretvori_enote(last, enota, kolicina)
        # dobimo se kategorijo
        kategorija = izdelek["data-formatted-categories"].split(";")[
            -1
        ]  # hevristicno locimo
        # appendamo izdelke v csv datoteko
        csv.write(
            ut.arr_to_csv([ime, znamka, cena, akcija,
                          kolicina, enota, kategorija])
        )


def main():
    # sparsamo vse izdelke na voljo v mercatorjevi spletni trgovini
    base_url = "https://www.mercatoronline.si/sl/search?ipp=75&page="
    cnt = 1
    csv = open(p.IZDELKI_PATH, "w")
    csv.write("Ime izdelka,Znamka,Cena,Promocijska cena,Kolicina,Enota,Kategorija\n")
    csv.close()
    print("Mercator parse:")
    for i in range(1, 207):  # 206 strani je ob casu scrapanja
        filename = "izdelki" + str(i) + ".html"
        ut.get_spletno_stran(
            base_url + str(i), p.IZDELKI_HTML_PREFIX + filename)
        html_doc = open(p.IZDELKI_HTML_PREFIX + filename, "rb").read()
        soup = BeautifulSoup(html_doc, "html.parser")
        parse_izdelke(soup)
        # sprintej progress
        print("[" + "{:.2f}".format((cnt / 206) * 100) + "%]")
        cnt += 1


main()
