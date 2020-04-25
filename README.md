# Versione 2.0

Questa è solamente una prova per comprendere come affrontare il problema della suddivisione matriciale dell'incrocio.

Le auto proseguono alla velocità di 1 m/s e la dimensione della matrice è 8 celle per lato. Quando un'auto arriva,
vengono segnate come occupati una serie di celle imposte anche in base alla sua traiettoria (è stato osservato banalmente
il comportamento dell'auto all'interno dell'incrocio). Il percorso viene pulito una volta che l’auto ha compiuto 
l’attraversata, si presuppone compiuta quando la vettura cambia il nome della via in cui si trova.

Viene fatta partire un’auto e poi viene controllato nell’array ferme, composto di tutte le auto capofila in attesa di 
poter attraversare, se qualcuna è compatibile con l’attuale situazione di occupazione della matrice viene fatta partire 
anche se l’incrocio non è libero.