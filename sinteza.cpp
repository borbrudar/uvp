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

map<string,vector<string>> cache; // shranmo ze splittane stringe (veckrat iste stringe splittamo tk da se bolj splaca)

// splitta po praznih prostorih in cacha
vector<string> split(const string&in){
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
            int cnt = 0;
            for(size_t k = 0; k < min(i.size(),j.size()); k++){
                if(i[k] != j[k]) break;
                cnt++;
            }
            if(cnt > 3) r += cnt*cnt;
        }
    return r;
}


int main(){
    //ios_base::sync_with_stdio(0);cin.tie(0); // hitrejsi io
    // poti 
    string out_path = string(filesystem::current_path()) + "/data/cene.csv",
    recepti_path = string(filesystem::current_path()) + "/data/recepti.csv",
    izdelki_path = string(filesystem::current_path()) + "/data/izdelki.csv";

    // cachamo izdelke
    ifstream iz(izdelki_path);
    string line;
    getline(iz,line);
    vector<vector<string>> izdelki;
    while(getline(iz,line))
        izdelki.push_back(csvline_to_vector(line));

    //freopen("data/cene.csv","w", stdout); // zvezemo output file na stdout
    auto f = ofstream(out_path);
    f << "Ime jedi,Cena,Promocijska cena\n";
    constexpr double default_cena = 1.0; //default parameter ce ne najdemo nobenega podobnega izdelka
    // za vsako jed gremo cez vse sestavine in jim dolocimo ceno
    ifstream recepti(recepti_path);
    getline(recepti,line); // prva vrstica ni uporabna
    while(getline(recepti,line)){
        string ime_jedi,csv;
        // dobi prvi element csvja
        auto get_first = [](const string&line, string&s){ 
            for(const auto&c: line)
                if(c == ',') break;
                else s += c;
        };
        
        // dobimo ime jedi (prvi element csvja) in ime csv datoteke za recepte (zadnji element, zato reversamo)
        get_first(line,ime_jedi);
        reverse(line.begin(),line.end());
        get_first(line,csv);
        reverse(csv.begin(),csv.end());

        // nastavimo akumulatorske spremenljivke
        double skupna_cena = 0.0;
        double skupna_prom_cena = 0.0;

        // gremo cez use sestavine za ta recept
        string sestavine_path = string(filesystem::current_path()) + "/data/recepti_sestavine/" + csv +".csv";
        ifstream sestavine(sestavine_path);
        string sestavine_line;
        getline(sestavine, sestavine_line); // prvo vrstico spet ignoramo
        while(getline(sestavine,sestavine_line)){
            string ime_sestavine,enota;
            double kolicina;
            // parsamo csv da dobimo podatke za to sestavino
            auto tmp = csvline_to_vector(sestavine_line);
            ime_sestavine = move(tmp[0]);
            kolicina = stod(move(tmp[1]));
            enota = move(tmp[2]);

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
                // prioriteta je najblizji zadetek, ce je vec enakih gledamo najnizjo ceno
                auto cena_izdelka = stod(izdelek[2]);
                auto prom_cena_izdelka = stod(izdelek[3]);
                if(sim > best_match) best_cena = cena_izdelka * kolicina;
                else best_cena = min(best_cena, cena_izdelka * kolicina);
                
                // enako za prom. ceno
                // ce je promocijska cena 0.0, ni promocije
                if(sim > best_match) best_prom_cena = prom_cena_izdelka * kolicina;
                else best_prom_cena = min(best_prom_cena, (prom_cena_izdelka == 0.0 ? cena_izdelka : prom_cena_izdelka) * kolicina);    
            }
            
            // povecamo vrednosti
            skupna_cena += best_cena;
            skupna_prom_cena += best_prom_cena;

        }
        // shranimo ceni za to jed v csv
        f<<ime_jedi<<","<<skupna_cena<<","<<skupna_prom_cena<<"\n";
        //cout<<"test"<<endl;
        //f.write(ime_jedi + "," + to_string(skupna_cena)+  "," + to_string(skupna_prom_cena)+"\n");
    }

}