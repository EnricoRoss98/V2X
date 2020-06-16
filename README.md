### `Autonomous Intersection Management in SUMO traffic simulator`
#### achieved with Python and TraCI libraries 
# 

I vari protocolli sono divisi per versioni e li si possono trovare come diverso branch.

Questa repository contiene tutte le versioni dei protocolli basati su controllo della route di ogni veicolo (v1.x) e 
basati su suddivisione matriciale dell'incrocio (v2.x).

#
#### A proposito della versione 2.x
Prima di eseguire la simulazione principale, il BatchExe richiama l'esecuzione dello script Traiettorie, che genera
un'auto per ogni rotta disponibile (escludendo le rotte di auto che girano a destra) e analizza il percorso dell'auto
segnando all'interno di una matrice tutte le celle occupate da ogni rotta.

Tale matrice viene poi trasferita alla simulazione principale in modo da permettere all'algoritmo di conoscere in anticipo
le celle che ogni auto andrà ad occupare.

Le variabili di simulazione sono settate in BatchExe. Va successivamente eseguito il codice di BatchExe.py e al termine 
restituirà all’interno della cartella di Output i file di output generati.
