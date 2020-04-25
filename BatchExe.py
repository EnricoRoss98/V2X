import BatchLib
from multiprocessing import Pool

direct = "~/SUMO/"  # percorso cartella

f = open("Output/ferme.txt", "w")  # creo file ferme.txt percentuale di auto ferme
vm = open("Output/vel_med.txt", "w")  # creo file vel_med vel. media delle auto presenti
cm = open("Output/code.txt", "w")  # creo file code contiene coda piu' lunga e n med auto in coda (%)
t = open("Output/tempo.txt", "w")  # scrivo il tempo impiegato per terminare la simulazione rispetto no code
t_coda = open("Output/t_in_coda.txt", "w")  # scrivo il tempo medio in coda rispetto al tempo tot di simulaz.

#
#
# -------------------- VARIABILI MODIFICABILI -------------------- #

from_auto_test = 10  # (per simulazione impostare a 10)
to_auto_test = 150  # (per simulazione impostare a 100 o 200 se abbasatanza efficente)
step_auto_test = 10  # (per simulazione impostare a 10)
prove_fissate_auto = 10  # (per simulazione impostare a 10)
max_auto_insieme = 12  # solo per Version4 e Versione7
gui = False
n_porta_base = 5000
prove_una_auto = 20  # (per simulazione impostare a 20)
celle_per_lato = 22  # per protocolli basati sulla suddivisione matriciale dell'incrocio

# ---------------------------------------------------------------- #
#
#

tempo_generazione = 600  # fissato
step0 = 0
step_sim = 0

# eseguo prove per rilevare tempo in condizione standard, con una sola auto
for y in range(0, prove_una_auto):
    n_port = n_porta_base + y + 1
    ret = BatchLib.run(n_port, 1, tempo_generazione, False)
    # ret = BatchLib.run(n_port, 1, tempo_generazione, False, max_auto_insieme)
    step_sim += float(ret[4])

step_sim = round(float(step_sim) / float(prove_una_auto), 4)
step0 = step_sim  # salvo tempo in situazione base, 1 sola auto senza fermarsi

for x in range(from_auto_test, to_auto_test + 1):
    if x % step_auto_test == 0:
        print("PROVE CON " + str(x) + " AUTO")
        f_t = 0.0
        vm_t = 0.0
        cm_t = 0.0
        cx_t = 0.0
        step_sim = 0.0
        t_med_coda = 0.0
        max_t_coda = 0.0

        n_auto = x

        if prove_fissate_auto == 10:
            n_port = n_porta_base
            pool = Pool(processes=10)
            p = pool.apply_async(BatchLib.run, (n_port + 0 + x, n_auto, tempo_generazione, gui))
            p1 = pool.apply_async(BatchLib.run, (n_port + 1 + x, n_auto, tempo_generazione, gui))
            p2 = pool.apply_async(BatchLib.run, (n_port + 2 + x, n_auto, tempo_generazione, gui))
            p3 = pool.apply_async(BatchLib.run, (n_port + 3 + x, n_auto, tempo_generazione, gui))
            p4 = pool.apply_async(BatchLib.run, (n_port + 4 + x, n_auto, tempo_generazione, gui))
            p5 = pool.apply_async(BatchLib.run, (n_port + 5 + x, n_auto, tempo_generazione, gui))
            p6 = pool.apply_async(BatchLib.run, (n_port + 6 + x, n_auto, tempo_generazione, gui))
            p7 = pool.apply_async(BatchLib.run, (n_port + 7 + x, n_auto, tempo_generazione, gui))
            p8 = pool.apply_async(BatchLib.run, (n_port + 8 + x, n_auto, tempo_generazione, gui))
            p9 = pool.apply_async(BatchLib.run, (n_port + 9 + x, n_auto, tempo_generazione, gui))

            ret = p.get()
            f_t += float(ret[0])
            vm_t += float(ret[1])
            cm_t += float(ret[2])
            cx_t += float(ret[3])
            step_sim += float(ret[4])
            max_t_coda += float(ret[5])
            t_med_coda += float(ret[6])

            ret = p1.get()
            f_t += float(ret[0])
            vm_t += float(ret[1])
            cm_t += float(ret[2])
            cx_t += float(ret[3])
            step_sim += float(ret[4])
            max_t_coda += float(ret[5])
            t_med_coda += float(ret[6])

            ret = p2.get()
            f_t += float(ret[0])
            vm_t += float(ret[1])
            cm_t += float(ret[2])
            cx_t += float(ret[3])
            step_sim += float(ret[4])
            max_t_coda += float(ret[5])
            t_med_coda += float(ret[6])

            ret = p3.get()
            f_t += float(ret[0])
            vm_t += float(ret[1])
            cm_t += float(ret[2])
            cx_t += float(ret[3])
            step_sim += float(ret[4])
            max_t_coda += float(ret[5])
            t_med_coda += float(ret[6])

            ret = p4.get()
            f_t += float(ret[0])
            vm_t += float(ret[1])
            cm_t += float(ret[2])
            cx_t += float(ret[3])
            step_sim += float(ret[4])
            max_t_coda += float(ret[5])
            t_med_coda += float(ret[6])

            ret = p5.get()
            f_t += float(ret[0])
            vm_t += float(ret[1])
            cm_t += float(ret[2])
            cx_t += float(ret[3])
            step_sim += float(ret[4])
            max_t_coda += float(ret[5])
            t_med_coda += float(ret[6])

            ret = p6.get()
            f_t += float(ret[0])
            vm_t += float(ret[1])
            cm_t += float(ret[2])
            cx_t += float(ret[3])
            step_sim += float(ret[4])
            max_t_coda += float(ret[5])
            t_med_coda += float(ret[6])

            ret = p7.get()
            f_t += float(ret[0])
            vm_t += float(ret[1])
            cm_t += float(ret[2])
            cx_t += float(ret[3])
            step_sim += float(ret[4])
            max_t_coda += float(ret[5])
            t_med_coda += float(ret[6])

            ret = p8.get()
            f_t += float(ret[0])
            vm_t += float(ret[1])
            cm_t += float(ret[2])
            cx_t += float(ret[3])
            step_sim += float(ret[4])
            max_t_coda += float(ret[5])
            t_med_coda += float(ret[6])

            ret = p9.get()
            f_t += float(ret[0])
            vm_t += float(ret[1])
            cm_t += float(ret[2])
            cx_t += float(ret[3])
            step_sim += float(ret[4])
            max_t_coda += float(ret[5])
            t_med_coda += float(ret[6])

        else:
            for y in range(0, prove_fissate_auto):
                print("")
                print("ESEGUO PROVA " + str(y + 1) + " CON " + str(x) + " AUTO...")

                n_port = n_porta_base + (x * step_auto_test) + y
                ret = BatchLib.run(n_port, n_auto, tempo_generazione, gui, celle_per_lato, traiettorie_matrice)

                f_t += float(ret[0])
                vm_t += float(ret[1])
                cm_t += float(ret[2])
                cx_t += float(ret[3])
                step_sim += float(ret[4])
                max_t_coda += float(ret[5])
                t_med_coda += float(ret[6])

        f_t = round(float(f_t) / float(prove_fissate_auto), 4)
        vm_t = round(float(vm_t) / float(prove_fissate_auto), 4)
        cm_t = round(float(cm_t) / float(prove_fissate_auto), 4)
        cx_t = round(float(cx_t) / float(prove_fissate_auto), 4)
        step_sim = round(float(step_sim) / float(prove_fissate_auto), 4)

        max_t_coda = round(float(max_t_coda) / float(prove_fissate_auto), 4)
        max_t_coda = round(float(max_t_coda) / float(step_sim), 4)  # tempo massimo in coda rispetto al tempo tot di sim
        t_med_coda = round(float(t_med_coda) / float(prove_fissate_auto), 4)
        t_med_coda = round(float(t_med_coda) / float(step_sim), 4)  # tempo medio in coda rispetto al tempo tot di sim

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

t.close()
f.close()
cm.close()
vm.close()
t_coda.close()
print("\n\n\n\n\n\n\n")
print("FINE")
