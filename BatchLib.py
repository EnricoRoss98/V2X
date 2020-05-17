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


def isLibero(occupato_temp, passaggio_temp):  # controllo se l'incrocio si e' liberato
    road = prossimaStrada(passaggio_temp)  # prossima via
    # print("In isLibero passaggio_temp[1] = " + passaggio_temp[1] + " e road = " + road)
    if traci.vehicle.getRoadID(passaggio_temp[0]) == road:  # se l'auto cambia via considero l'incrocio libero
        occupato_temp = False
        # print("In isLibero: LIBERO!")
    return occupato_temp


def prossimaStrada(passaggio_temp):  # ottengo il nome della via a cui l'auto e' diretta
    route = traci.vehicle.getRoute(passaggio_temp[0])  # ottengo rotta dell'auto che sta attraversando
    att_road = passaggio_temp[1]  # strada attuale
    pross_roadID = route.index(att_road) + 1  # posizione nel vettore attuale via + 1 = prossima
    pross_road = route[pross_roadID]  # prossima strada

    return pross_road


def costruzioneArray(arrayAuto_temp):
    # costruzione dell'array composto dal nome delle auto presenti nella sim.
    loadedIDList = traci.simulation.getDepartedIDList()  # carica nell'array le auto partite
    for id_auto in loadedIDList:
        if id_auto not in arrayAuto_temp:
            arrayAuto_temp.append(id_auto)

            # print("AUTO INSERT " + id_auto)

    arrivedIDList = traci.simulation.getArrivedIDList()  # elimina nell'array le auto arrivate
    for id_auto in arrivedIDList:
        if id_auto in arrayAuto_temp:
            arrayAuto_temp.pop(arrayAuto_temp.index(id_auto))
            # print("AUTO POP " + id_auto)

    return arrayAuto_temp


def output(arrayAuto_temp, auto_in_simulazione_t, consumo_temp):  # preparo valori per scrivere nei file di output
    # calcoli per file ferme, vel_med e consumo
    for auto_temp in arrayAuto_temp:
        if auto_temp not in consumo_temp:
            consumo_temp[auto_temp] = []
            consumo_temp[auto_temp].append(traci.vehicle.getFuelConsumption(auto_temp) * 16)
        else:
            consumo_temp[auto_temp].append(traci.vehicle.getFuelConsumption(auto_temp) * 16)

    return consumo_temp


def generaVeicoli(n_auto_t, t_gen):
    r_depart = 0
    lane = 0
    auto_ogni = t_gen / float(n_auto_t)
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
        traci.vehicle.add(id_veh, route, "Car", str(r_depart), lane, "base", "13.888888")
        traci.vehicle.setMaxSpeed(id_veh, 13.888888)
        traci.vehicle.setAccel(id_veh, 3.858024)
        traci.vehicle.setDecel(id_veh, 3.858024)


def run(port_t, n_auto, t_generazione, gui):
    # -------- import python modules from the $SUMO_HOME/tools directory --------
    global dist_stop
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
        [sumoBinary, "-c", direct + config_sumo, "--remote-port", str(PORT), "--time-to-teleport", "-1", "-Q",
         "--step-length", "0.001"],
        stdout=sys.stdout,
        stderr=sys.stderr)

    # -------- dichiarazione variabili --------

    traci.init(PORT)
    step = 0.000
    step_incr = 0.036

    auto_in_simulazione = n_auto  # auto tot generate nella simulazione da passare come parametro in batch
    generaVeicoli(auto_in_simulazione, t_generazione)  # genero veicoli

    # istanzio le matrici [nome_incrocio, variabile]
    attesa = []  # ordine di arrivo su lista, si pulisce quando liberano incrocio
    lista_arrivo = []  # auto entrate nelle vicinanze dell'incrocio, non si pulisce
    lista_uscita = []  # auto uscite dall'incrocio, non si pulisce
    occupato = []  # incrocio e' occupato?
    ferme = []  # lista di auto ferme allo stop
    stop = []  # di quanto si distanzia lo stop dal centro incrocio [dx, sotto, sx, sopra]
    centerJunctID = []  # coordinate (x,y) del centro di un incrocio
    arrayAuto = []  # contiene lista di auto presenti nella simulazione
    tempo_coda = []
    strade = []
    consumo = dict()  # lista di consumi rilevati per ogni auto (in un dizionario)

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
        occupato.append(False)
        ferme.append([])

        centerJunctID.append(traci.junction.getPosition(incrNome))  # posizione centro dell'incrocio

        shape = traci.junction.getShape(incrNome)  # forma dell'incrocio
        stop.append(stopXY(shape))  # esrtremi dell'incrocio, dove sono presenti gli stop

    arrayAuto = costruzioneArray(arrayAuto)

    while traci.simulation.getMinExpectedNumber() > 0:  # fino a quando tt le auto da inserire hanno terminato la corsa

        for incrNome in junctIDList:  # scorro lista incroci
            incrID = junctIDList.index(incrNome)

            for auto in arrayAuto:

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
                        # print(auto + " vicino a " + incrNome)
                        lista_arrivo[incrID].append(auto)  # inserisco nella lista d'arrivo di quell'incrocio
                        attesa[incrID].append(auto)  # e inserisco nella lista d'attesa di quell'incrocio
                        strade.append([auto, traci.vehicle.getRoadID(auto)])

                index_a = -1
                for auto_strade in strade:
                    if auto_strade[0] == auto:
                        index_a = strade.index(auto_strade)

                if index_a >= 0:
                    route = traci.vehicle.getRoute(auto)  # ottengo rotta dell'auto che sta attraversando
                    att_road = strade[index_a][1]  # strada attuale
                    pross_roadID = route.index(att_road) + 1  # posizione nel vettore attuale via + 1 = prossima
                    pross_road = route[pross_roadID]  # prossima strada
                    if traci.vehicle.getRoadID(auto) == pross_road:
                        attesa[incrID].pop(attesa[incrID].index(auto))
                        strade.pop(index_a)

        if int(step / step_incr) % 16 == 0:
            consumo = output(arrayAuto, auto_in_simulazione, consumo)  # per generare stringhe di output

        step += step_incr
        # print(step/step_incr)
        traci.simulationStep(step)  # faccio avanzare la simulazione

        arrayAuto = costruzioneArray(arrayAuto)  # inserisco nell'array le auto presenti nella simulazione
    #
    # ---------- genero output e lo rimando indietro ----------
    consumo_totale_per_auto = dict()

    for auto_temp in consumo:
        consumo_totale = 0
        lista_consumi = consumo[auto_temp]
        for x in lista_consumi:
            consumo_totale += x
        consumo_totale_per_auto[auto_temp] = consumo_totale

    # calcolo consumo massimo e medio
    consumo_massimo = 0.0
    consumo_medio = 0.0
    for x in consumo_totale_per_auto:
        consumo_medio += consumo_totale_per_auto.get(x)
        if consumo_totale_per_auto.get(x) > consumo_massimo:
            consumo_massimo = consumo_totale_per_auto.get(x)
    consumo_medio = round(consumo_medio / float(n_auto), 4)
    consumo_massimo = round(consumo_massimo, 4)

    # print(consumo_medio)
    # print(consumo_massimo)

    traci.close()
    return consumo_massimo, consumo_medio
