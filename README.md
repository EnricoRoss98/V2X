# Versione 1.2

Le auto passano una alla volta ma c’è controllo che se la prossima auto che deve passare proviene dalla stessa strada di 
quella che sta passando allora falle partire insieme.
Ulteriore controllo nella funzione “avantiAuto” con passaggio di ulteriore parametro “insieme” 0 o 1, che se a 1 controlla che:
- se la seconda gira subito tengo la prima nel vettore “passaggio”, a meno che anche la seconda non giri subito allora segno 
la seconda
- se la prima va dritta tengo lei nel vettore “passaggio” a meno che anche la seconda non vada dritta, allora segno la seconda
- altrimenti salva nel vettore “passaggio” l’ultima auto fatta partire

