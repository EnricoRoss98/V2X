# SEMPLIFICAZIONI:
# - incrocio a forma di "+" e strade ad angoli multipli di 90 gradi
# - ricordarsi di modificare il tipo di junction in netedit, in unregulated o l'ultimo

import os
import sys
import random
import math
import array

import subprocess
import traci


# -------- FUNZIONI --------

def stopXY(shape_temp):  # calcolo esrtremi dell'incrocio, dove sono presenti gli stop
    stop_temp = []
    for count in range(0, len(shape_temp) - 1):
        if shape_temp[count][0] == shape_temp[count + 1][0]:
            stop_temp.append(shape_temp[count][0])
        elif shape_temp[count][1] == shape_temp[count + 1][1]:
            stop_temp.append(shape_temp[count][1])

    # print(shape_temp)
    # print("Trovati " + str(len(stop_temp)) + " angoli")
    # print(stop_temp)

    return stop_temp


def limiti_celle(estremi_incrocio, celle_per_lato):
    # definisco i vettori
    limiti_celle_X_temp = []
    limiti_celle_Y_temp = []

    # lunghezza totale incrocio nell'asse X e Y
    lunghezza_X = estremi_incrocio[1] - estremi_incrocio[3]
    lunghezza_Y = estremi_incrocio[0] - estremi_incrocio[2]

    # lunghezza di una sola cella
    lungh_cella_X = float(lunghezza_X) / float(celle_per_lato)
    lungh_cella_Y = float(lunghezza_Y) / float(celle_per_lato)

    for i in range(0, celle_per_lato + 1):  # scrivo sui vettori
        limiti_celle_X_temp.append(round((estremi_incrocio[3] + (lungh_cella_X * i)), 3))
        limiti_celle_Y_temp.append(round((estremi_incrocio[0] - (lungh_cella_Y * i)), 3))

    # print(estremi_incrocio)
    # print(limiti_celle_X_temp)
    # print(limiti_celle_Y_temp)

    return [limiti_celle_X_temp, limiti_celle_Y_temp]


def get_cella_from_pos_auto(auto_temp, limiti_celle_X_temp, limiti_celle_Y_temp):
    # ritorna la cella in X e Y in cui si trova l'auto (vettore di ritorno e' gia' costruito per l'array)
    cella_X = 0
    cella_Y = 0
    pos = traci.vehicle.getPosition(auto_temp)

    for x in range(0, len(limiti_celle_X_temp) - 1):
        if limiti_celle_X_temp[x] <= pos[0] <= limiti_celle_X_temp[x + 1]:
            cella_X = x
    for y in range(0, len(limiti_celle_Y_temp) - 1):
        if limiti_celle_Y_temp[y] >= pos[1] >= limiti_celle_Y_temp[y + 1]:
            cella_Y = y

    print(limiti_celle_X_temp)
    print(limiti_celle_Y_temp)
    print(pos)
    print(str(cella_X) + " | " + str(cella_Y))

    return [auto_temp, cella_X, cella_Y]


def in_incrocio(pos_temp, estremi_incrocio):
    if (estremi_incrocio[3] <= pos_temp[0] <= estremi_incrocio[1]) and \
            (estremi_incrocio[2] <= pos_temp[1] <= estremi_incrocio[0]):
        return True
    else:
        return False


def arrivoAuto(auto_temp, passaggio_temp, ferme_temp, attesa_temp, matrice_incrocio_temp, passaggio_cella_temp,
               traiettorie_matrice_temp):
    # gest. arrivo auto in prossimita' dello stop

    if not get_from_matrice_incrocio(auto_temp, matrice_incrocio_temp, traiettorie_matrice_temp):
        ferme_temp.append(auto_temp)
        traci.vehicle.setSpeed(auto_temp, 0.0)  # faccio fermare l'auto
    else:
        # puo' passare e la faccio passare, segnandola in matrice e vettori
        passaggio_temp.append([auto_temp, traci.vehicle.getRoadID(auto_temp), traci.vehicle.getAngle(auto_temp)])
        attesa_temp.pop(attesa_temp.index(auto_temp))  # lo tolgo dalla lista d'attesa e sotto scrivo nella matrice
        matrice_incrocio_temp = set_in_matrice_incrocio(auto_temp, matrice_incrocio_temp, 1,
                                                        traiettorie_matrice_temp)

        rotta = traci.vehicle.getRouteID(auto_temp)
        if rotta != "route_2" and rotta != "route_4" and rotta != "route_6" and rotta != "route_11":  # se non gira a DX
            passaggio_cella_temp.append([auto_temp, None, None])

    ritorno = [passaggio_temp, attesa_temp, ferme_temp, matrice_incrocio_temp, passaggio_cella_temp]
    return ritorno


def set_in_matrice_incrocio(auto_temp, matrice_incrocio_temp, set_delete, traiettorie_matrice_temp):
    # segna sulla matrice_incrocio l'occupazione delle celle toccate dall'auto durante l'attraversamento
    # set_delete: 1 -> SET / 0 -> DELETE

    rotta = traci.vehicle.getRouteID(auto_temp)

    scrivi = False
    if set_delete == 1:
        scrivi = True

    for route in traiettorie_matrice_temp:
        if route[0] == rotta:
            for celle in route[1]:
                print("\n"+str(celle[0])+" | "+str(celle[1]))
                # scrivo sulla casella centrale e anche sulle 8 caselle circostanti
                for index_y in range(-1, 2):
                    for index_x in range(-1, 2):
                        if ((celle[0] + index_y) >= 0) and ((celle[1] + index_x) >= 0) and \
                                ((celle[0] + index_y) < len(matrice_incrocio_temp)) and \
                                ((celle[1] + index_x) < len(matrice_incrocio_temp)):
                            print(str(celle[0] + index_y) + " | " + str(celle[1] + index_x))
                            matrice_incrocio_temp[celle[0] + index_y][celle[1] + index_x] = scrivi

    return matrice_incrocio_temp


def get_from_matrice_incrocio(auto_temp, matrice_incrocio_temp, traiettorie_matrice_temp):
    # data auto e matrice_incrocio restituisce variabile booleana a True se non sono state rilevate collisioni
    # dall'attuale situazione di passaggio rilevata all'interno della matrice, False se rilevate collisioni

    rotta = traci.vehicle.getRouteID(auto_temp)

    libero = True

    for route in traiettorie_matrice_temp:
        if route[0] == rotta and libero:
            for celle in route[1]:

                # controllo la cella centrale e controllo anche le 8 caselle circostanti
                for index_y in range(-1, 2):
                    for index_x in range(-1, 2):
                        if ((celle[0] + index_y) >= 0) and ((celle[1] + index_x) >= 0) and \
                                ((celle[0] + index_y) < len(matrice_incrocio_temp)) and \
                                ((celle[1] + index_x) < len(matrice_incrocio_temp)):
                            if matrice_incrocio_temp[celle[0] + index_y][celle[1] + index_x]:
                                libero = False
                                break

    return libero


def isLibero(passaggio_temp, matrice_incrocio_temp, passaggio_cella_temp, limiti_celle_X_temp, limiti_celle_Y_temp,
             estremi_incrocio):
    # controllo se e' cambiata la situazione all'interno dell'incrocio
    passaggio_nuovo = passaggio_temp.copy()
    passaggio_cella_nuovo = passaggio_cella_temp.copy()

    print("isLibero")

    for x in passaggio_temp:

        rotta = traci.vehicle.getRouteID(x[0])
        if rotta != "route_2" and rotta != "route_4" and rotta != "route_6" and rotta != "route_11":  # se non gira a DX

            for y in passaggio_cella_temp:
                if x[0] == y[0]:

                    print(x[0])

                    pos = traci.vehicle.getPosition(x[0])
                    if in_incrocio(pos, estremi_incrocio):  # se e' ancora nell'incrocio

                        print("inIncrocio")

                        ritorno = get_cella_from_pos_auto(x[0], limiti_celle_X_temp, limiti_celle_Y_temp)
                        pos_attuale_X = ritorno[1]
                        pos_attuale_Y = ritorno[2]

                        print("Posizione attuale: " + str(pos_attuale_X) + " | " + str(pos_attuale_Y))

                        if pos_attuale_X != y[1] or pos_attuale_Y != y[2]:  # se la pos della vettura nelle celle cambia

                            print("Posizione attuale diversa dalla precedente! -> " + str(y[1]) + " | " + str(y[2]))

                            if y[1] is not None and y[2] is not None:
                                print("Imposto vecchia cella su cui era a False")

                                # imposto la vecchia cella su cui era a False e anche sulle 8 caselle circostanti
                                for index_y in range(-1, 2):
                                    for index_x in range(-1, 2):
                                        if ((y[2] + index_y) >= 0) and ((y[1] + index_x) >= 0) and \
                                                ((y[2] + index_y) < len(matrice_incrocio_temp)) and \
                                                ((y[1] + index_x) < len(matrice_incrocio_temp)):
                                            matrice_incrocio_temp[y[2] + index_y][y[1] + index_x] = False

                            # matrice_incrocio_temp[pos_attuale_X][pos_attuale_Y] = True  # e la nuova cella su True

                            # aggiorno poi il vettore con la nuova posizione della cella in cui si trova
                            passaggio_cella_nuovo[passaggio_cella_nuovo.index(y)] = [y[0], pos_attuale_X, pos_attuale_Y]

                            y1 = [y[0], pos_attuale_X, pos_attuale_Y]
                            print("Aggiorno vettore: " + str(passaggio_cella_nuovo[passaggio_cella_nuovo.index(y1)]))

                    else:  # altrimenti se l'auto e' uscita dall'incrocio
                        if y[1] is not None and y[2] is not None:  # se None allora non e' ancora entrata e non la tolgo
                            passaggio_nuovo.pop(passaggio_nuovo.index(x))  # tolgo l'auto dal vettore
                            passaggio_cella_nuovo.pop(passaggio_cella_nuovo.index(y))  # tolgo l'auto dal vettore

                            # imposto la vecchia cella su cui era a False e anche le 8 caselle circostanti
                            for index_y in range(-1, 2):
                                for index_x in range(-1, 2):
                                    if ((y[2] + index_y) >= 0) and ((y[1] + index_x) >= 0) and \
                                            ((y[2] + index_y) < len(matrice_incrocio_temp)) and \
                                            ((y[1] + index_x) < len(matrice_incrocio_temp)):
                                        matrice_incrocio_temp[y[2] + index_y][y[1] + index_x] = False

        else:  # se gira a destra vedo se cambia via e la tolgo dal vettore passaggio[]
            road = prossimaStrada(x)  # prossima via
            if traci.vehicle.getRoadID(x[0]) == road:
                passaggio_nuovo.pop(passaggio_nuovo.index(x))  # tolgo da passaggio

    ritorno = [passaggio_nuovo, matrice_incrocio_temp, passaggio_cella_nuovo]
    return ritorno


def avantiAuto(auto_temp, passaggio_temp, attesa_temp, ferme_temp, matrice_incrocio_temp, passaggio_cella_temp,
               traiettorie_matrice_temp):
    # faccio avanzare auto

    traci.vehicle.setSpeed(auto_temp, 0.5)  # riparte l'auto
    passaggio_temp.append([auto_temp, traci.vehicle.getRoadID(auto_temp), traci.vehicle.getAngle(auto_temp)])
    matrice_incrocio_temp = set_in_matrice_incrocio(auto_temp, matrice_incrocio_temp, 1,
                                                    traiettorie_matrice_temp)

    if ferme_temp:
        try:
            ferme_temp.pop(ferme_temp.index(auto_temp))  # tolgo dalla lista di auto ferme
        except ValueError:  # per le auto che faccio partire senza fermare non serve toglerle dalla lista
            pass
    attesa_temp.pop(attesa_temp.index(auto_temp))  # tolgo dalla lista l'auto
    passaggio_cella_temp.append([auto_temp, None, None])
    ritorno = [passaggio_temp, attesa_temp, ferme_temp, matrice_incrocio_temp, passaggio_cella_temp]
    return ritorno


def prossimaStrada(passaggio_temp):  # ottengo il nome della via a cui l'auto e' diretta
    # print("Entrato in prossimaStrada")
    route = traci.vehicle.getRoute(passaggio_temp[0])  # ottengo rotta dell'auto che sta attraversando
    # print(route)
    att_road = passaggio_temp[1]  # strada attuale
    # print(att_road)
    pross_roadID = route.index(att_road) + 1  # posizione nel vettore attuale via + 1 = prossima
    # print(pross_roadID)
    pross_road = route[pross_roadID]  # prossima strada
    # print(pross_roadID)
    # print(pross_road)
    return pross_road


def costruzioneArray(arrayAuto_temp):  # costruzione dell'array composto dal nome delle auto presenti nella sim.
    loadedIDList = traci.simulation.getDepartedIDList()  # carica nell'array le auto partite
    for id_auto in loadedIDList:
        if id_auto not in arrayAuto_temp:
            arrayAuto_temp.append(id_auto)
            traci.vehicle.setSpeed(id_auto, 0.5)
            # print("AUTO INSERT " + id_auto)

    arrivedIDList = traci.simulation.getArrivedIDList()  # elimina nell'array le auto arrivate
    for id_auto in arrivedIDList:
        if id_auto in arrayAuto_temp:
            arrayAuto_temp.pop(arrayAuto_temp.index(id_auto))
            # print("AUTO POP " + id_auto)

    return arrayAuto_temp


def coloreAuto(arrayAuto_temp, junctIDList_temp, attesa_temp, ferme_temp):  # colora le auto a seconda del loro stato
    for auto_temp in arrayAuto_temp:
        colorata = False
        for junctID in range(0, len(junctIDList_temp)):
            if auto_temp in attesa_temp[junctID]:
                colorata = True
                if auto_temp in ferme_temp[junctID]:
                    traci.vehicle.setColor(auto_temp, (255, 0, 0))
                else:
                    traci.vehicle.setColor(auto_temp, (255, 255, 0))
        if not colorata:
            traci.vehicle.setColor(auto_temp, (0, 255, 0))


def output(arrayAuto_temp, auto_in_simulazione_t):  # scrivo nei file di output ad ogni timestep
    # calcoli per file ferme e vel_med
    vmed = 0
    ferme_count = 0
    for auto_temp in arrayAuto_temp:
        if round(traci.vehicle.getSpeed(auto_temp), 3) == 0:
            ferme_count += 1
        vmed += traci.vehicle.getSpeed(auto_temp)
        # vm_temp.write(auto_temp + ": " + str(traci.vehicle.getSpeed(auto_temp)) + " |  ")
    # vm_temp.write("\n\n")

    # calcoli per scrivere nel file code
    code = []

    for viaID in traci.edge.getIDList():  # scorro vie
        # coda per ogni angolo di percorrenza della via
        coda0 = 0
        coda90 = 0
        coda180 = 0
        coda270 = 0
        for auto_temp in arrayAuto_temp:  # scorro auto nella simulazione
            if traci.vehicle.getRoadID(auto_temp) == viaID:  # vedo se auto e' su quella via
                # print(auto_temp+" "+str(round(traci.vehicle.getSpeed(auto_temp), 3)))
                if round(traci.vehicle.getSpeed(auto_temp), 3) == 0:  # se ferma contr. ang e +1 uno alla relativa coda
                    ang = traci.vehicle.getAngle(auto_temp)
                    if ang == 0:
                        coda0 += 1
                    if ang == 90:
                        coda90 += 1
                    if ang == 180:
                        coda180 += 1
                    if ang == 270:
                        coda270 += 1

        # se ci sono auto nella coda di quell'angolo inserisci nel vettore code
        if coda0 > 0:
            code.append(coda0)
        if coda90 > 0:
            code.append(coda90)
        if coda180 > 0:
            code.append(coda180)
        if coda270 > 0:
            code.append(coda270)

    codesum = 0
    for count in range(0, len(code)):
        codesum += code[count]

    if len(arrayAuto_temp) > 0:

        # costruisco riga in file velocita' media
        vmed = float(vmed) / float(len(arrayAuto_temp))
        vmed = round(vmed, 4)  # fino a 4 numeri dopo la virgola

        # costruisco riga in file ferme
        ferme_perc = float(ferme_count) / float(auto_in_simulazione_t)
        ferme_perc = round(ferme_perc, 4)

        if len(code) > 0:
            # costruisco riga in file code
            codemed = (float(codesum) / float(len(code))) / float(auto_in_simulazione_t)
            cmed = round(codemed, 4)

            codemax = float(max(code)) / float(auto_in_simulazione_t)
            cmax = round(codemax, 4)

        else:
            cmax = 0.0
            cmed = 0.0
    else:
        ferme_perc = 0.0
        vmed = 0.0
        cmax = 0.0
        cmed = 0.0

    return ferme_perc, vmed, cmax, cmed


def output_t_in_coda(arrayAuto_temp, auto_coda_temp, step_temp, attesa_temp):
    # scrittura nell'array auto_coda per il calcolo del tempo in coda medio rispetto al tempo totale di simulazione
    for auto_temp in arrayAuto_temp:
        split = str(auto_temp).rsplit("_")
        auto_temp_ID = int(split[1])
        if auto_coda_temp[auto_temp_ID][0] == 0:
            if round(traci.vehicle.getSpeed(auto_temp), 3) == 0:  # se auto ferma allora segno timestep inizio coda
                auto_coda_temp[auto_temp_ID][0] = step_temp
        if auto_coda_temp[auto_temp_ID][0] != 0 and auto_coda_temp[auto_temp_ID][1] == 0 and \
                auto_temp not in attesa_temp:  # se non e' piu' in attesa allora segno timestep di fine coda
            auto_coda_temp[auto_temp_ID][1] = step_temp
    return auto_coda_temp


def generaVeicoli(n_auto_t, t_gen):
    r_depart = 0
    lane = 0
    auto_ogni = int(t_gen / n_auto_t)
    for i in range(0, n_auto_t):
        r_route = int(random.randint(0, 11))
        # r_depart += int(random.expovariate(0.05))
        r_depart += auto_ogni
        if r_route == 0 or r_route == 5 or r_route == 8 or r_route == 10:
            lane = "2"
        elif r_route == 1 or r_route == 3 or r_route == 7 or r_route == 9:
            lane = "1"
        elif r_route == 2 or r_route == 4 or r_route == 6 or r_route == 11:
            lane = "0"
        route = "route_" + str(r_route)
        id_veh = "veh_" + str(i)
        traci.vehicle.add(id_veh, route, "Car", str(r_depart), lane, "base", "0.5")
        traci.vehicle.setAccel(id_veh, 0.0078125)
        traci.vehicle.setDecel(id_veh, 0.0078125)


def run(port_t, n_auto, t_generazione, gui, celle_per_lato, traiettorie_matrice):
    # -------- import python modules from the $SUMO_HOME/tools directory --------

    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
        sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
            os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
        from sumolib import checkBinary
    except ImportError:
        sys.exit("please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation "
                 "(it should contain folders 'bin', 'tools' and 'docs')")

    PORT = port_t
    if gui:
        sumoBinary = checkBinary('sumo-gui')
    else:
        sumoBinary = checkBinary('sumo')

    # -------- percorsi cartella e file SUMO --------

    direct = "SUMO/"  # percorso cartella
    config_sumo = "incrocio.sumo.cfg"  # nome del file SUMO config

    # -----------------------------------------------

    # print(sumoBinary)
    sumoProcess = subprocess.Popen(
        [sumoBinary, "-c", direct + config_sumo, "--remote-port", str(PORT), "--time-to-teleport", "-1", "-Q"],
        stdout=sys.stdout,
        stderr=sys.stderr)

    # -------- dichiarazione variabili --------

    traci.init(PORT)
    step = 0

    auto_in_simulazione = n_auto  # auto tot generate nella simulazione da passare come parametro in batch
    generaVeicoli(auto_in_simulazione, t_generazione)  # genero veicoli

    # istanzio le matrici [nome_incrocio, variabile]
    attesa = []  # ordine di arrivo su lista, si pulisce quando liberano incrocio
    passaggio = []  # auto in passaggio
    lista_arrivo = []  # auto entrate nelle vicinanze dell'incrocio, non si pulisce
    matrice_incrocio = []  # rappresenta la suddivisione matriciale dell'incrocio (in celle)
    lista_uscita = []  # auto uscite dall'incrocio, non si pulisce
    ferme = []  # lista di auto ferme allo stop
    stop = []  # di quanto si distanzia lo stop dal centro incrocio [dx, sotto, sx, sopra]
    centerJunctID = []  # coordinate (x,y) del centro di un incrocio
    arrayAuto = []  # contiene lista di auto presenti nella simulazione
    tempo_coda = []  # usata per fare calcoli su output del tempo medio in coda
    limiti_celle_X = []  # utile per verificare l'appartenenza ad una cella all'interno della matrice dell'incrocio
    limiti_celle_Y = []  # utile per verificare l'appartenenza ad una cella all'interno della matrice dell'incrocio
    passaggio_cella = []  # salvo in che cella si trova l'auto in passaggio [incrID][ [ auto , cella_X , cella_Y ],... ]

    rientro4 = [passaggio, attesa, ferme, matrice_incrocio]

    f_s = []
    vm_s = []
    cm_s = []
    cx_s = []

    # -------- trovo lista degli incroci --------

    junctIDList_temp = []  # lista delle junction
    junctIDList_tupla = traci.junction.getIDList()  # creo lista delle junction (creo l'array dalla tupla)
    for junct in junctIDList_tupla:
        if not junct.startswith(":"):  # elimino le junction che iniziano con ':'
            junctIDList_temp.append(junct)

    junctIDList = []  # lista degli incroci

    for junctID in range(0, len(junctIDList_temp)):  # elimino junction di estermita', non sono degli incroci
        junct = junctIDList_temp[junctID]
        junctShape = traci.junction.getShape(junct)
        if len(junctShape) > 3:
            junctIDList.append(junct)

    # ---------- MAIN ----------

    for incrNome in junctIDList:  # scorro lista incroci
        incrID = junctIDList.index(incrNome)  # popolo vettori e matrici inserendo le righe
        attesa.append([])
        lista_arrivo.append([])
        lista_uscita.append([])
        ferme.append([])
        passaggio.append([])
        passaggio_cella.insert(incrID, [])

        centerJunctID.append(traci.junction.getPosition(incrNome))  # posizione centro dell'incrocio

        shape = traci.junction.getShape(incrNome)  # forma dell'incrocio
        stop.append(stopXY(shape))  # esrtremi dell'incrocio, dove sono presenti gli stop

        # popolo i vettori limiti_celle_X e limiti_celle_Y
        ritorno2 = limiti_celle(stopXY(shape), celle_per_lato)
        limiti_celle_X.append(ritorno2[0])
        limiti_celle_Y.append(ritorno2[1])

        tempo_coda.insert(incrID, [])  # popolo vettore per calcolo del tempo medio in coda
        for i in range(0, n_auto):
            tempo_coda[incrID].insert(i, [0, 0])

        matrice_incrocio.append([])  # popolo la matrice_incrocio (di ogni incrocio rilevato) mettendo tutte celle False
        for x in range(0, celle_per_lato):  # matrice
            matrice_incrocio[incrID].append([])
            for y in range(0, celle_per_lato):
                matrice_incrocio[incrID][x].append(False)

    arrayAuto = costruzioneArray(arrayAuto)  # inserisco nell'array le auto presenti nella simulazione

    while traci.simulation.getMinExpectedNumber() > 0:  # fino a quando tt le auto da inserire hanno terminato la corsa

        for incrNome in junctIDList:  # scorro lista incroci
            incrID = junctIDList.index(incrNome)

            for auto in arrayAuto:  # scorro l'array delle auto ancora presenti nella simulazione

                auto_in_lista = True
                try:  # vedo se auto e' in lista tra le auto segnate per attraversare l'incrocio
                    presente = int(lista_arrivo[incrID].index(auto))
                except ValueError:
                    auto_in_lista = False

                pos = traci.vehicle.getPosition(auto)

                if not auto_in_lista:  # se non in lista allora vedi se sta entrando nelle vicinanze dell'incrocio
                    centerJunctID_temp = centerJunctID[incrID]

                    if ((centerJunctID_temp[0] - 50 <= pos[0] <= centerJunctID_temp[0] + 50)
                            and (centerJunctID_temp[1] - 50 <= pos[1] <= centerJunctID_temp[1] + 50)):
                        lista_arrivo[incrID].append(auto)  # inserisco nella lista d'arrivo di quell'incrocio
                        attesa[incrID].append(auto)  # e inserisco nella lista d'attesa di quell'incrocio

                if auto in attesa[incrID] and auto not in ferme[incrID]:
                    # se auto in attesa e non ferma, vedo se vicino allo stop e fermo se incr. occ.

                    stop_temp = stop[incrID]
                    if len(stop_temp) > 3:  # se ci sono i 4 lati dell'incrocio
                        if (stop_temp[3] - 17 <= pos[0] <= stop_temp[1] + 17) and \
                                (stop_temp[2] - 17 <= pos[1] <= stop_temp[0] + 17):  # 1 +16 m to stop from 30km/h

                            leader = traci.vehicle.getLeader(auto)  # salvo il leader (nome_auto, distanza)
                            if leader:
                                if leader[0] not in attesa[incrID]:  # se leader ha iniziato l'attraversata non lo conto
                                    leader = None

                            if not leader:  # se non c'e' leader
                                # controllo se auto non ha subito rallentamenti e la fermo in 16 m
                                if traci.vehicle.getSpeed(auto) == 1:
                                    rientro4 = arrivoAuto(auto, passaggio[incrID], ferme[incrID], attesa[incrID],
                                                          matrice_incrocio[incrID], passaggio_cella[incrID],
                                                          traiettorie_matrice)
                                    passaggio[incrID] = rientro4[0]
                                    attesa[incrID] = rientro4[1]
                                    ferme[incrID] = rientro4[2]
                                    matrice_incrocio[incrID] = rientro4[3]
                                    passaggio_cella[incrID] = rientro4[4]

                                # se auto ha subito rallentamenti calcolo dalla sua velocita' in quanti metri
                                # dall'incrocio si fermerebbe se la facessi rallentare subito, se si va a fermare in
                                # prossimita' allora avvio l'arresto del veicolo altrimenti aspetto il prossimo step
                                # e ricontrollo
                                else:
                                    dist_stop = 0
                                    v_auto = traci.vehicle.getSpeed(auto)
                                    decel = traci.vehicle.getDecel(auto)

                                    ang = traci.vehicle.getAngle(auto)

                                    if ang == 90:
                                        dist_stop = abs(stop_temp[3] - pos[0])
                                    if ang == 0:
                                        dist_stop = abs(stop_temp[2] - pos[1])
                                    if ang == 270:
                                        dist_stop = abs(stop_temp[1] - pos[0])
                                    if ang == 180:
                                        dist_stop = abs(stop_temp[0] - pos[1])

                                    dist_to_stop = (v_auto * v_auto) / (2 * decel)

                                    if dist_to_stop + 2 >= dist_stop:
                                        rientro4 = arrivoAuto(auto, passaggio[incrID], ferme[incrID], attesa[incrID],
                                                              matrice_incrocio[incrID], passaggio_cella[incrID],
                                                              traiettorie_matrice)
                                        passaggio[incrID] = rientro4[0]
                                        attesa[incrID] = rientro4[1]
                                        ferme[incrID] = rientro4[2]
                                        matrice_incrocio[incrID] = rientro4[3]
                                        passaggio_cella[incrID] = rientro4[4]

            if passaggio[incrID] is not None:  # se ci sono auto in passaggio[] check se situazione incrocio e' cambiata

                # se e' appena entrata nell'area dell'incrocio salvo la cella in cui si trova
                for x in passaggio_cella[incrID]:
                    rotta = traci.vehicle.getRouteID(x[0])
                    if rotta != "route_2" and rotta != "route_4" and rotta != "route_6" and rotta != "route_11":
                        # se non gira a DX
                        if x[1] is None and x[2] is None:
                            print("DENTRO!")
                            pos = traci.vehicle.getPosition(x[0])
                            if in_incrocio(pos, stop[incrID]):
                                IDvett = passaggio_cella[incrID].index(x)
                                print("\nget_cella_from_pos_auto")
                                passaggio_cella[incrID][IDvett] = get_cella_from_pos_auto(x[0], limiti_celle_X[incrID],
                                                                                          limiti_celle_Y[incrID])
                                print("\n")

                rientro2 = isLibero(passaggio[incrID], matrice_incrocio[incrID], passaggio_cella[incrID],
                                    limiti_celle_X[incrID], limiti_celle_Y[incrID], stop[incrID])
                passaggio[incrID] = rientro2[0]
                matrice_incrocio[incrID] = rientro2[1]
                passaggio_cella[incrID] = rientro2[2]

                if step % 2 == 0:
                    if len(ferme[incrID]) > 0:  # se ci sono auto ferme, vedo se posso farne partire qualcuna

                        # scorri tra tutte le auto ferme e se una e' compatibile con la matrice allora falla partire
                        for auto_ferma in ferme[incrID]:
                            if auto_ferma in ferme[incrID]:
                                if get_from_matrice_incrocio(auto_ferma, matrice_incrocio[incrID], traiettorie_matrice):
                                    print("Faccio passare la " + str(auto_ferma))
                                    # vedo se percorso e' libero, e se si allora la faccio partire
                                    rientro4 = avantiAuto(auto_ferma, passaggio[incrID], attesa[incrID], ferme[incrID],
                                                          matrice_incrocio[incrID], passaggio_cella[incrID],
                                                          traiettorie_matrice)

                                    passaggio[incrID] = rientro4[0]
                                    attesa[incrID] = rientro4[1]
                                    ferme[incrID] = rientro4[2]
                                    matrice_incrocio[incrID] = rientro4[3]
                                    passaggio_cella[incrID] = rientro4[4]

            if step % 2 == 0:
                tempo_coda[incrID] = output_t_in_coda(arrayAuto, tempo_coda[incrID], step, attesa[incrID])

            # STAMPO LA MATRICE
            print(step)
            print(passaggio[incrID])
            print(passaggio_cella[incrID])
            for x in range(0, celle_per_lato):  # matrice
                print(matrice_incrocio[incrID][x])
            print("\n\n")

        if step % 4 == 0:  # ogni 2 step ne calcola output
            file_rit = output(arrayAuto, auto_in_simulazione)  # per generare stringhe di output
            f_s.append(file_rit[0])
            vm_s.append(file_rit[1])
            cm_s.append(file_rit[2])
            cx_s.append(file_rit[3])

        coloreAuto(arrayAuto, junctIDList, attesa, ferme)  # assegna colori alle auto

        step += 1
        traci.simulationStep(step)  # faccio avanzare la simulazione

        arrayAuto = costruzioneArray(arrayAuto)  # inserisco nell'array le auto presenti nella simulazione

    #
    # ---------- genero output e lo rimando indietro ----------
    t_med_coda = 0.0
    f_ret = 0.0
    vm_ret = 0.0
    cm_ret = 0.0
    cx_ret = 0.0

    for i in f_s:
        f_ret += i
    for i in vm_s:
        vm_ret += i
    for i in cm_s:
        cm_ret += i
    for i in cx_s:
        cx_ret += i

    # calcolo del tempo massimo in coda e tempo medio in coda
    diff_t_med_coda_incr = 0.0
    media_t_med_coda = 0.0
    max_t_coda = 0.0
    for incr in range(0, len(tempo_coda)):
        for auto in range(0, len(tempo_coda[incr])):
            t_in_coda = tempo_coda[incr][auto][1] - tempo_coda[incr][auto][0]
            if t_in_coda > max_t_coda:
                max_t_coda = t_in_coda
            diff_t_med_coda_incr += t_in_coda
        media_t_med_coda += round(float(diff_t_med_coda_incr) / float(len(tempo_coda[incr])), 4)
    media_t_med_coda = round(float(media_t_med_coda) / float(len(tempo_coda)), 4)

    f_ret = round(float(f_ret) / float(len(f_s)), 4)
    vm_ret = round(float(vm_ret) / float(len(vm_s)), 4)
    cm_ret = round(float(cm_ret) / float(len(cm_s)), 4)
    cx_ret = round(float(cx_ret) / float(len(cx_s)), 4)

    traci.close()
    return f_ret, vm_ret, cm_ret, cx_ret, step, max_t_coda, media_t_med_coda
