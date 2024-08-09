# Poceni Pythonska Pojedina

Analizirali bomo prvih 1000 jedi pridobljenih s spletne strani [Okusno.Je](https://okusno.je/), ter ugotovili cenovno najugodnej[sh]o s pomo[ch]jo podatkov, pridobljenih z [Mercatorjeve spletne trgovine](https://www.mercatoronline.si/sl/search). Primerjali bomo zahtevnost kuhe, hranilno vrednost obrokov ter njihovo cenovno ugodnost. 


## Navodila za uporabo

Privzemam da se nahajate v Linux ali Unix okolju ter imate nalo[zh]ena sprejemljivo novo verzijo Pythona in pa `git`. Najprej klonirajte repozitorij, se premaknite vanj ter po [zh]elji ustvarite ustrezno virtualno okolje:
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
* `wordcloud`

Za scrapanje in analizo sta na volji dve python datoteki, in sicer
`mercator_scraper.py` in pa `okusno_scraper.py`. Kot imeni navajajo sta namenjeni obdelavi mercatorjeve spletne strani in pa okusno.je.
Datoteki lahko po[zh]enete s:
```
python mercator_scraper.py
python okusno_scraper.py
```

Ti bosta pobrali spletne strani, jih obdelali ter shranili v `data` direktorij. Lokacijo shrambe je mogo[ch]e nastaviti preko
spremenljivk na vrhu `mercator_scraper.py` oz. `okusno_scraper.py`. Vse poti naj bodo relativno glede na vrh direktorija tega projekta.

### Generiranje sinteze

V `analiza.ipynb` je podana python skripta za generiranje cen, natan[ch]neje datoteke `cene.csv`. Ker je le-ta dokaj po[ch]asna (na avtorjevem ra[ch]unalnika traja ~10 min), je priporo[ch]ena uporaba C++ verzije te skripte (ki na avtorjevem ra[ch]unalniku zaklju[ch]i izvajanje v ~14s), na voljo v `sinteza.cpp`. Dependencijev nima, potrebna je le uporaba C++ compilerja, ki podpira vsaj C++17. S `gcc`-jem je postopek slede[ch] (privzamemo da smo na vrhu direktorija tega projekta):

```
g++ --std=c++17 -O3 -s sinteza.cpp -o sinteza 
./sinteza
```

[Ch] ste slu[ch]ajno premikali ostale CSV-je na druge lokacije, bo treba popraviti deklaracije spremenljivk `out_path`, `recepti_path`, `izdelki_path` in `sestavine_path`, da odra[zh]ajo nove lokacije. Priporo[ch]am, da ohranite privzete vrednosti. 

## Analiza 

Analizo podatkov pridobljenih 4.8.2024 je na voljo v `analiza.ipynb`. Priporo[ch]ena je uporaba programa, namenjenega ogledu Jupyter Notebook datotek. Ogled je mo[zh]en tudi preko Githuba. 

Analiza obsega primerjavo receptov med sabo (hranilne vrednosti, kompleksnost, ipd.), Mercatorjevih izdelkov med sabo (povpre[ch]na cena, po kategoriji, ipd.) ter skupna *sinteza*, v kateri izra[ch]unamo cenovno ugodnost jedi glede na Mercatorjeve cene ter jih ponovmo primerjamo med sabo s temi dodatnimi informacijami.

## Licensa

Projekt je licensiran pod GPL-3.0. 
