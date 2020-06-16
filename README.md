### `Autonomous Intersection Management in SUMO traffic simulator`
### achieved with Python and TraCI libraries 
# 

I vari protocolli sono divisi per versioni e li si possono trovare come diverso branch.

Questa repository contiene tutte le versioni dei protocolli basati su controllo della route di ogni veicolo (v1.x) e 
basati su suddivisione matriciale dell'incrocio (v2.x).

#
### A proposito della versione 2.x
Prima di eseguire la simulazione principale, il BatchExe richiama l'esecuzione dello script Traiettorie, che genera
un'auto per ogni rotta disponibile (escludendo le rotte di auto che girano a destra) e analizza il percorso dell'auto
segnando all'interno di una matrice tutte le celle occupate da ogni rotta.

Tale matrice viene poi trasferita alla simulazione principale in modo da permettere all'algoritmo di conoscere in anticipo
le celle che ogni auto andrà ad occupare.

Le variabili di simulazione sono settate in BatchExe. Va successivamente eseguito il codice di BatchExe.py e al termine 
restituirà all’interno della cartella di Output i file di output generati.

#
### Lista Branch principali
#### Incrocio regolato da semaforo
- 1.0.2 -> per la generazione di tutti gli output + consumo EV
- 1.0.3 -> per la generazione output di consumo per il termico

#### Primo approccio:
incrocio regolato da semaforo immaginario che fa avanzare le auto per condizioni di passaggio
- 1.6.2 -> per la generazione di tutti gli output + consumo EV
- 1.6.3 -> per la generazione output di consumo per il termico

#### Secondo approccio:
suddivisione matriciale dell'incrocio, passaggio regolato a seconda dei tempi di presunto arrivo in cella
- 2.3.2 -> per la generazione di tutti gli output + consumo EV
- 2.3.3 -> per la generazione output di consumo per il termico
