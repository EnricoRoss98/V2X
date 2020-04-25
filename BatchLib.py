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


def arrivoAuto(auto_temp, occupato_temp, passaggio_temp, ferme_temp, attesa_temp):  # gest. arrivo auto in prossim. stop
    # print("Auto " + auto_temp + " vicino allo STOP!")
    if occupato_temp:
        ferme_temp.append(auto_temp)
        # print("STOP " + auto_temp + " !")
        traci.vehicle.setSpeed(auto_temp, 0.0)  # faccio fermare l'auto
    else:
        # print("INCROCIO LIBERO!  Auto " + auto_temp + " autorizzata al passaggio")
        occupato_temp = True
        passaggio_temp = [auto_temp, traci.vehicle.getRoadID(auto_temp)]  # segno il suo passaggio e via attuale
        attesa_temp.pop(attesa_temp.index(auto_temp))  # lo tolgo dalla lista d'attesa
    ritorno = [occupato_temp, passaggio_temp, attesa_temp, ferme_temp]
    return ritorno


def isLibero(occupato_temp, passaggio_temp):  # controllo se l'incrocio si e' liberato
    road = prossimaStrada(passaggio_temp)  # prossima via
    # print("In isLibero passaggio_temp[1] = " + passaggio_temp[1] + " e road = " + road)
    if traci.vehicle.getRoadID(passaggio_temp[0]) == road:  # se l'auto cambia via considero l'incrocio libero
        occupato_temp = False
        # print("In isLibero: LIBERO!")
    return occupato_temp


def avantiAuto(occupato_temp, passaggio_temp, attesa_temp, ferme_temp):  # faccio avanzare la prima in attesa
    # traci.vehicle.resume(attesa_temp[0])  # faccio ripartire il primo
    traci.vehicle.setSpeed(attesa_temp[0], 1.0)  # riparte l'auto
    # print("Resume " + attesa_temp[0])
    passaggio_temp = [attesa_temp[0], traci.vehicle.getRoadID(attesa_temp[0])]

    # print("avantiAuto: POP " + attesa_temp[0])

    if ferme_temp != []:
        try:
            ferme_temp.pop(ferme_temp.index(attesa_temp[0]))  # tolgo dalla lista di auto ferme
            # print("Tolgo dalla lista di auto ferme")
        except ValueError:  # per le auto che faccio partire senza fermare non serve toglerle dalla lista
            pass
    attesa_temp.pop(0)  # tolgo dalla lista d'attesa il primo
    occupato_temp = True
    ritorno = [occupato_temp, passaggio_temp, attesa_temp, ferme_temp]
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
            traci.vehicle.setSpeed(id_auto, 1.0)
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


def output(step_temp, arrayAuto_temp, auto_in_simulazione_t):  # scrivo nei file di output ad ogni timestep
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
        traci.vehicle.add(id_veh, route, "Car", str(r_depart), lane, "base", "1")


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
        [sumoBinary, "-c", direct + config_sumo, "--remote-port", str(PORT), "-S", "--time-to-teleport", "-1", "-Q"],
        stdout=sys.stdout,
        stderr=sys.stderr)

    # -------- dichiarazione variabili --------

    traci.init(PORT)
    step = 0

    auto_in_simulazione = n_auto  # auto tot generate nella simulazione da passare come parametro in batch
    generaVeicoli(auto_in_simulazione, t_generazione)  # genero veicoli

    # istanzio le matrici [nome_incrocio, variabile]
    attesa = []  # ordine di arrivo su lista, si pulisce quando liberano incrocio
    lista_arrivo = []  # auto entrate nelle vicinanze dell'incrocio, non si pulisce
    passaggio = []  # auto che sta passando [auto, strada]
    lista_uscita = []  # auto uscite dall'incrocio, non si pulisce
    occupato = []  # incrocio e' occupato?
    ferme = []  # lista di auto ferme allo stop
    stop = []  # di quanto si distanzia lo stop dal centro incrocio [dx, sotto, sx, sopra]
    centerJunctID = []  # coordinate (x,y) del centro di un incrocio
    arrayAuto = []  # contiene lista di auto presenti nella simulazione
    tempo_coda = []

    rientro4 = [occupato, passaggio, attesa, ferme]

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
        passaggio.append(["", ""])
        lista_uscita.append([])
        occupato.append(False)
        ferme.append([])

        centerJunctID.append(traci.junction.getPosition(incrNome))  # posizione centro dell'incrocio

        shape = traci.junction.getShape(incrNome)  # forma dell'incrocio
        stop.append(stopXY(shape))  # esrtremi dell'incrocio, dove sono presenti gli stop

        tempo_coda.insert(incrID, [])  # popolo vettore per calcolo del tempo medio in coda
        for i in range(0, n_auto):
            tempo_coda[incrID].insert(i, [0, 0])

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
                        # print(auto + " vicino a " + incrNome)
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
                                    rientro4 = arrivoAuto(auto, occupato[incrID], passaggio[incrID], ferme[incrID],
                                                          attesa[incrID])
                                    occupato[incrID] = rientro4[0]
                                    passaggio[incrID] = rientro4[1]
                                    attesa[incrID] = rientro4[2]
                                    ferme[incrID] = rientro4[3]

                                # se auto ha subito rallentamenti calcolo dalla sua velocita' in quanti metri
                                # dall'incrocio si fermerebbe se la facessi rallentare subito, se si va a fermare in
                                # prossimita' allora avvio l'arresto del veicolo altrimenti aspetto il prossimo step
                                # e ricontrollo
                                else:
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
                                        rientro4 = arrivoAuto(auto, occupato[incrID], passaggio[incrID], ferme[incrID],
                                                              attesa[incrID])
                                        occupato[incrID] = rientro4[0]
                                        passaggio[incrID] = rientro4[1]
                                        attesa[incrID] = rientro4[2]
                                        ferme[incrID] = rientro4[3]

            if passaggio[incrID][0] != "" and occupato[incrID]:  # se auto in passaggio[] check se incr. si e' liberato
                occupato[incrID] = isLibero(occupato[incrID], passaggio[incrID])

                if len(ferme[incrID]) > 0:  # se ci sono auto ferme, vedo se posso farne partire qualcuna

                    if not occupato[incrID]:  # se l'incrocio e' libero e ci sono auto ferme in attesa
                        rientro4 = avantiAuto(occupato[incrID], passaggio[incrID], attesa[incrID], ferme[incrID])

                        occupato[incrID] = rientro4[0]
                        passaggio[incrID] = rientro4[1]
                        attesa[incrID] = rientro4[2]
                        ferme[incrID] = rientro4[3]

            tempo_coda[incrID] = output_t_in_coda(arrayAuto, tempo_coda[incrID], step, attesa[incrID])

        if step % 2 == 0:  # ogni 2 step ne calcola output
            file_rit = output(step, arrayAuto, auto_in_simulazione)  # per generare stringhe di output
            f_s.append(file_rit[0])
            vm_s.append(file_rit[1])
            cx_s.append(file_rit[2])
            cm_s.append(file_rit[3])

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
    for i in cx_s:  # prendo il massimo
        if i > cx_ret:
            cx_ret = i

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

    traci.close()
    return f_ret, vm_ret, cm_ret, cx_ret, step, max_t_coda, media_t_med_coda
