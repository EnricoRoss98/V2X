import BatchLib
from multiprocessing import Pool

direct = "~/SUMO/"  # percorso cartella
cons = open("Output/consumo2.txt", "w")
cons0 = open("Output0/consumo2.txt")

#
#
# -------------------- VARIABILI MODIFICABILI -------------------- #

from_auto_test = 50  # (per simulazione impostare a 10)
to_auto_test = 200  # (per simulazione impostare a 100 o 200 se abbasatanza efficente)
step_auto_test = 50  # (per simulazione impostare a 10)
prove_fissate_auto = 20  # (per simulazione impostare a 20)
max_auto_insieme = 12  # solo per Version4 e Versione7
gui = False
n_porta_base = 5000

# ---------------------------------------------------------------- #
#
#

tempo_generazione = 43.2  # fissato
lines6 = cons0.readlines()

for x in range(from_auto_test, to_auto_test + 1):
    if x % step_auto_test == 0:
        print("\nPROVE CON " + str(x) + " AUTO\n")
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
            consumo_max += float(ret[0])
            consumo_med += float(ret[1])

        consumo_max = float(consumo_max) / float(prove_fissate_auto)
        consumo_med = float(consumo_med) / float(prove_fissate_auto)

        indice_riga = 0
        for c in range(0, 5):
            linea = lines6[c].split(" ")
            if linea[0].__contains__(str(x)):
                indice_riga = c
                break

        consumo_max0 = float((lines6[indice_riga].split(" "))[1])
        consumo_med0 = float((lines6[indice_riga].split(" "))[2])

        consumo_max = round(float(consumo_max) / float(consumo_max0), 4)
        consumo_med = round(float(consumo_med) / float(consumo_med0), 4)

        consumo_max = consumo_max - 1
        consumo_med = consumo_med - 1

        consumo_max_s = str(consumo_max)
        consumo_med_s = str(consumo_med)

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

cons.close()
cons0.close()
print("\n\n\n\n\n\n\n")
print("FINE")
