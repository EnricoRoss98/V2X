# Versione 1.6

Nella Versione 1.6 è stato migliorato l’algoritmo della Versione 1.5 permettendo il passaggio senza attese e 
rallentamenti per tutti quei veicoli sulla corsia più a destra, che quindi dovranno svoltare esclusivamente a destra, 
poiché essi non intralciano il cammino di alcuna delle altre rotte. Esse non vanno a incrementare il contatore dei 
passaggi né influiscono sulla variabile “semaforo” occupato, il sistema effettuerà le proprie valutazioni sul permesso 
o meno di passaggio solo sulle altre auto. Vi è stato aggiunto un ulteriore controllo che rileva se tutte le auto in 
passaggio stanno girando a destra allora fa partire la prima auto nella coda delle attese, così da permettere lo sblocco
 della situazione e l’avanzamento con una nuova condizione di passaggio.

Poco prima di entrare nell’incrocio, per le auto che girano a destra viene rallentata fino ad un valore pari a metà 
della velocità massima e poi all’uscita viene fatta accelerare nuovamente al valore massimo impostato. Questa condizione
 è stata poi implementata anche sulle successive versioni.