# Versione 1.3

Vengono controllate le traiettorie all’interno dell’incrocio di ogni veicolo, se compatibile con l’attuale “situazione” 
di attraversata allora lo faccio passare insieme. Il codice non guarda più ad una coda di arrivo, ma vede tra le prime 
della coda di ogni corsia se c’è qualcuno che può passare senza interferire con le traiettorie altrui. 
Le due condizioni di passaggio in completa sicurezza sono:
- veicolo proveniente da una corsia o corsia opposta che deve girare a destra o andare diritto
- veicolo proveniente da una corsia o da quella opposta che deve girare a sinistra

Quando non ci non più auto “capofila” che rispettano l’attuale condizione di passaggio e l’incrocio si libera, si parte 
con l’altra condizione di passaggio.

