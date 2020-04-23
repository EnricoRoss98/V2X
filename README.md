# Versione 2.0 (da modificare)

Per prima cosa suddivide la dimensione dell’incrocio (grazie anche alla funzione che trova dove sono posizionati gli stop)
in sezioni, e salva in due vettori gli estremi di ogni cella.

Quando entra nell’incrocio un veicolo, viene localizzata la cella della matrice in cui si trova e viene salvata in un vettore,
ad ogni timestep viene ri-localizzata e se le coordinate della cella in cui si trova sono cambiate rispetto a quelle salvate
allora toglie l’occupazione da quella cella e salva l’indirizzo della nuova.
Al termine di questa procedura vengono scorse le auto ferme e se qualcuna ha una traiettoria di attraversamento
dell’incrocio compatibile con l’attuale situazione viene fatta partire e tutta la traiettoria viene prenotata.

In questo algoritmo per ogni cella in cui è stata rilevata l'occupazione si settano occupate anche le 8 celle adicaenti.

Le auto proseguono ad una velocità di simulazione di 0.5 m/s, in modo da permettere una distanza minore tra campionamenti, 
questo ci permette di essere più precisi nella rilevazione della posizione dell'automobile nell'incorico. In questo modo
riusciamo a dividere l'incrocio in una matrice di massimo 22 celle per lato.