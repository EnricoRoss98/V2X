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


def arrivoAuto(auto_temp, passaggio_temp, ferme_temp, attesa_temp, matrice_incrocio_temp):
    # gest. arrivo auto in prossimita' dello stop

    if not get_from_matrice_incrocio(auto_temp, matrice_incrocio_temp):
        ferme_temp.append(auto_temp)
        traci.vehicle.setSpeed(auto_temp, 0.0)  # faccio fermare l'auto
    else:
        # puo' passare e la faccio passare, segnandola in matrice e vettori
        passaggio_temp.append([auto_temp, traci.vehicle.getRoadID(auto_temp), traci.vehicle.getAngle(auto_temp)])
        attesa_temp.pop(attesa_temp.index(auto_temp))  # lo tolgo dalla lista d'attesa e sotto scrivo nella matrice
        matrice_incrocio_temp = set_in_matrice_incrocio(auto_temp, passaggio_temp, matrice_incrocio_temp, 1)
    ritorno = [passaggio_temp, attesa_temp, ferme_temp, matrice_incrocio_temp]
    return ritorno


def set_in_matrice_incrocio(auto_temp, passaggio_temp, matrice_incrocio_temp, set_delete):
    # segna sulla matrice_incrocio l'occupazione delle celle toccate dall'auto durante l'attraversamento
    # set_delete: 1 -> SET / 0 -> DELETE

    ang = 0
    count = 0
    for x in passaggio_temp:
        if passaggio_temp[count][0] == auto_temp:
            ang = passaggio_temp[count][2]
        count += 1
    rotta = traci.vehicle.getRouteID(auto_temp)

    scrivi = False
    if set_delete == 1:
        scrivi = True

    if rotta == "route_1" or rotta == "route_3" or rotta == "route_7" or rotta == "route_9":  # vanno diritte
        if ang == 0:
            for y in range(0, 8):
                matrice_incrocio_temp[y][5] = scrivi
        if ang == 270:
            for x in range(0, 8):
                matrice_incrocio_temp[2][x] = scrivi
        if ang == 180:
            for y in range(0, 8):
                matrice_incrocio_temp[y][2] = scrivi
        if ang == 90:
            for x in range(0, 8):
                matrice_incrocio_temp[5][x] = scrivi

    if rotta == "route_2" or rotta == "route_4" or rotta == "route_6" or rotta == "route_11":  # girano a DX
        if ang == 0:
            matrice_incrocio_temp[7][6] = scrivi
            matrice_incrocio_temp[6][6] = scrivi
            matrice_incrocio_temp[6][7] = scrivi
        if ang == 180:
            matrice_incrocio_temp[0][1] = scrivi
            matrice_incrocio_temp[1][0] = scrivi
            matrice_incrocio_temp[1][1] = scrivi
        if ang == 90:
            matrice_incrocio_temp[6][0] = scrivi
            matrice_incrocio_temp[6][1] = scrivi
            matrice_incrocio_temp[7][1] = scrivi
        if ang == 270:
            matrice_incrocio_temp[0][6] = scrivi
            matrice_incrocio_temp[1][6] = scrivi
            matrice_incrocio_temp[1][7] = scrivi

    if rotta == "route_0" or rotta == "route_5" or rotta == "route_8" or rotta == "route_10":  # girano a SX
        if ang == 0:
            matrice_incrocio_temp[3][0] = scrivi
            matrice_incrocio_temp[3][1] = scrivi
            matrice_incrocio_temp[3][2] = scrivi
            matrice_incrocio_temp[4][1] = scrivi
            matrice_incrocio_temp[4][2] = scrivi
            matrice_incrocio_temp[4][3] = scrivi
            matrice_incrocio_temp[5][3] = scrivi
            matrice_incrocio_temp[5][4] = scrivi
            matrice_incrocio_temp[6][3] = scrivi
            matrice_incrocio_temp[6][4] = scrivi
            matrice_incrocio_temp[7][4] = scrivi
        if ang == 270:
            matrice_incrocio_temp[3][7] = scrivi
            matrice_incrocio_temp[3][6] = scrivi
            matrice_incrocio_temp[3][5] = scrivi
            matrice_incrocio_temp[4][6] = scrivi
            matrice_incrocio_temp[4][5] = scrivi
            matrice_incrocio_temp[4][4] = scrivi
            matrice_incrocio_temp[5][4] = scrivi
            matrice_incrocio_temp[5][3] = scrivi
            matrice_incrocio_temp[6][4] = scrivi
            matrice_incrocio_temp[6][3] = scrivi
            matrice_incrocio_temp[7][3] = scrivi
        if ang == 90:
            matrice_incrocio_temp[0][4] = scrivi
            matrice_incrocio_temp[1][4] = scrivi
            matrice_incrocio_temp[1][3] = scrivi
            matrice_incrocio_temp[2][4] = scrivi
            matrice_incrocio_temp[2][3] = scrivi
            matrice_incrocio_temp[3][3] = scrivi
            matrice_incrocio_temp[3][2] = scrivi
            matrice_incrocio_temp[3][1] = scrivi
            matrice_incrocio_temp[4][2] = scrivi
            matrice_incrocio_temp[4][1] = scrivi
            matrice_incrocio_temp[4][0] = scrivi
        if ang == 180:
            matrice_incrocio_temp[0][3] = scrivi
            matrice_incrocio_temp[1][3] = scrivi
            matrice_incrocio_temp[1][4] = scrivi
            matrice_incrocio_temp[2][3] = scrivi
            matrice_incrocio_temp[2][4] = scrivi
            matrice_incrocio_temp[3][4] = scrivi
            matrice_incrocio_temp[3][5] = scrivi
            matrice_incrocio_temp[3][6] = scrivi
            matrice_incrocio_temp[4][5] = scrivi
            matrice_incrocio_temp[4][6] = scrivi
            matrice_incrocio_temp[4][7] = scrivi

    return matrice_incrocio_temp


def get_from_matrice_incrocio(auto_temp, matrice_incrocio_temp):
    # data auto e matrice_incrocio restituisce variabile booleana a True se non sono state rilevate collisioni
    # dall'attuale situazione di passaggio rilevata all'interno della matrice, False se rilevate collisioni

    ang = traci.vehicle.getAngle(auto_temp)
    rotta = traci.vehicle.getRouteID(auto_temp)

    libero = True

    if rotta == "route_1" or rotta == "route_3" or rotta == "route_7" or rotta == "route_9":  # vanno diritte
        if ang == 0:
            if matrice_incrocio_temp[2][5] == True or matrice_incrocio_temp[3][5] == True or \
                    matrice_incrocio_temp[4][5] == True or matrice_incrocio_temp[5][5] == True:
                libero = False
        if ang == 90:
            if matrice_incrocio_temp[5][2] == True or matrice_incrocio_temp[5][3] == True or \
                    matrice_incrocio_temp[5][4] == True or matrice_incrocio_temp[5][5] == True:
                libero = False
        if ang == 180:
            if matrice_incrocio_temp[2][2] == True or matrice_incrocio_temp[3][2] == True or \
                    matrice_incrocio_temp[4][2] == True or matrice_incrocio_temp[5][2] == True:
                libero = False
        if ang == 270:
            if matrice_incrocio_temp[2][2] == True or matrice_incrocio_temp[2][3] == True or \
                    matrice_incrocio_temp[2][4] == True or matrice_incrocio_temp[2][5] == True:
                libero = False

    if rotta == "route_0" or rotta == "route_5" or rotta == "route_8" or rotta == "route_10":  # girano a SX
        if ang == 0:
            if matrice_incrocio_temp[3][1] == True or matrice_incrocio_temp[3][2] == True or \
                    matrice_incrocio_temp[4][1] == True or matrice_incrocio_temp[4][2] == True:
                libero = False
            if matrice_incrocio_temp[5][3] == True or matrice_incrocio_temp[5][4] == True or \
                    matrice_incrocio_temp[6][3] == True or matrice_incrocio_temp[6][4] == True:
                libero = False
        if ang == 90:
            if matrice_incrocio_temp[3][1] == True or matrice_incrocio_temp[3][2] == True or \
                    matrice_incrocio_temp[4][1] == True or matrice_incrocio_temp[4][2] == True:
                libero = False
            if matrice_incrocio_temp[1][3] == True or matrice_incrocio_temp[1][4] == True or \
                    matrice_incrocio_temp[2][3] == True or matrice_incrocio_temp[2][4] == True:
                libero = False
        if ang == 180:
            if matrice_incrocio_temp[1][3] == True or matrice_incrocio_temp[1][4] == True or \
                    matrice_incrocio_temp[2][3] == True or matrice_incrocio_temp[2][4] == True:
                libero = False
            if matrice_incrocio_temp[2][5] == True or matrice_incrocio_temp[2][6] == True or \
                    matrice_incrocio_temp[3][5] == True or matrice_incrocio_temp[3][6] == True:
                libero = False
        if ang == 270:
            if matrice_incrocio_temp[2][5] == True or matrice_incrocio_temp[2][6] == True or \
                    matrice_incrocio_temp[3][5] == True or matrice_incrocio_temp[3][6] == True:
                libero = False
            if matrice_incrocio_temp[5][3] == True or matrice_incrocio_temp[5][4] == True or \
                    matrice_incrocio_temp[6][3] == True or matrice_incrocio_temp[6][4] == True:
                libero = False

    return libero


def isLibero(passaggio_temp, matrice_incrocio_temp):  # controllo se l'incrocio si e' liberato
    passaggio_nuovo = passaggio_temp[:]
    count = 0
    for x in passaggio_temp:

        road = prossimaStrada(passaggio_temp[count])  # prossima via
        if traci.vehicle.getRoadID(passaggio_temp[count][0]) == road:  # se l'auto cambia via considero incrocio libero
            passaggio_nuovo.pop(passaggio_nuovo.index(x))  # tolgo da passaggio e sotto tolgo occupazione su matrice
            matrice_incrocio_temp = set_in_matrice_incrocio(passaggio_temp[count][0], passaggio_temp,
                                                            matrice_incrocio_temp, 0)

        count += 1
    ritorno = [passaggio_nuovo, matrice_incrocio_temp]
    return ritorno


def avantiAuto(auto_temp, passaggio_temp, attesa_temp, ferme_temp, matrice_incrocio_temp):  # faccio avanzare auto

    traci.vehicle.setSpeed(auto_temp, 1.0)  # riparte l'auto
    passaggio_temp.append([auto_temp, traci.vehicle.getRoadID(auto_temp), traci.vehicle.getAngle(auto_temp)])
    matrice_incrocio_temp = set_in_matrice_incrocio(auto_temp, passaggio_temp, matrice_incrocio_temp, 1)

    if ferme_temp:
        try:
            ferme_temp.pop(ferme_temp.index(auto_temp))  # tolgo dalla lista di auto ferme
        except ValueError:  # per le auto che faccio partire senza fermare non serve toglerle dalla lista
            pass
    attesa_temp.pop(attesa_temp.index(auto_temp))  # tolgo dalla lista l'auto
    ritorno = [passaggio_temp, attesa_temp, ferme_temp, matrice_incrocio_temp]
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

    direct = "/Users/Enrico/Documents/TraCI/Incrocio-batch/"  # percorso cartella
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
    passaggio = []  # auto in passaggio
    lista_arrivo = []  # auto entrate nelle vicinanze dell'incrocio, non si pulisce
    matrice_incrocio = []  # rappresenta la suddivisione matriciale dell'incrocio (in celle)
    lista_uscita = []  # auto uscite dall'incrocio, non si pulisce
    ferme = []  # lista di auto ferme allo stop
    stop = []  # di quanto si distanzia lo stop dal centro incrocio [dx, sotto, sx, sopra]
    centerJunctID = []  # coordinate (x,y) del centro di un incrocio
    arrayAuto = []  # contiene lista di auto presenti nella simulazione
    tempo_coda = []  # usata per fare calcoli su output del tempo medio in coda

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

        centerJunctID.append(traci.junction.getPosition(incrNome))  # posizione centro dell'incrocio

        shape = traci.junction.getShape(incrNome)  # forma dell'incrocio
        stop.append(stopXY(shape))  # esrtremi dell'incrocio, dove sono presenti gli stop

        tempo_coda.insert(incrID, [])  # popolo vettore per calcolo del tempo medio in coda
        for i in range(0, n_auto):
            tempo_coda[incrID].insert(i, [0, 0])

        matrice_incrocio.append([])  # popolo la matrice_incrocio (di ogni incrocio rilevato) mettendo tutte celle False
        for x in range(0, 8):  # matrice 8 x 8
            matrice_incrocio[incrID].append([])
            for y in range(0, 8):
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
                                    rientro4 = arrivoAuto(auto, passaggio[incrID], ferme[incrID],
                                                          attesa[incrID], matrice_incrocio[incrID])
                                    passaggio[incrID] = rientro4[0]
                                    attesa[incrID] = rientro4[1]
                                    ferme[incrID] = rientro4[2]
                                    matrice_incrocio[incrID] = rientro4[3]

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
                                        rientro4 = arrivoAuto(auto, passaggio[incrID], ferme[incrID],
                                                              attesa[incrID], matrice_incrocio[incrID])
                                        passaggio[incrID] = rientro4[0]
                                        attesa[incrID] = rientro4[1]
                                        ferme[incrID] = rientro4[2]
                                        matrice_incrocio[incrID] = rientro4[3]

            if passaggio[incrID] is not None:  # se ci sono auto in passaggio[] check se incrocio si e' liberato
                rientro2 = isLibero(passaggio[incrID], matrice_incrocio[incrID])
                passaggio[incrID] = rientro2[0]
                matrice_incrocio[incrID] = rientro2[1]

                if len(ferme[incrID]) > 0:  # se ci sono auto ferme, vedo se posso farne partire qualcuna

                    # scorri tra tutte le auto ferme e se una e' compatibile con la matrice allora falla partire
                    for auto_ferma in ferme[incrID]:
                        if auto_ferma in ferme[incrID]:
                            if get_from_matrice_incrocio(auto_ferma, matrice_incrocio[incrID]):
                                print("Faccio passare la "+str(auto_ferma))
                                # vedo se percorso e' libero, e se si allora la faccio partire
                                rientro4 = avantiAuto(auto_ferma, passaggio[incrID], attesa[incrID], ferme[incrID],
                                                      matrice_incrocio[incrID])

                                passaggio[incrID] = rientro4[0]
                                attesa[incrID] = rientro4[1]
                                ferme[incrID] = rientro4[2]
                                matrice_incrocio[incrID] = rientro4[3]

            tempo_coda[incrID] = output_t_in_coda(arrayAuto, tempo_coda[incrID], step, attesa[incrID])

            # STAMPO LA MATRICE
            # print(step)
            # print(passaggio[incrID])
            # stampo matrice incrocio
            # for x in range(0, 8):  # matrice 8 x 8
            #     print(matrice_incrocio[incrID][x])
            # print("\n\n")

        if step % 2 == 0:  # ogni 2 step ne calcola output
            file_rit = output(arrayAuto, auto_in_simulazione)  # per generare stringhe di output
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
