#include <bits/stdc++.h>

using namespace std;

// parsa csv, vrne vektor stringov 
vector<string> csvline_to_vector(const string&s){
    vector<string> tmp = {""};
    for(const auto &u: s){
        if(u == ',') tmp.push_back(string());
        else tmp.back() += u;
    }
    return move(tmp);
}

// unordered je v tem primeru hitrejsa
unordered_map<string,vector<string>> cache; // shranmo ze splittane stringe (veckrat iste stringe splittamo tk da se splaca)

// splitta po praznih prostorih in cacha
vector<string>& split(const string&in){
    if(cache.count(in) != 0 || in.size() == 0) return cache[in];
    string tmp;
    for(size_t i = 0;i < in.size();i++){
        if(in[i] == ' ' ||  i == in.size() - 1){ 
            if(tmp.size() > 0) cache[in].push_back(tmp);
            tmp.clear();
        } else tmp += in[i];
    }
    return cache[in];
}

// razdeli stringe na besede in primerja podobnost besed (drugace dobimo absurdne rezultate, npr. "olivnega olja" matcha z "Hladilna torba")
// bolj podobna -> visja cifra
int similar(const string &a,const string &b){
    int r = 0;
    auto b_cache = split(b);
    for(const auto &i : split(a))
        for(const auto &j : b_cache){
            size_t k = 0;
            for(; k < min(i.size(),j.size()); k++)
                if(i[k] != j[k]) break;
            if(k > 3) r += k*k;
        }
    return r;
}


int main(){
    //ios_base::sync_with_stdio(0);cin.tie(0); // hitrejsi io
    // poti 
    const string out_path = string(filesystem::current_path()) + "/data/cene.csv",
    recepti_path = string(filesystem::current_path()) + "/data/recepti.csv",
    izdelki_path = string(filesystem::current_path()) + "/data/izdelki.csv";

    // cachamo izdelke
    ifstream iz(izdelki_path);
    string line;
    getline(iz,line);
    vector<vector<string>> izdelki; 
    izdelki.reserve(16000); // mikrooptimizacije lol
    while(getline(iz,line))
        izdelki.push_back(csvline_to_vector(line));

    // file stream za zapis cen
    auto out = ofstream(out_path);
    out << "Ime jedi,Cena,Promocijska cena\n";
    constexpr double default_cena = 1.0; //default parameter ce ne najdemo nobenega podobnega izdelka
    // za vsako jed gremo cez vse sestavine in jim dolocimo ceno
    ifstream recepti(recepti_path);
    getline(recepti,line); // prva vrstica ni uporabna
    while(getline(recepti,line)){
        // dobimo ime jedi (prvi element csvja) in ime csv datoteke za recepte(zadnji element)
        const auto tmp_ = csvline_to_vector(line);
        const string ime_jedi = move(tmp_[0]);
        const string csv = move(tmp_[12]);

        // nastavimo akumulatorske spremenljivke
        double skupna_cena = 0.0;
        double skupna_prom_cena = 0.0;

        // gremo cez use sestavine za ta recept
        const string sestavine_path = string(filesystem::current_path()) + "/data/recepti_sestavine/" + csv +".csv";
        ifstream sestavine(sestavine_path);
        string sestavine_line;
        getline(sestavine, sestavine_line); // prvo vrstico spet ignoramo
        while(getline(sestavine,sestavine_line)){
            // parsamo csv da dobimo podatke za to sestavino
            const auto tmp = csvline_to_vector(sestavine_line);
            const string ime_sestavine = move(tmp[0]);
            const double kolicina = stod(tmp[1]);
            const string enota = move(tmp[2]);

            // najdi match
            int best_match = 20; // nek default value
            double best_cena = default_cena;
            double best_prom_cena = default_cena;

            // gremo cez use izdelke
            for(const auto &izdelek : izdelki){
                if(enota != izdelek[5]) continue; // ce nista v istih enotah nadaljujemo     
                auto sim = similar(izdelek[0], ime_sestavine);
                if(sim < best_match) continue; // ugotovimo podobnost, ce je slabsa od trenutnega najboljsega nadaljujemo
                best_match = sim;
                //dobimo cene
                auto cena_izdelka = stod(izdelek[2]);
                auto prom_cena_izdelka = stod(izdelek[3]);
                // ce je promocijska cena 0.0, ni promocije
                prom_cena_izdelka = prom_cena_izdelka == 0.0 ? cena_izdelka : prom_cena_izdelka;
                // prioriteta je najblizji zadetek, ce je vec enakih gledamo najnizjo ceno
                if(sim > best_match) {
                    best_cena = cena_izdelka * kolicina;
                    best_prom_cena = prom_cena_izdelka * kolicina;
                }
                else {
                    best_cena = min(best_cena, cena_izdelka * kolicina);
                    best_prom_cena = min(best_prom_cena, prom_cena_izdelka * kolicina);    
                }
            }
            
            // povecamo vrednosti
            skupna_cena += best_cena;
            skupna_prom_cena += best_prom_cena;
        }
        // shranimo ceni za to jed v csv
        out<<ime_jedi<<","<<skupna_cena<<","<<skupna_prom_cena<<"\n";
    }
}