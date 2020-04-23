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

    for i in range(0, celle_per_lato+1):  # scrivo sui vettori
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

    return [auto_temp, cella_X, cella_Y]


def in_incrocio(pos_temp, estremi_incrocio):
    if (estremi_incrocio[3] <= pos_temp[0] <= estremi_incrocio[1]) and \
            (estremi_incrocio[2] <= pos_temp[1] <= estremi_incrocio[0]):
        return True
    else:
        return False


def costruzioneArray(arrayAuto_temp):  # costruzione dell'array composto dal nome delle auto presenti nella sim.
    loadedIDList = traci.simulation.getDepartedIDList()  # carica nell'array le auto partite
    for id_auto in loadedIDList:
        if id_auto not in arrayAuto_temp:
            arrayAuto_temp.append(id_auto)
            traci.vehicle.setSpeed(id_auto, 1.0)
            # print("AUTO INSERT " + id_auto)

    arrivedIDList = traci.simulation.getArrivedIDList()  # elimina nell'array le auto arrivate
    for id_auto in arrivedIDList:
        if id_auto in arrayAuto_temp:
            arrayAuto_temp.pop(arrayAuto_temp.index(id_auto))
            # print("AUTO POP " + id_auto)

    return arrayAuto_temp


def generaVeicoli():
    r_depart = -49
    lane = 0
    auto_ogni = 50
    for i in range(0, 11):
        r_route = i
        r_depart += auto_ogni
        if r_route != 2 and r_route != 4 and r_route != 6 and r_route != 11:

            if r_route == 0 or r_route == 5 or r_route == 8 or r_route == 10:
                lane = "2"
            elif r_route == 1 or r_route == 3 or r_route == 7 or r_route == 9:
                lane = "1"

            route = "route_" + str(r_route)
            id_veh = "veh_" + str(i)
            traci.vehicle.add(id_veh, route, "Car", str(r_depart), lane, "base", "0.5")


def run(port_t, gui, celle_per_lato):
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

    generaVeicoli()  # genero veicoli

    # istanzio le matrici [nome_incrocio, variabile]
    lista_arrivo = []  # auto entrate nelle vicinanze dell'incrocio, non si pulisce
    lista_uscita = []  # auto uscite dall'incrocio, non si pulisce
    stop = []  # di quanto si distanzia lo stop dal centro incrocio [dx, sotto, sx, sopra]
    centerJunctID = []  # coordinate (x,y) del centro di un incrocio
    arrayAuto = []  # contiene lista di auto presenti nella simulazione
    limiti_celle_X = []  # utile per verificare l'appartenenza ad una cella all'interno della matrice dell'incrocio
    limiti_celle_Y = []  # utile per verificare l'appartenenza ad una cella all'interno della matrice dell'incrocio

    ret_lista_occupazione_celle = []

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
        # popolo vettori e matrici inserendo le righe
        lista_arrivo.append([])
        lista_uscita.append([])

        centerJunctID.append(traci.junction.getPosition(incrNome))  # posizione centro dell'incrocio

        shape = traci.junction.getShape(incrNome)  # forma dell'incrocio
        stop.append(stopXY(shape))  # esrtremi dell'incrocio, dove sono presenti gli stop

        # popolo i vettori limiti_celle_X e limiti_celle_Y
        ritorno2 = limiti_celle(stopXY(shape), celle_per_lato)
        limiti_celle_X.append(ritorno2[0])
        limiti_celle_Y.append(ritorno2[1])
        print(limiti_celle_X)
        print(limiti_celle_Y)

    arrayAuto = costruzioneArray(arrayAuto)  # inserisco nell'array le auto presenti nella simulazione

    while traci.simulation.getMinExpectedNumber() > 0:  # fino a quando tt le auto da inserire hanno terminato la corsa

        for incrNome in junctIDList:  # scorro lista incroci
            incrID = junctIDList.index(incrNome)

            for auto in arrayAuto:  # scorro l'array delle auto ancora presenti nella simulazione

                # print(index)

                if in_incrocio(traci.vehicle.getPosition(auto), stop[incrID]):

                    index = -1
                    route = traci.vehicle.getRouteID(auto)

                    if len(ret_lista_occupazione_celle):
                        for x in ret_lista_occupazione_celle:
                            if x[0] == route:
                                index = ret_lista_occupazione_celle.index(x)

                        if index == -1:
                            vett = [route, []]
                            ret_lista_occupazione_celle.append(vett)
                            index = ret_lista_occupazione_celle.index(vett)
                    else:
                        # print("Inserisco nell'array")
                        vett = [route, []]
                        ret_lista_occupazione_celle.append(vett)
                        index = ret_lista_occupazione_celle.index(vett)

                    # print("DENTRO INCROCIO!")

                    ritorno = get_cella_from_pos_auto(auto, limiti_celle_X[incrID], limiti_celle_Y[incrID])
                    pos_attuale_X = ritorno[1]
                    pos_attuale_Y = ritorno[2]

                    try:
                        if ret_lista_occupazione_celle[index][1].index([pos_attuale_Y, pos_attuale_X]):
                            pass
                    except ValueError:
                        ret_lista_occupazione_celle[index][1].append([pos_attuale_Y, pos_attuale_X])
                        # print("\n")
                        # print(route)
                        # print("Posizione attuale: " + str(pos_attuale_X) + " | " + str(pos_attuale_Y))

        step += 1
        traci.simulationStep(step)  # faccio avanzare la simulazione

        arrayAuto = costruzioneArray(arrayAuto)  # inserisco nell'array le auto presenti nella simulazione

    # STAMPO LA MATRICE
    for x in ret_lista_occupazione_celle:
        print(x)

    traci.close()
    return ret_lista_occupazione_celle
