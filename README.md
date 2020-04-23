### Autonomous Intersection Management in SUMO traffic simulator
#### achieved with Python and TraCI libraries 
# 

I vari protocolli sono divisi per versioni e li si possono trovare come diverso branch.

Questa repository contiene tutte le versioni dei protocolli basati su suddivisione matriciale dell'incrocio.

Prima di eseguire la simulazione principale, il BatchExe richiama l'esecuzione dello script Traiettorie, che genera
un'auto per ogni rotta disponibile (escludendo le rotte di auto che girano a destra) e analizza il percorso dell'auto
segnando all'interno di una matrice tutte le celle occupate da ogni rotta.

Tale matrice viene poi trasferita alla simulazione principale in modo da permettere all'algoritmo di conoscere in anticipo
le celle che ogni auto andrà ad occupare.

Vengono poi restituiti 5 file all'interno della cartella Output di ogni branch: code, ferme, tempo, vel_med e t_in_coda.

