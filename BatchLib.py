# SEMPLIFICAZIONI:
# - incrocio a forma di "+" e strade ad angoli multipli di 90 gradi
# - ricordarsi di modificare il tipo di junction in netedit, in unregulated o l'ultimo

import os
import sys
import random
import math

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

    # print(limiti_celle_X_temp)
    # print(limiti_celle_Y_temp)
    # print(pos)
    # print(str(cella_X) + " | " + str(cella_Y))

    return [auto_temp, cella_X, cella_Y]


def in_incrocio(pos_temp, estremi_incrocio):
    if (estremi_incrocio[3] <= pos_temp[0] <= estremi_incrocio[1]) and \
            (estremi_incrocio[2] <= pos_temp[1] <= estremi_incrocio[0]):
        return True
    else:
        return False


def metri_da_incrocio(auto_temp, estremi_incrocio):  # calcolo la distanza in metri dall'incrocio
    pos = traci.vehicle.getPosition(auto_temp)
    ang = traci.vehicle.getAngle(auto_temp)
    dist = 0
    if ang == 0:
        dist = abs(float(estremi_incrocio[2]) - float(pos[1]))
    if ang == 180:
        dist = abs(float(estremi_incrocio[0]) - float(pos[1]))
    if ang == 90:
        dist = abs(float(estremi_incrocio[3]) - float(pos[0]))
    if ang == 270:
        dist = abs(float(estremi_incrocio[1]) - float(pos[0]))

    dist = 0 - dist
    # ritorno i metri di distanza dall'incrocio come numero negativo (inizio dell'incrocio e' lo zero)
    return dist


def t_arrivo_cella(auto_temp, metri_da_incrocio_temp, metri_da_cella_temp):  # ritorna timstep di arrivo sulla cella
    vi = traci.vehicle.getSpeed(auto_temp)
    vf = traci.vehicle.getMaxSpeed(auto_temp)
    a = traci.vehicle.getAccel(auto_temp)
    # print vi, vf, a # CORRETTI

    t = - (vi / a) + (math.sqrt((vi * vi) + (float(2) * a * (metri_da_cella_temp - metri_da_incrocio_temp))) / a) + \
        (metri_da_cella_temp / vf) - (((vf * vf) - (vi * vi)) / (float(2) * a * vf)) + (metri_da_incrocio_temp / vf)
    t = round(t, 4)

    print metri_da_incrocio_temp, metri_da_cella_temp, t
    return t + traci.simulation.getTime()


def celle_occupate_data_ang(ang, x_auto_in_celle_temp, y_auto_in_celle_temp):
    # restituisce le celle occupate data angolazione del veicolo, centrate in [0][0]
    celle_occupate = []
    ang = ang % 180
    ang = - ang
    x_auto = x_auto_in_celle_temp * 1.3
    y_auto = y_auto_in_celle_temp
    # print(x_auto)
    # print(y_auto)
    # print("\n")
    ang = math.radians(ang)  # converto in radianti
    a1 = [- float(x_auto) / float(2), float(y_auto) / float(2)]
    a2 = [float(x_auto) / float(2), float(y_auto) / float(2)]
    b1 = [- float(x_auto) / float(2), - float(y_auto) / float(2)]
    b2 = [float(x_auto) / float(2), - float(y_auto) / float(2)]
    # print(a1)
    # print(a2)
    # print(b1)
    # print(b2)
    # print("\n")

    # coordinate degli angoli ruotati
    a1 = [round(a1[0] * math.cos(ang) - a1[1] * math.sin(ang), 4),
          round(a1[0] * math.sin(ang) + a1[1] * math.cos(ang), 4)]
    a2 = [round(a2[0] * math.cos(ang) - a2[1] * math.sin(ang), 4),
          round(a2[0] * math.sin(ang) + a2[1] * math.cos(ang), 4)]
    b1 = [round(b1[0] * math.cos(ang) - b1[1] * math.sin(ang), 4),
          round(b1[0] * math.sin(ang) + b1[1] * math.cos(ang), 4)]
    b2 = [round(b2[0] * math.cos(ang) - b2[1] * math.sin(ang), 4),
          round(b2[0] * math.sin(ang) + b2[1] * math.cos(ang), 4)]
    # print(a1)
    # print(a2)
    # print(b1)
    # print(b2)
    # print("\n")

    # r = [a, b, c]
    r1 = [a2[1] - a1[1], a1[0] - a2[0], - a1[0] * a2[1] + a2[0] * a1[1]]
    r2 = [b2[1] - a2[1], a2[0] - b2[0], - a2[0] * b2[1] + b2[0] * a2[1]]
    r3 = [b2[1] - b1[1], b1[0] - b2[0], - b1[0] * b2[1] + b2[0] * b1[1]]
    r4 = [b1[1] - a1[1], a1[0] - b1[0], - a1[0] * b1[1] + b1[0] * a1[1]]
    # print("r1 = "+str(r1[0])+"x + "+str(r1[1])+"y + "+str(r1[2])+" = 0")
    # print("r2 = "+str(r2[0])+"x + "+str(r2[1])+"y + "+str(r2[2])+" = 0")
    # print("r3 = "+str(r3[0])+"x + "+str(r3[1])+"y + "+str(r3[2])+" = 0")
    # print("r4 = "+str(r4[0])+"x + "+str(r4[1])+"y + "+str(r4[2])+" = 0")
    # print("\n")

    # per ogni cella guardo se uno dei 4 angoli e' all'interno del rettangolo
    massimo = max([x_auto, y_auto])
    for y_cella in range(-int(massimo / 2) - 3, int(massimo / 2) + 4):
        for x_cella in range(-int(massimo / 2) - 3, int(massimo / 2) + 4):
            # print(str(y_cella)+" | "+str(x_cella))
            inserito = False
            if not inserito and (r1[0] * (x_cella - 0.5) + r1[1] * (y_cella - 0.5) + r1[2] >= 0) and \
                    (r2[0] * (x_cella - 0.5) + r2[1] * (y_cella - 0.5) + r2[2] >= 0) and \
                    (r3[0] * (x_cella - 0.5) + r3[1] * (y_cella - 0.5) + r3[2] <= 0) and \
                    (r4[0] * (x_cella - 0.5) + r4[1] * (y_cella - 0.5) + r4[2] <= 0):
                celle_occupate.append([y_cella, x_cella])
                inserito = True
            if not inserito and (r1[0] * (x_cella + 0.5) + r1[1] * (y_cella - 0.5) + r1[2] >= 0) and \
                    (r2[0] * (x_cella + 0.5) + r2[1] * (y_cella - 0.5) + r2[2] >= 0) and \
                    (r3[0] * (x_cella + 0.5) + r3[1] * (y_cella - 0.5) + r3[2] <= 0) and \
                    (r4[0] * (x_cella + 0.5) + r4[1] * (y_cella - 0.5) + r4[2] <= 0):
                celle_occupate.append([y_cella, x_cella])
                inserito = True
            if not inserito and (r1[0] * (x_cella - 0.5) + r1[1] * (y_cella + 0.5) + r1[2] >= 0) and \
                    (r2[0] * (x_cella - 0.5) + r2[1] * (y_cella + 0.5) + r2[2] >= 0) and \
                    (r3[0] * (x_cella - 0.5) + r3[1] * (y_cella + 0.5) + r3[2] <= 0) and \
                    (r4[0] * (x_cella - 0.5) + r4[1] * (y_cella + 0.5) + r4[2] <= 0):
                celle_occupate.append([y_cella, x_cella])
                inserito = True
            if not inserito and (r1[0] * (x_cella + 0.5) + r1[1] * (y_cella + 0.5) + r1[2] >= 0) and \
                    (r2[0] * (x_cella + 0.5) + r2[1] * (y_cella + 0.5) + r2[2] >= 0) and \
                    (r3[0] * (x_cella + 0.5) + r3[1] * (y_cella + 0.5) + r3[2] <= 0) and \
                    (r4[0] * (x_cella + 0.5) + r4[1] * (y_cella + 0.5) + r4[2] <= 0):
                celle_occupate.append([y_cella, x_cella])
                inserito = True

    # print celle_occupate
    # print len(celle_occupate)

    return celle_occupate


def arrivoAuto(auto_temp, passaggio_temp, ferme_temp, attesa_temp, matrice_incrocio_temp, passaggio_cella_temp,
               traiettorie_matrice_temp, estremi_incrocio, sec_sicurezza, x_auto_in_celle_temp, y_auto_in_celle_temp):
    # gest. arrivo auto in prossimita' dello stop

    if not get_from_matrice_incrocio(auto_temp, matrice_incrocio_temp, traiettorie_matrice_temp, estremi_incrocio,
                                     sec_sicurezza, x_auto_in_celle_temp, y_auto_in_celle_temp):
        ferme_temp.append(auto_temp)
        traci.vehicle.setSpeed(auto_temp, 0.0)  # faccio fermare l'auto
    else:
        # puo' passare e la faccio passare, segnandola in matrice e vettori
        traci.vehicle.setSpeedMode(auto_temp, 30)
        passaggio_temp.append([auto_temp, traci.vehicle.getRoadID(auto_temp), traci.vehicle.getAngle(auto_temp)])
        attesa_temp.pop(attesa_temp.index(auto_temp))  # lo tolgo dalla lista d'attesa e sotto scrivo nella matrice
        matrice_incrocio_temp = set_in_matrice_incrocio(auto_temp, matrice_incrocio_temp, traiettorie_matrice_temp,
                                                        estremi_incrocio, x_auto_in_celle_temp, y_auto_in_celle_temp)

        rotta = traci.vehicle.getRouteID(auto_temp)
        if rotta != "route_2" and rotta != "route_4" and rotta != "route_6" and rotta != "route_11":  # se non gira a DX
            passaggio_cella_temp.append([auto_temp, None, None])

        else:  # se l'auto gira a destra la faccio rallentare fino a dimezzare la velocita'
            traci.vehicle.setSpeed(auto_temp, traci.vehicle.getMaxSpeed(auto_temp) / float(2))

    ritorno = [passaggio_temp, attesa_temp, ferme_temp, matrice_incrocio_temp, passaggio_cella_temp]
    return ritorno


def set_in_matrice_incrocio(auto_temp, matrice_incrocio_temp, traiettorie_matrice_temp, estermi_incrocio,
                            x_auto_in_celle_temp, y_auto_in_celle_temp):
    # segna sulla matrice_incrocio l'occupazione delle celle toccate dall'auto durante l'attraversamento

    rotta = traci.vehicle.getRouteID(auto_temp)

    for route in traiettorie_matrice_temp:
        if route[0] == rotta:
            for celle in route[1]:
                # calcolo timestep di arrivo su tale cella
                timestep = t_arrivo_cella(auto_temp, metri_da_incrocio(auto_temp, estermi_incrocio), celle[2])
                celle_occupate = celle_occupate_data_ang(celle[3], x_auto_in_celle_temp, y_auto_in_celle_temp)
                # controllo le celle occupate dall'auto
                for celle_circostanti in celle_occupate:
                    index_y = celle_circostanti[0]
                    index_x = celle_circostanti[1]
                    if ((celle[0] + index_y) >= 0) and ((celle[1] + index_x) >= 0) and \
                            ((celle[0] + index_y) < len(matrice_incrocio_temp)) and \
                            ((celle[1] + index_x) < len(matrice_incrocio_temp)):
                        # print(str(celle[0] + index_y) + " | " + str(celle[1] + index_x))
                        matrice_incrocio_temp[celle[0] + index_y][celle[1] + index_x].append(round(timestep, 4))

    return matrice_incrocio_temp


def get_from_matrice_incrocio(auto_temp, matrice_incrocio_temp, traiettorie_matrice_temp, estermi_incrocio,
                              sec_sicurezza, x_auto_in_celle_temp, y_auto_in_celle_temp):
    # data auto e matrice_incrocio restituisce variabile booleana a True se non sono state rilevate collisioni
    # dall'attuale situazione di passaggio rilevata all'interno della matrice, False se rilevate collisioni

    rotta = traci.vehicle.getRouteID(auto_temp)

    libero = True

    for route in traiettorie_matrice_temp:
        if route[0] == rotta and libero:
            for celle in route[1]:
                timestep = t_arrivo_cella(auto_temp, metri_da_incrocio(auto_temp, estermi_incrocio), celle[2])
                celle_occupate = celle_occupate_data_ang(celle[3], x_auto_in_celle_temp, y_auto_in_celle_temp)
                # controllo le celle occupate dall'auto
                for celle_circostanti in celle_occupate:
                    index_y = celle_circostanti[0]
                    index_x = celle_circostanti[1]
                    if ((celle[0] + index_y) >= 0) and ((celle[1] + index_x) >= 0) and \
                            ((celle[0] + index_y) < len(matrice_incrocio_temp)) and \
                            ((celle[1] + index_x) < len(matrice_incrocio_temp)):
                        # scorre i tempi di occupazione segnati all'interno della cella
                        for t in matrice_incrocio_temp[celle[0] + index_y][celle[1] + index_x]:
                            # controlla che il timestep di arrivo calcolato non cada in un range di sicurezza
                            # dal valore selezionato
                            if t - sec_sicurezza <= timestep <= t + sec_sicurezza:
                                libero = False
                                break

    return libero


def isLibero(passaggio_temp, matrice_incrocio_temp, passaggio_cella_temp, limiti_celle_X_temp, limiti_celle_Y_temp,
             estremi_incrocio):
    # controllo se e' cambiata la situazione all'interno dell'incrocio
    passaggio_nuovo = passaggio_temp[:]
    passaggio_cella_nuovo = passaggio_cella_temp[:]

    # print("isLibero")

    for x in passaggio_temp:

        rotta = traci.vehicle.getRouteID(x[0])
        if rotta != "route_2" and rotta != "route_4" and rotta != "route_6" and rotta != "route_11":  # se non gira a DX

            for y in passaggio_cella_temp:
                if x[0] == y[0]:

                    # print(x[0])

                    pos = traci.vehicle.getPosition(x[0])
                    if in_incrocio(pos, estremi_incrocio):  # se e' ancora nell'incrocio

                        # print("inIncrocio")

                        ritorno = get_cella_from_pos_auto(x[0], limiti_celle_X_temp, limiti_celle_Y_temp)
                        pos_attuale_X = ritorno[1]
                        pos_attuale_Y = ritorno[2]

                        # print("Posizione attuale: " + str(pos_attuale_X) + " | " + str(pos_attuale_Y))

                        if pos_attuale_X != y[1] or pos_attuale_Y != y[2]:  # se la pos della vettura nelle celle cambia

                            # aggiorno poi il vettore con la nuova posizione della cella in cui si trova
                            passaggio_cella_nuovo[passaggio_cella_nuovo.index(y)] = [y[0], pos_attuale_X, pos_attuale_Y]

                            # y1 = [y[0], pos_attuale_X, pos_attuale_Y]
                            # print("Aggiorno vettore: " + str(passaggio_cella_nuovo[passaggio_cella_nuovo.index(y1)]))

                    else:  # altrimenti se l'auto e' uscita dall'incrocio
                        if y[1] is not None and y[2] is not None:  # se None allora non e' ancora entrata e non la tolgo
                            passaggio_nuovo.pop(passaggio_nuovo.index(x))  # tolgo l'auto dal vettore
                            passaggio_cella_nuovo.pop(passaggio_cella_nuovo.index(y))  # tolgo l'auto dal vettore

        else:  # se gira a destra vedo se cambia via e la tolgo dal vettore passaggio[]
            road = prossimaStrada(x)  # prossima via
            if traci.vehicle.getRoadID(x[0]) == road:
                passaggio_nuovo.pop(passaggio_nuovo.index(x))  # tolgo da passaggio

                # la faccio riaccelerare il veicolo
                traci.vehicle.setSpeed(x[0], traci.vehicle.getMaxSpeed(x[0]) * 4)

    ritorno = [passaggio_nuovo, matrice_incrocio_temp, passaggio_cella_nuovo]
    return ritorno


def avantiAuto(auto_temp, passaggio_temp, attesa_temp, ferme_temp, matrice_incrocio_temp, passaggio_cella_temp,
               traiettorie_matrice_temp, estremi_incrocio, x_auto_in_celle_temp, y_auto_in_celle_temp):
    # faccio avanzare auto

    traci.vehicle.setSpeedMode(auto_temp, 30)

    traci.vehicle.setSpeed(auto_temp, traci.vehicle.getMaxSpeed(auto_temp))  # riparte l'auto
    passaggio_temp.append([auto_temp, traci.vehicle.getRoadID(auto_temp), traci.vehicle.getAngle(auto_temp)])
    matrice_incrocio_temp = set_in_matrice_incrocio(auto_temp, matrice_incrocio_temp, traiettorie_matrice_temp,
                                                    estremi_incrocio, x_auto_in_celle_temp, y_auto_in_celle_temp)

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
            traci.vehicle.setSpeed(id_auto, traci.vehicle.getMaxSpeed(id_auto))
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
            consumo_temp[auto_temp].append(traci.vehicle.getElectricityConsumption(auto_temp) * 8)
        else:
            consumo_temp[auto_temp].append(traci.vehicle.getElectricityConsumption(auto_temp) * 8)

        # print(traci.vehicle.getElectricityConsumption(auto_temp) * 2)
        # print(traci.vehicle.getSpeed(auto_temp))

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

        if len(code) > 0:
            # costruisco riga in file code
            codemed = float(codesum) / float(len(code))
            cmed = round(codemed, 4)

            codemax = max(code)
            cmax = round(codemax, 4)

        else:
            cmax = 0.0
            cmed = 0.0
    else:
        ferme_count = 0
        vmed = 0.0
        cmax = 0.0
        cmed = 0.0

    return ferme_count, vmed, cmed, cmax, consumo_temp


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
    auto_ogni = float(t_gen) / float(n_auto_t)
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

        # 4 istruzioni sotto permettono di cambiare velocita' massima e accelerazione/decelerazione per la simulazione
        traci.vehicle.add(id_veh, route, "Car", str(r_depart), lane, "base", "13.88888")


def pulisci_matrice(matrice_incrocio_temp, sec_sicurezza_temp):
    matrice_incrocio = []
    for incr in matrice_incrocio_temp:
        index_incr = matrice_incrocio_temp.index(incr)
        matrice_incrocio.append(incr)
        for y in matrice_incrocio_temp[index_incr]:
            index_y = matrice_incrocio_temp[index_incr].index(y)
            for x in matrice_incrocio_temp[index_incr][index_y]:
                index_x = matrice_incrocio_temp[index_incr][index_y].index(x)
                for val in matrice_incrocio_temp[index_incr][index_y][index_x]:
                    # print(val)
                    index_val = matrice_incrocio_temp[index_incr][index_y][index_x].index(val)
                    if val < (traci.simulation.getTime() - sec_sicurezza_temp - 1):
                        matrice_incrocio[index_incr][index_y][index_x].pop(index_val)

    return matrice_incrocio


def run(port_t, n_auto, t_generazione, gui, celle_per_lato, traiettorie_matrice, sec_sicurezza):
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
        [sumoBinary, "-c", direct + config_sumo, "--remote-port", str(PORT), "--time-to-teleport", "-1", "-Q",
         "--step-length", "0.001"],
        stdout=sys.stdout,
        stderr=sys.stderr)
    # sumoProcess = subprocess.Popen(
    #     [sumoBinary, "-c", direct + config_sumo, "--remote-port", str(PORT), "-S", "--time-to-teleport", "-1", "-Q",
    #      "--battery-output", "out_battery.xml", "--battery-output.precision", "6"],
    #     stdout=sys.stdout,
    #     stderr=sys.stderr)

    # -------- dichiarazione variabili --------

    traci.init(PORT)
    step = 0.000
    step_incr = 0.036

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
    consumo = dict()  # lista di consumi rilevati per ogni auto (in un dizionario)
    rallentate = []  # lista di auto rallentate in prossimita' dell'incrocio
    passaggio_precedente = []  # salvo l'ultima situazione di auto in passaggio per rilasciarle all'uscita

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
        rallentate.append([])
        passaggio_cella.insert(incrID, [])
        passaggio_precedente.append([])

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

        matrice_incrocio.append([])  # popolo la matrice_incrocio (di ogni incrocio rilevato)
        for x in range(0, celle_per_lato):  # matrice
            matrice_incrocio[incrID].append([])
            for y in range(0, celle_per_lato):
                # ogni cella e' un'array dei tempi stimati di occupazione della medesima
                matrice_incrocio[incrID][x].append([])

    arrayAuto = costruzioneArray(arrayAuto)  # inserisco nell'array le auto presenti nella simulazione

    # trovo lunghezza e altezza auto in celle
    x_cella_in_m = abs(limiti_celle_X[0][1] - limiti_celle_X[0][0])
    y_cella_in_m = abs(limiti_celle_Y[0][1] - limiti_celle_Y[0][0])
    x_auto_in_m = traci.vehicle.getHeight("veh_0")
    y_auto_in_m = traci.vehicle.getLength("veh_0")
    x_auto_in_celle = float(x_auto_in_m) / float(x_cella_in_m)
    y_auto_in_celle = float(y_auto_in_m) / float(y_cella_in_m)
    # print(x_auto_in_celle)
    # print(y_auto_in_celle)

    while traci.simulation.getMinExpectedNumber() > 0:  # fino a quando tt le auto da inserire hanno terminato la corsa

        for incrNome in junctIDList:  # scorro lista incroci
            incrID = junctIDList.index(incrNome)

            for auto in arrayAuto:  # scorro l'array delle auto ancora presenti nella simulazione

                # print(auto + ": " + str(traci.vehicle.getSpeed(auto)))

                auto_in_lista = True
                try:  # vedo se auto e' in lista tra le auto segnate per attraversare l'incrocio
                    presente = int(lista_arrivo[incrID].index(auto))
                except ValueError:
                    auto_in_lista = False

                pos = traci.vehicle.getPosition(auto)

                if not auto_in_lista:  # se non in lista allora vedi se sta entrando nelle vicinanze dell'incrocio
                    stop_temp = stop[incrID]

                    if (stop_temp[3] - 50 <= pos[0] <= stop_temp[1] + 50) and \
                            (stop_temp[2] - 50 <= pos[1] <= stop_temp[0] + 50):
                        lista_arrivo[incrID].append(auto)  # inserisco nella lista d'arrivo di quell'incrocio
                        attesa[incrID].append(auto)  # e inserisco nella lista d'attesa di quell'incrocio
                        traci.vehicle.setMaxSpeed(auto, 6.944444)

                if auto in attesa[incrID] and auto not in ferme[incrID]:
                    # se auto in attesa e non ferma, vedo se vicino allo stop e fermo se incr. occ.

                    if len(stop_temp) > 3:  # se ci sono i 4 lati dell'incrocio
                        if (stop_temp[3] - 13.5 <= pos[0] <= stop_temp[1] + 13.5) and \
                                (stop_temp[2] - 13.5 <= pos[1] <= stop_temp[0] + 13.5):

                            traci.vehicle.setDecel(auto, 1.92901)
                            traci.vehicle.setAccel(auto, 1.92901)

                            leader = traci.vehicle.getLeader(auto)  # salvo il leader (nome_auto, distanza)
                            if leader:
                                if leader[0] not in attesa[incrID]:  # se leader ha iniziato l'attraversata non lo conto
                                    leader = None

                            if not leader:  # se non c'e' leader
                                # controllo se auto non ha subito rallentamenti e la fermo in 16 m
                                if round(traci.vehicle.getSpeed(auto), 2) == round(traci.vehicle.getMaxSpeed(auto), 2):
                                    rientro4 = arrivoAuto(auto, passaggio[incrID], ferme[incrID], attesa[incrID],
                                                          matrice_incrocio[incrID], passaggio_cella[incrID],
                                                          traiettorie_matrice, stop[incrID], sec_sicurezza,
                                                          x_auto_in_celle, y_auto_in_celle)
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
                                                              traiettorie_matrice, stop[incrID], sec_sicurezza,
                                                              x_auto_in_celle, y_auto_in_celle)
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
                            # print("DENTRO!")
                            pos = traci.vehicle.getPosition(x[0])
                            if in_incrocio(pos, stop[incrID]):
                                IDvett = passaggio_cella[incrID].index(x)
                                # print("\nget_cella_from_pos_auto")
                                passaggio_cella[incrID][IDvett] = get_cella_from_pos_auto(x[0], limiti_celle_X[incrID],
                                                                                          limiti_celle_Y[incrID])
                                # print("\n")

                rientro2 = isLibero(passaggio[incrID], matrice_incrocio[incrID], passaggio_cella[incrID],
                                    limiti_celle_X[incrID], limiti_celle_Y[incrID], stop[incrID])
                passaggio[incrID] = rientro2[0]
                matrice_incrocio[incrID] = rientro2[1]
                passaggio_cella[incrID] = rientro2[2]

                if len(ferme[incrID]) > 0:  # se ci sono auto ferme, vedo se posso farne partire qualcuna

                    # scorri tra tutte le auto ferme e se una e' compatibile con la matrice allora falla partire
                    for auto_ferma in ferme[incrID]:
                        if auto_ferma in ferme[incrID]:
                            if get_from_matrice_incrocio(auto_ferma, matrice_incrocio[incrID], traiettorie_matrice,
                                                         stop[incrID], sec_sicurezza, x_auto_in_celle,
                                                         y_auto_in_celle):
                                # print("Faccio passare la " + str(auto_ferma))
                                # vedo se percorso e' libero, e se si allora la faccio partire
                                rientro4 = avantiAuto(auto_ferma, passaggio[incrID], attesa[incrID], ferme[incrID],
                                                      matrice_incrocio[incrID], passaggio_cella[incrID],
                                                      traiettorie_matrice, stop[incrID], x_auto_in_celle,
                                                      y_auto_in_celle)

                                passaggio[incrID] = rientro4[0]
                                attesa[incrID] = rientro4[1]
                                ferme[incrID] = rientro4[2]
                                matrice_incrocio[incrID] = rientro4[3]
                                passaggio_cella[incrID] = rientro4[4]

            if int(step / step_incr) % 4 == 0:
                tempo_coda[incrID] = output_t_in_coda(arrayAuto, tempo_coda[incrID], step, attesa[incrID])

        if int(step / step_incr) % 10 == 0:  # riaccelero i veicoli all'uscita dall'incrocio
            # print(passaggio_precedente[incrID])
            # print(passaggio[incrID])
            for auto_uscita in passaggio_precedente[incrID]:
                if auto_uscita not in passaggio[incrID]:
                    traci.vehicle.setMaxSpeed(auto_uscita[0], 13.888888)
            passaggio_precedente[incrID] = passaggio[incrID][:]

        # STAMPO LA MATRICE
        # print(traci.simulation.getTime())
        # print(passaggio[incrID])
        # print(passaggio_cella[incrID])
        # for x in matrice_incrocio[incrID]:  # matrice
        #     print(x)
        # print("\n\n")

        if int(step / step_incr) % 8 == 0:  # ogni 8 step ne calcola output
            file_rit = output(arrayAuto, auto_in_simulazione, consumo)  # per generare stringhe di output
            f_s.append(file_rit[0])
            vm_s.append(file_rit[1])
            cm_s.append(file_rit[2])
            cx_s.append(file_rit[3])
            consumo = file_rit[4]

        if int(step / step_incr) % 10 == 0:  # ogni 10 step pulisco la matrice da valori troppo vecchi
            matrice_incrocio = pulisci_matrice(matrice_incrocio, sec_sicurezza)

        coloreAuto(arrayAuto, junctIDList, attesa, ferme)  # assegna colori alle auto

        step += step_incr
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
