# Poceni Pythonska Pojedina

Analizirali bomo prvih 1000 jedi pridobljenih s spletne strani [Okusno.Je](https://okusno.je/), ter ugotovili cenovno najugodnejše s pomočjo podatkov, pridobljenih z [Mercatorjeve spletne trgovine](https://www.mercatoronline.si/sl/search). Primerjali bomo zahtevnost kuhe, hranilno vrednost obrokov ter njihovo cenovno ugodnost. 


## Navodila za uporabo

Privzemam da se nahajate v Linux ali Unix okolju ter imate naložena sprejemljivo novo verzijo Pythona in pa `git`. Najprej klonirajte repozitorij, se premaknite vanj ter po želji ustvarite virtualno okolje:

```
git clone https://github.com/borbrudar/uvp.git
cd uvp
python -m venv env
source env/bin/activate
```

Potrebne pakete lahko naložite z uporabo `pip install -r requirements.txt`.
Če jih želite naložiti ročno, boste potrebovali:
* `requests`
* `beautifulsoup4`
* `pandas`
* `numpy`
* `matplotlib`
* `matplotlib-inline`
* `seaborn` 
* `wordcloud`

Za scrapanje spletnih strani sta na volji dve python datoteki, in sicer `mercator_scraper.py` in pa `okusno_scraper.py`. Kot imeni navajajo sta namenjeni obdelavi Mercatorjeve spletne strani in pa Okusno.Je.
Datoteki lahko poženete s:
```
python mercator_scraper.py
python okusno_scraper.py
```

Ti bosta pobrali spletne strani, jih obdelali ter shranili v `data` direktorij. Poleg tega bosta generirali `csv` datoteke iz podatkov, ki jih pridobita.Lokacijo shrambe je mogoče nastaviti preko spremenljivk v `paths.py`. Vse poti naj bodo relativno glede na vrh direktorija tega projekta. Opomba: sprememba poti v `paths.py` ne bo vplivala na poti v `sinteza.cpp`.

### Generiranje sinteze

V `analiza.ipynb` je podana python skripta za generiranje cen, natančneje datoteke `cene.csv`. Ker je le-ta dokaj počasna (na avtorjevem računalnika traja ~10 min), je priporočena uporaba C++ verzije te skripte (ta avtorjevem računalniku zaključi izvajanje v ~14s), na voljo v `sinteza.cpp`. Dependencijev nima, potrebna je le uporaba C++ compilerja, ki podpira vsaj C++17. S `gcc`-jem je ukaz sledeč (privzamemo da smo na vrhu direktorija tega projekta):

```
g++ --std=c++17 -O3 -s sinteza.cpp -o sinteza 
./sinteza
```

Če ste slučajno premikali ostale CSV-je na druge lokacije, bo treba popraviti deklaracije spremenljivk `out_path`, `recepti_path`, `izdelki_path` in `sestavine_path`, da odražajo nove lokacije. Zato priporočam, da ohranite privzete vrednosti. 

## Analiza 

Analiza podatkov pridobljenih 4.8.2024 je na voljo v `analiza.ipynb`. Priporočena je uporaba programa, namenjenega ogledu Jupyter Notebook datotek. Ogled je možen tudi preko Githuba. 

Analiza obsega primerjavo receptov med sabo (hranilne vrednosti, kompleksnost, ipd.), Mercatorjevih izdelkov med sabo (povprečna cena, po kategoriji, ipd.) ter skupna *sinteza*, v kateri izračunamo cenovno ugodnost jedi glede na Mercatorjeve cene ter jih ponovmo primerjamo med sabo s temi dodatnimi informacijami.

## Licensa

Projekt je licensiran pod GPL-3.0. 
