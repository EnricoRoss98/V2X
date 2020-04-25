### `Autonomous Intersection Management in SUMO traffic simulator`
#### achieved with Python and TraCI libraries 
# 

I vari protocolli sono divisi per versioni e li si possono trovare come diverso branch.

Questa repository contiene tutte le versioni dei protocolli basati su controllo della route di ogni veicolo (v1.x) e 
basati su suddivisione matriciale dell'incrocio (v2.x).
#
#### In generale
In tutte le versioni è stata implementata una gestione più realistica della accelerazione e decelerazione dei veicoli.
È stato ipotizzato un tempo di rallentamento fino al completo arresto del veicolo dai 30 Km/h in totale comodità 
(non una frenata brusca) e dopo essere risalito ai metri necessari, in questo caso 16 metri, è stata calcolata 
l’accelerazione (o decelerazione, impostati con uguale valore) equivalente per arrestare il veicolo in 16 metri a 1 m/s 
(valore di avanzamento della simulazione), risultata 0,03125 . È stato quindi inserito il valore nel file di 
configurazione rou.xml nella sezione di definizione del vType ed è stato modificato il codice in modo da iniziare il 
rallentamento del veicolo a 16 metri dall’incrocio, se non ci sono veicoli davanti, altrimenti l’auto segue la velocità 
di quella di fronte fino a quando non entra nell’incrocio, a questo punto, se l’auto non ha il permesso di passare ad 
ogni secondo viene calcolata la distanza di arresto a quella velocità, e se permette una fermata del veicolo in 
prossimità dello stop viene fatta iniziare la fase di frenata.

Le variabili di simulazione sono settate in BatchExe. Va successivamente eseguito il codice di BatchExe.py e al termine 
restituirà all’interno della cartella di Output i file di output generati.

#
#### A proposito della versione 2.x
Prima di eseguire la simulazione principale, il BatchExe richiama l'esecuzione dello script Traiettorie, che genera
un'auto per ogni rotta disponibile (escludendo le rotte di auto che girano a destra) e analizza il percorso dell'auto
segnando all'interno di una matrice tutte le celle occupate da ogni rotta.

Tale matrice viene poi trasferita alla simulazione principale in modo da permettere all'algoritmo di conoscere in anticipo
le celle che ogni auto andrà ad occupare.

Vengono poi restituiti 5 file all'interno della cartella Output di ogni branch: code, ferme, tempo, vel_med e t_in_coda.

