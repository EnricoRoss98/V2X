# Versione 1.4

La versione 1.4 segue la precedente versione 1.3 ma introduce un contatore delle auto passate per tale “situazione” e 
si azzera quando la cambia. Tale contatore è utile per ovviare al fatto che nella precedente versione un’auto da 
distanza con route compatibile con la “situazione” corrente all’interno dell’incrocio e con ancora auto in attraversata 
veniva sempre fatta passare, bloccando naturalmente tutte le altre auto non compatibili con le rotte delle auto in 
passaggio. Questo risulta poco efficace ed efficiente, sopratutto per un alto numero di auto generate, creerà una lunga 
serie di code.

Il contatore chiamato “max_auto_insieme” e settabile dal file BatchExe.py solo per l’esecuzione della Versione 1.4, 
permette di tenere conto dei veicoli passati in quella “situazione” e quando tale limite viene raggiunto si procede con 
una nuova configurazione di passaggio, in modo da consentire un flusso più o meno costante di avanzamento per tutte le 
code.