# Versione 2.2

Tale versione si basa sempre sulla suddivisione matriciale dell’incrocio, ma al posto di popolare le celle della matrice
 con una variabile booleana T/F di occupazione o meno della cella, ora le celle contengono un vettore popolato da tutti 
 i valori di timestep di presunta futura occupazione della cella. Tali valori sono calcolati mediante funzione che si 
 basa sulla velocità iniziale dell’auto, quella al momento della richiesta, la velocità finale, cioè la velocità a 
 regime dell’auto, la sua accelerazione per raggiungere la velocità finale, e la sua distanza dalla cella. 

È stato modificato lo script Traiettorie.py, ora ritorna una struttura dati complessa contenente: le coordinate delle 
celle occupate, e la distanza percorsa dall’auto dall’entrata dell’incrocio fino a tale cella (utilizzata nella formula 
sopra indicata), questo per ogni rotta di possibile attraversamento dell’incrocio (a meno delle auto che girano a 
destra). Il calcolo della distanza si basa sulla differenza tra timestep corrente e quello di entrata nell’incrocio, 
moltiplicato per la velocità di crociera delle auto (in questa simulazione, le auto non rallentano mai, vengono infatti
 generate molto distanziate tra di loro). Se un’auto viene campionata più volte sulla stessa cella, lo script salva 
 tutte le distanze in un’array, per poi farci una media e salvare nella struttura dati di ritorno un valore unico di 
 riferimento.
 
La funzione sopra citata per il calcolo del tempo di presunto arrivo nella cella viene richiamata al momento di 
avvicinamento dell’auto all’incrocio, precisamente a 16m da esso, quando l’auto deve decidere se tenere la velocità,
 o rallentare per arrestarsi allo stop, e calcola tutti i tempi di arrivo nelle celle che l’auto in questione 
 attraverserà durante il suo attraversamento. Se tutti i tempi calcolati, sono compatibili con i tempi già inseriti 
 all’interno del vettore delle celle attraversate, tenendo conto di un ulteriore margine di sicurezza (parametro in 
 secondi impostato in fase di configurazione delle simulazioni), allora i vettori di cella vengono scritti e l’auto 
 inizia la sua attraversata.
 
 L’algoritmo, scorre costantemente le auto in arrivo o quelle prime di ogni coda per testare la loro futura compatibilità
 con le auto in attraversamento.
 
Ogni 10 step, l’algoritmo controlla su tutte le celle della matrice se ci sono valori troppo vecchi di occupazione della
 cella, in tal caso pulisce i vettori di cella da tali valori per scorrerli più velocemente. Per il controllo si tiene 
 conto del margine di sicurezza impostato per evitare che si tolgano valori ancora utili.