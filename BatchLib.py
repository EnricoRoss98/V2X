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
    vmed = 0
    ferme_count = 0
    for auto_temp in arrayAuto_temp:
        if round(traci.vehicle.getSpeed(auto_temp), 3) == 0:
            ferme_count += 1
        vmed += traci.vehicle.getSpeed(auto_temp)

        # print(traci.vehicle.getElectricityConsumption(auto_temp))
        if auto_temp not in consumo_temp:
            consumo_temp[auto_temp] = []
            consumo_temp[auto_temp].append(traci.vehicle.getElectricityConsumption(auto_temp))
        else:
            consumo_temp[auto_temp].append(traci.vehicle.getElectricityConsumption(auto_temp))

        # vm_temp.write(auto_temp + ": " + str(traci.vehicle.getSpeed(auto_temp)) + " |  ")
    # vm_temp.write("\n\n")

    # calcoli per scrivere nel file code
    code = []

    for viaID in traci.edge.getIDList():  # scorro vie
        if not viaID.startswith(":"):
            # coda per ogni corsia nella via
            coda0 = 0
            coda1 = 0
            coda2 = 0
            for auto_temp in arrayAuto_temp:  # scorro auto nella simulazione
                if traci.vehicle.getRoadID(auto_temp) == viaID:  # vedo se auto e' su quella via
                    # print(auto_temp+" "+str(round(traci.vehicle.getSpeed(auto_temp), 3)))
                    if round(traci.vehicle.getSpeed(auto_temp), 3) == 0:  # se V==0 contr corsia e +1 alla relativa coda
                        corsia = traci.vehicle.getLaneIndex(auto_temp)
                        if corsia == 0:
                            coda0 += 1
                        if corsia == 1:
                            coda1 += 1
                        if corsia == 2:
                            coda2 += 1
                        # print(auto_temp + " ferma in " + viaID + " corsia " + str(corsia))

            # se ci sono auto nella coda di quella corsia inserisci nel vettore code
            if coda0 > 0:
                code.append(coda0)
            if coda1 > 0:
                code.append(coda1)
            if coda2 > 0:
                code.append(coda2)
            # print(code)

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

    return ferme_perc, vmed, cmax, cmed, consumo_temp


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
         "--step-length", "0.1"],
        stdout=sys.stdout,
        stderr=sys.stderr)

    # -------- dichiarazione variabili --------

    traci.init(PORT)
    step = 0.0
    step_incr = 0.1

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
        occupato.append(False)
        ferme.append([])

        centerJunctID.append(traci.junction.getPosition(incrNome))  # posizione centro dell'incrocio

        shape = traci.junction.getShape(incrNome)  # forma dell'incrocio
        stop.append(stopXY(shape))  # esrtremi dell'incrocio, dove sono presenti gli stop

        tempo_coda.insert(incrID, [])  # popolo vettore per calcolo del tempo medio in coda
        for i in range(0, n_auto):
            tempo_coda[incrID].insert(i, [0, 0])

    arrayAuto = costruzioneArray(arrayAuto)

    while traci.simulation.getMinExpectedNumber() > 0:  # fino a quando tt le auto da inserire hanno terminato la corsa

        for incrNome in junctIDList:  # scorro lista incroci
            incrID = junctIDList.index(incrNome)

            for auto in arrayAuto:

                # print(traci.vehicle.getSpeed(auto))

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

            tempo_coda[incrID] = output_t_in_coda(arrayAuto, tempo_coda[incrID], step, attesa[incrID])

        file_rit = output(arrayAuto, auto_in_simulazione, consumo)  # per generare stringhe di output
        f_s.append(file_rit[0])
        vm_s.append(file_rit[1])
        cx_s.append(file_rit[2])
        cm_s.append(file_rit[3])
        consumo = file_rit[4]

        step += step_incr
        # print(step/step_incr)
        traci.simulationStep(step)  # faccio avanzare la simulazione

        arrayAuto = costruzioneArray(arrayAuto)  # inserisco nell'array le auto presenti nella simulazione
    #
    # ---------- genero output e lo rimando indietro ----------
    f_ret = 0.0
    vm_ret = 0.0
    cm_ret = 0.0
    cx_ret = 0.0
    consumo_totale_per_auto = dict()

    for i in f_s:
        f_ret += i
    for i in vm_s:
        vm_ret += i
    for i in cm_s:
        cm_ret += i
    for i in cx_s:
        cx_ret += i
    for auto_temp in consumo:
        consumo_totale = 0
        lista_consumi = consumo[auto_temp]
        for x in lista_consumi:
            consumo_totale += x
        consumo_totale_per_auto[auto_temp] = consumo_totale

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

    # calcolo consumo massimo e medio
    consumo_massimo = 0.0
    consumo_medio = 0.0
    for x in consumo_totale_per_auto:
        consumo_medio += consumo_totale_per_auto.get(x)
        if consumo_totale_per_auto.get(x) > consumo_massimo:
            consumo_massimo = consumo_totale_per_auto.get(x)
    consumo_medio = round(consumo_medio / float(n_auto), 4)
    consumo_massimo = round(consumo_massimo, 4)

    f_ret = round(float(f_ret) / float(len(f_s)), 4)
    vm_ret = round(float(vm_ret) / float(len(vm_s)), 4)
    cm_ret = round(float(cm_ret) / float(len(cm_s)), 4)
    cx_ret = round(float(cx_ret) / float(len(cx_s)), 4)

    # print(consumo_medio)
    # print(consumo_massimo)

    traci.close()
    return f_ret, vm_ret, cm_ret, cx_ret, step, max_t_coda, media_t_med_coda, consumo_massimo, consumo_medio
