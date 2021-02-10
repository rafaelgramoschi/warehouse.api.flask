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