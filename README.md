# Poceni Pythonska Pojedina

Analizirali bomo prvih 1000 jedi pridobljenih s spletne strani okusno.je, ter ugotovili cenovno najugodnej[sh]o s pomo[ch]jo podatkov, pridobljenih z Mercatorjeve spletne trgovine. Primerjali bomo zahtevnost kuhe, hranilno vrednost obrokov ter njihovo cenovno ugodnost. 


## Navodila za uporabo

Najprej klonirajte repozitorij, se premaknite vanj ter po [zh]elji ustvarite ustrezno virtualno okolje:
```
git clone https://github.com/borbrudar/uvp.git
cd uvp
python -m venv env
source env/bin/activate
```
[Ch]e se nimate nalo[zh]enih dependicijev jih nalo[zh]te preko `pip`-a v virtualno okolje (lahko pa tudi globalno).
Potrebni so:
* `requests`
* `beautifulsoup4`
* `pandas`
* `numpy`
* `matplotlib`
* `seaborn` 

Za scrapanje in analizo sta na volji dve python datoteki, in sicer
`mercator_scraper.py` in pa `okusno_scraper.py`. Kot imeni navajajo sta namenjeni obdelavi mercatorjeve spletne strani in pa okusno.je.
Datoteki lahko po[zh]ente s:
```
python mercator_scraper.py
python okusno_scraper.py
```

Ki bosta pobrali spletne strani ter jih obdelali ter shranili v `data` direktorij. Lokacijo shrambe je mogo[ch]e nastaviti preko
spremenljivk na vrhu `mercator_scraper.py` oz. `mercator_scraper.py`

## Analiza 

Analizo podatkov vnaprej pridobljenih 4.8.2024 je na voljo v `analiza.ipynb`. Za ogled je priporo[ch]en program, namenjen ogledu
Jupyter Notebook datotek. Ogled je mo[zh]en tudi preko Githuba. 


## Licensa

Projekt je licensiran pod GPL-3.0. 
