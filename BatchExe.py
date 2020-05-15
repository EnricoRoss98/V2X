import BatchLib
from multiprocessing import Pool

direct = "~/SUMO/"  # percorso cartella

f = open("Output/ferme.txt", "w")  # creo file ferme.txt percentuale di auto ferme
vm = open("Output/vel_med.txt", "w")  # creo file vel_med vel. media delle auto presenti
cm = open("Output/code.txt", "w")  # creo file code contiene coda piu' lunga e n med auto in coda (%)
t = open("Output/tempo.txt", "w")  # scrivo il tempo impiegato per terminare la simulazione rispetto no code
t_coda = open("Output/t_in_coda.txt", "w")  # scrivo il tempo medio in coda rispetto al tempo tot di simulaz.
cons = open("Output/consumo.txt", "w")  # scrivo consumo medio e massimo rispetto consumo in assenza di traffico (%)

f0 = open("Output0/ferme.txt", "r")  # creo file ferme.txt percentuale di auto ferme
vm0 = open("Output0/vel_med.txt", "r")  # creo file vel_med vel. media delle auto presenti
cm0 = open("Output0/code.txt", "r")  # creo file code contiene coda piu' lunga e n med auto in coda (%)
t0 = open("Output0/tempo.txt", "r")  # scrivo il tempo impiegato per terminare la simulazione rispetto no code
t_coda0 = open("Output0/t_in_coda.txt", "r")  # scrivo il tempo medio in coda rispetto al tempo tot di simulaz.
cons0 = open("Output0/consumo.txt", "r")  # scrivo consumo medio e massimo rispetto consumo in assenza di traffico (%)

#
#
# -------------------- VARIABILI MODIFICABILI -------------------- #

from_auto_test = 50  # (per simulazione impostare a 10)
to_auto_test = 200  # (per simulazione impostare a 100 o 200 se abbasatanza efficente)
step_auto_test = 50  # (per simulazione impostare a 10)
prove_fissate_auto = 1  # (per simulazione impostare a 20)
max_auto_insieme = 12  # solo per Version4 e Versione7
gui = True
n_porta_base = 5000

# ---------------------------------------------------------------- #
#
#

tempo_generazione = 43.2  # fissato

for x in range(from_auto_test, to_auto_test + 1):
    if x % step_auto_test == 0:
        print("\nPROVE CON " + str(x) + " AUTO\n")
        f_t = 0.0
        vm_t = 0.0
        cm_t = 0.0
        cx_t = 0.0
        step_sim = 0.0
        t_med_coda = 0.0
        max_t_coda = 0.0
        consumo_max = 0.0
        consumo_med = 0.0

        n_auto = x

        n_port = n_porta_base
        pool = Pool(processes=prove_fissate_auto)
        pool_arr = []
        for y in range(0, prove_fissate_auto):
            print("")
            print("\nESEGUO PROVA CON " + str(x) + " AUTO...\n")

            pool_arr.append(pool.apply_async(BatchLib.run,
                                             (n_port + x + y, n_auto, tempo_generazione, gui, max_auto_insieme)))

        for y in range(0, prove_fissate_auto):
            ret = pool_arr[y].get()
            f_t += float(ret[0])
            vm_t += float(ret[1])
            cm_t += float(ret[2])
            cx_t += float(ret[3])
            step_sim += float(ret[4])
            max_t_coda += float(ret[5])
            t_med_coda += float(ret[6])
            consumo_max += float(ret[7])
            consumo_med += float(ret[8])

        f_t = float(f_t) / float(prove_fissate_auto)
        vm_t = float(vm_t) / float(prove_fissate_auto)
        cm_t = float(cm_t) / float(prove_fissate_auto)
        cx_t = float(cx_t) / float(prove_fissate_auto)
        step_sim = float(step_sim) / float(prove_fissate_auto)
        max_t_coda = float(max_t_coda) / float(prove_fissate_auto)
        t_med_coda = float(t_med_coda) / float(prove_fissate_auto)
        consumo_max = float(consumo_max) / float(prove_fissate_auto)
        consumo_med = float(consumo_med) / float(prove_fissate_auto)

        indice_riga = 0
        count = 0
        while True:
            linea = (f0.readline()).split(" ")
            if linea is None or linea == "":
                break
            else:
                if int(linea[0]) == x:
                    indice_riga = count
            count += 1

        lines = f0.readlines()
        f_t0 = float((lines[indice_riga].split(" "))[1])
        lines = vm0.readlines()
        vm_t0 = float((lines[indice_riga].split(" "))[1])
        lines = cm0.readlines()
        cm_t0 = float((lines[indice_riga].split(" "))[1])
        cx_t0 = float((lines[indice_riga].split(" "))[2])
        lines = t0.readlines()
        step_sim0 = float((lines[indice_riga].split(" "))[1])
        lines = t_coda0.readlines()
        max_t_coda0 = float((lines[indice_riga].split(" "))[1])
        t_med_coda0 = float((lines[indice_riga].split(" "))[2])
        lines = cons0.readlines()
        consumo_max0 = float((lines[indice_riga].split(" "))[1])
        consumo_med0 = float((lines[indice_riga].split(" "))[2])

        f_t = round(float(f_t) / float(f_t0), 4)
        vm_t = round(float(vm_t) / float(vm_t0), 4)
        cm_t = round(float(cm_t) / float(cm_t0), 4)
        cx_t = round(float(cx_t) / float(cx_t0), 4)
        step_sim = round(float(step_sim) / float(step_sim0), 4)
        max_t_coda = round(float(max_t_coda) / float(max_t_coda0), 4)
        t_med_coda = round(float(t_med_coda) / float(t_med_coda0), 4)
        consumo_max = round(float(consumo_max) / float(consumo_max0), 4)
        consumo_med = round(float(consumo_med) / float(consumo_med0), 4)

        f_s = str(f_t)
        vm_s = str(vm_t)
        cm_s = str(cm_t)
        cx_s = str(cx_t)
        step_sim_s = str(step_sim)
        t_med_coda_s = str(t_med_coda)
        max_t_coda_s = str(max_t_coda)
        consumo_max_s = str(consumo_max)
        consumo_med_s = str(consumo_med)

        string_vett1 = vm_s.rsplit(".")
        if vm_t > 0:  # inserisco segno + se non c'e'
            vm_s = "+" + string_vett1[0] + "," + string_vett1[1]
        else:
            vm_s = string_vett1[0] + "," + string_vett1[1]
        vm.write(str(x) + " " + vm_s + "\n")

        string_vett1 = f_s.rsplit(".")
        if f_t > 0:  # inserisco segno + se non c'e'
            f_s = "+" + string_vett1[0] + "," + string_vett1[1]
        else:
            f_s = string_vett1[0] + "," + string_vett1[1]
        f.write(str(x) + " " + f_s + "\n")

        string_vett1 = cm_s.rsplit(".")
        string_vett2 = cx_s.rsplit(".")
        if cm_t > 0:  # inserisco segno + se non c'e'
            cm_s = "+" + string_vett1[0] + "," + string_vett1[1]
        else:
            cm_s = string_vett1[0] + "," + string_vett1[1]
        if cx_t > 0:  # inserisco segno + se non c'e'
            cx_s = "+" + string_vett2[0] + "," + string_vett2[1]
        else:
            cx_s = string_vett2[0] + "," + string_vett2[1]
        cm.write(str(x) + " " + cm_s + " " + cx_s + "\n")

        string_vett1 = step_sim_s.rsplit(".")
        if step_sim > 0:  # inserisco segno + se non c'e'
            step_sim_s = "+" + string_vett1[0] + "," + string_vett1[1]
        else:
            step_sim_s = string_vett1[0] + "," + string_vett1[1]
        t.write(str(x) + " " + step_sim_s + "\n")

        string_vett1 = max_t_coda_s.rsplit(".")
        string_vett2 = t_med_coda_s.rsplit(".")
        if max_t_coda > 0:  # inserisco segno + se non c'e'
            max_t_coda_s = "+" + string_vett1[0] + "," + string_vett1[1]
        else:
            max_t_coda_s = string_vett1[0] + "," + string_vett1[1]
        if t_med_coda > 0:  # inserisco segno + se non c'e'
            t_med_coda_s = "+" + string_vett2[0] + "," + string_vett2[1]
        else:
            t_med_coda_s = string_vett2[0] + "," + string_vett2[1]
        t_coda.write(str(x) + " " + max_t_coda_s + " " + t_med_coda_s + "\n")

        string_vett1 = consumo_max_s.rsplit(".")
        string_vett2 = consumo_med_s.rsplit(".")
        if consumo_max > 0:  # inserisco segno + se non c'e'
            consumo_max_s = "+" + string_vett1[0] + "," + string_vett1[1]
        else:
            consumo_max_s = string_vett1[0] + "," + string_vett1[1]
        if consumo_med > 0:  # inserisco segno + se non c'e'
            consumo_med_s = "+" + string_vett2[0] + "," + string_vett2[1]
        else:
            consumo_med_s = string_vett2[0] + "," + string_vett2[1]
        cons.write(str(x) + " " + consumo_max_s + " " + consumo_med_s + "\n")

t.close()
f.close()
cm.close()
vm.close()
t_coda.close()
cons.close()
print("\n\n\n\n\n\n\n")
print("FINE")
