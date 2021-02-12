1. Fare un database "test".
sudo su - postgres
psql
create database test;

2. Fare un virtual environment
sudo apt-get install python3-pip
pip3 install virtualenv
python3 -m venv venv
source venv/bin/activate
pip3 install -r req.txt --no-index

3. Inizializzare le tabelle:
python3 manage.py db init
python3 manage.py db migrate
python3 manage.py db upgrade

4. Inserire manualmente un utente superuser specificando alla colonna is_admin=True

insert into users(public_id,username,password,is_admin)
values(
'42023454-ff29-41b8-bb53-866632dbb215',
'superuser',
'sha256$jZjo8bo4$8da964de32888df79efe4bc19f05e0f19ead4c9577a07b2386e52de2a8ab1ba4',
True);

5. Eseguire l'applicazione
python3 flask_app.py

6. Esempi di lancio curl

curl http://localhost:5000/login -u "superuser:password"

curl http://localhost:5000/signup/user -d '{"username":"user3","password":"password","org_id":"3","user_access_level":"1"}' -H "x-access-token:eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwdWJsaWNfaWQiOiJhYzI2ZThiOC1kZDBlLTQ0MjMtYTkwOS1kZTE1ZGEwMWU2ZGYiLCJleHAiOjE2MTI5ODE4MTl9.Becr-QbiSLNP5wSbhGtb6IEMeI7M756aDOEFtPDMZiM"

curl http://localhost:5000/warehouse -H "x-access-token:eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwdWJsaWNfaWQiOiJhYzI2ZThiOC1kZDBlLTQ0MjMtYTkwOS1kZTE1ZGEwMWU2ZGYiLCJleHAiOjE2MTI5MTIwNjR9.gv_4Itve10MHW_ZUe_1bFMxLjJvPFsvQofxP0uVpV_E"



# Esercitazione

## Scopo

Si implementi un backend RESTful che modelli la gestione di un magazzino che affitta spazio a varie organizzazioni.

Il magazzino contiene il materiale di organizzazioni indipendenti, organizzato come segue:

- il magazzino è diviso in unità
- ogni unità è interamente di competenza di una singola organizzazione
- ogni unità contiene una o più scatole fino ad un limite impostato su ciascuna unità

Esiste un utente amministratore del sistema (superutente); solamente questo utente ha facoltà di creare unità e di assegnarle ad un'organizzazione.

L'amministratore ha inoltre pieni poteri su tutte le entità del sistema, indipendentemente dall'organizzazione a cui appartengono.

Ogni altro utente del sistema fa parte di un'organizzazione, ed ha accesso in lettura e scrittura esclusivamente alle strutture di contenimento (ed al loro contenuto) di competenza della propria organizzazione.

Le API devono permettere di:

- listing delle unità a cui l'utente ha accesso
- listing delle scatole a cui l'utente ha accesso
- creare / cancellare scatole all'interno di un'unità fino al limite di scatole

## Consegna

La consegna dovrà avvenire preferibilmente tramite repository git privato (possiamo fornirne uno dedicato con accessi per il candidato),
e dovrà contenere tutto il necessario per fare il setup e la compilazione dell'applicazione (compresa la dichiarazione delle dipendenze),
ed eventualmente una breve guida di come fare il setup / eseguire l'applicazione, qualora fossero necessarie azioni manuali particolari.

## Implementazione

Fornire l'implementazione di:

* API REST in lettura e scrittura per gli utenti non admin
* Documentazione sotto forma di dichiarazione di cosa deve essere documentato, in che forma (docstrings o documentazione in prosa) e quali strumenti si andrebbero ad usare per la gestione della documentazione, con alcuni esempi di documentazione di un model ed un metodo
* Interfaccia admin per il solo superutente

### Informazioni sull'implementazione

Le API possono essere implementate con la tecnologia backend che si conosce meglio

Il formato degli URL, il formato delle richieste, i verbi ed i codici HTTP e il formato delle risposte, sono a discrezione.


## Elementi opzionali

- implementazione di interfaccia REST per utente superadmin
- distinzione degli utenti di un'organizzazione in base a privilegi (es. utenti in sola lettura da un determinato livello di contenimento in giù)
- limiti di capacità dei vari livelli di contenimento
- signup degli utenti
- interfaccia openapi e/o swagger