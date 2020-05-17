import BatchLib
from multiprocessing import Pool

direct = "~/SUMO/"  # percorso cartella

cons = open("Output/consumo2.txt", "w")  # scrivo consumo medio e massimo

#
#
# -------------------- VARIABILI MODIFICABILI -------------------- #

from_auto_test = 50  # (per simulazione impostare a 50)
to_auto_test = 200  # (per simulazione impostare a 100 o 200 se abbasatanza efficente)
step_auto_test = 50  # (per simulazione impostare a 50)
prove_fissate_auto = 20  # (per simulazione impostare a 20)
gui = False
n_porta_base = 5000

# ---------------------------------------------------------------- #
#
#

tempo_generazione = 43.2  # fissato
step0 = 0
step_sim = 0


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
                                             (n_port + x + y, n_auto, tempo_generazione, gui)))

        for y in range(0, prove_fissate_auto):
            ret = pool_arr[y].get()
            consumo_max += float(ret[0])
            consumo_med += float(ret[1])

        consumo_max = round(float(consumo_max) / float(prove_fissate_auto), 4)
        consumo_med = round(float(consumo_med) / float(prove_fissate_auto), 4)

        consumo_max_s = str(consumo_max)
        consumo_med_s = str(consumo_med)
        cons.write(str(x) + " " + consumo_max_s + " " + consumo_med_s + "\n")

cons.close()
print("\n\n\n\n\n\n\n")
print("FINE")
