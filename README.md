# Versione 2.3
In questa versione si è voluto risolvere il problema che le 8 celle occupate sono tutte contate attorno al centro della 
vettura, ma nel caso di una suddivisione di 20 celle/lato dell’incrocio, la coprono solo di larghezza e non di lunghezza
, servirebbe in questo caso un’altra cella di lunghezza per il muso e un’altra per il retro dell’auto.
Nella “simulazione 0” vengono salvate, oltre alle coordinate della cella e i metri di distanza percorsa dallo stop, 
anche l’angolo medio con la quale l’auto attraversa tale cella.
Nella simulazione principale è stata aggiunta una funzione per il calcolo delle celle occupate (centrate nella cella 
in cui è stato campionato l’attraversamento) data l’angolazione dell’auto rilevata in quella cella dalla “simulazione 
0”: essa è richiamata dalle funzioni di controllo e salvataggio dei timestep all’interno della struttura dati 
dell’incrocio in modo da conoscere con esattezza le effettive celle attraversate dall’auto nell’intorno della cella 
considerata.

Successivamente spiegati rapidamente i passaggi svolti all’interno della funzione:
- si considera l’auto come un rettangolo di base ed altezza fissata (sono due ulteriori variabili da modificare oltre 
al tempo di sicurezza quando si decide di variare il numero di celle lato di suddivisione dell’incrocio);
- dopo aver trovato i vertici di tale rettangolo si fanno ruotare attorno ad un fulcro 
posizionato al centro del rettangolo e si calcolano le coordinate dei vertici ruotati;
- a questo punto trovo le 4 rette che delimitano il mio rettangolo mediante formula della retta passante per due punti;
- infine controllo per ogni cella, e per ognuno dei suoi vertici, se tale punto ricade all’interno del mio rettangolo, 
se almeno un vertice ricade all’interno allora quella cella (o una parte di essa) verrà toccata dall’attraversamento 
dall’auto.


