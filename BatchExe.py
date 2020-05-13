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

from_auto_test = 50  # (per simulazione impostare a 10)
to_auto_test = 200  # (per simulazione impostare a 100 o 200 se abbasatanza efficente)
step_auto_test = 50  # (per simulazione impostare a 10)
prove_fissate_auto = 20  # (per simulazione impostare a 10)
gui = False
n_porta_base = 5000
prove_una_auto = 40  # (per simulazione impostare a 20)

# ---------------------------------------------------------------- #
#
#

tempo_generazione = 600 / 8.33  # fissato
step0 = 0
step_sim = 0
consumo0 = 0

# eseguo prove per rilevare tempo in condizione standard, con una sola auto
for y in range(0, prove_una_auto):
    n_port = n_porta_base + y + 1
    ret = BatchLib.run(n_port, 1, tempo_generazione, False)
    # ret = BatchLib.run(n_port, 1, tempo_generazione, False, max_auto_insieme)
    step_sim += float(ret[4])
    consumo0 += float(ret[7])

step_sim = round(float(step_sim) / float(prove_una_auto), 4)
consumo0 = round(float(consumo0) / float(prove_una_auto), 4)
step0 = step_sim  # salvo tempo in situazione base, 1 sola auto senza fermarsi

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
        max_t_coda = round(float(max_t_coda) / float(step_sim), 4)  # tempo massimo in coda rispetto al tempo tot di sim
        t_med_coda = round(float(t_med_coda) / float(prove_fissate_auto), 4)
        t_med_coda = round(float(t_med_coda) / float(step_sim), 4)  # tempo medio in coda rispetto al tempo tot di sim

        # calcolo consimo medio e massimo rispetto al consumo calcolato in assenza di congestione
        consumo_max = round(float(consumo_max) / float(prove_fissate_auto), 4)
        consumo_max = round(float(consumo_max) / float(consumo0), 4)
        consumo_med = round(float(consumo_med) / float(prove_fissate_auto), 4)
        consumo_med = round(float(consumo_med) / float(consumo0), 4)

        f_s = str(f_t)
        vm_s = str(vm_t)
        cm_s = str(cm_t)
        cx_s = str(cx_t)
        t_med_coda_s = str(t_med_coda)
        max_t_coda_s = str(max_t_coda)

        string_vett = vm_s.rsplit(".")
        vm.write(str(x) + " " + string_vett[0] + "," + string_vett[1] + "\n")

        string_vett = f_s.rsplit(".")
        f.write(str(x) + " " + string_vett[0] + "," + string_vett[1] + "\n")

        string_vett1 = cm_s.rsplit(".")
        string_vett2 = cx_s.rsplit(".")
        cm.write(str(x) + " " + string_vett1[0] + "," + string_vett1[1] + " " + string_vett2[0] + "," + string_vett2[
            1] + "\n")

        # creare percentuale relativa al step0
        perc = round((float(step_sim) / float(step0)) - 1,
                     4)  # calcolo percentuale rispetto situazione di base (1 auto)
        step_sim_s = str(perc)
        string_vett = step_sim_s.rsplit(".")
        if perc > 0:  # inserisco segno + se non c'e'
            t.write(str(x) + " +" + string_vett[0] + "," + string_vett[1] + "\n")
        else:
            t.write(str(x) + " " + string_vett[0] + "," + string_vett[1] + "\n")

        string_vett1 = max_t_coda_s.rsplit(".")
        string_vett2 = t_med_coda_s.rsplit(".")
        t_coda.write(
            str(x) + " " + string_vett1[0] + "," + string_vett1[1] + " " + string_vett2[0] + "," + string_vett2[
                1] + "\n")

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

t.close()
f.close()
cm.close()
vm.close()
t_coda.close()
cons.close()
print("\n\n\n\n\n\n\n")
print("FINE")
