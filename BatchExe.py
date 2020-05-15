import BatchLib
from multiprocessing import Pool

direct = "~/SUMO/"  # percorso cartella

f = open("Output/ferme.txt", "w")  # creo file ferme.txt percentuale di auto ferme
vm = open("Output/vel_med.txt", "w")  # creo file vel_med vel. media delle auto presenti
cm = open("Output/code.txt", "w")  # creo file code contiene coda piu' lunga e n med auto in coda (%)
t = open("Output/tempo.txt", "w")  # scrivo il tempo impiegato per terminare la simulazione rispetto no code
t_coda = open("Output/t_in_coda.txt", "w")  # scrivo il tempo medio in coda rispetto al tempo tot di simulaz.
cons = open("Output/consumo.txt", "w")  # scrivo consumo medio e massimo rispetto consumo in assenza di traffico (%)

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
            f_t += float(ret[0])
            vm_t += float(float(ret[1])/float(8.33))
            cm_t += float(ret[2])
            cx_t += float(ret[3])
            step_sim += float(ret[4])
            max_t_coda += float(ret[5])
            t_med_coda += float(ret[6])
            consumo_max += float(ret[7])
            consumo_med += float(ret[8])

        f_t = round(float(f_t) / float(prove_fissate_auto), 4)
        vm_t = round(float(vm_t) / float(prove_fissate_auto), 4)
        cm_t = round(float(cm_t) / float(prove_fissate_auto), 4)
        cx_t = round(float(cx_t) / float(prove_fissate_auto), 4)
        step_sim = round(float(step_sim) / float(prove_fissate_auto), 4)
        max_t_coda = round(float(max_t_coda) / float(prove_fissate_auto), 4)
        t_med_coda = round(float(t_med_coda) / float(prove_fissate_auto), 4)
        consumo_max = round(float(consumo_max) / float(prove_fissate_auto), 4)
        consumo_med = round(float(consumo_med) / float(prove_fissate_auto), 4)

        f_s = str(f_t)
        vm_s = str(vm_t)
        cm_s = str(cm_t)
        cx_s = str(cx_t)
        t_med_coda_s = str(t_med_coda)
        max_t_coda_s = str(max_t_coda)
        step_sim_s = str(step_sim)

        t.write(str(x) + " " + step_sim_s + "\n")

        vm.write(str(x) + " " + vm_s + "\n")

        f.write(str(x) + " " + f_s + "\n")

        cm.write(str(x) + " " + cm_s + " " + cx_s + "\n")

        t_coda.write(str(x) + " " + max_t_coda_s + " " + t_med_coda_s + "\n")

        consumo_max_s = str(consumo_max)
        consumo_med_s = str(consumo_med)
        cons.write(str(x) + " " + consumo_max_s + " " + consumo_med_s + "\n")

t.close()
f.close()
cm.close()
vm.close()
t_coda.close()
cons.close()
print("\n\n\n\n\n\n\n")
print("FINE")
