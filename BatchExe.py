import BatchLib
import Traiettorie
from multiprocessing import Pool

direct = "~/SUMO/"  # percorso cartella

#
#
# -------------------- VARIABILI MODIFICABILI -------------------- #

from_auto_test = 100  # (per simulazione impostare a 10)
to_auto_test = 100  # (per simulazione impostare a 100 o 200 se abbasatanza efficente)
step_auto_test = 50  # (per simulazione impostare a 10)
prove_fissate_auto = 1  # (per simulazione impostare a 10)
gui = True
n_porta_base = 5000
celle_per_lato = 20  # per protocolli basati sulla suddivisione matriciale dell'incrocio
secondi_di_sicurezza = 0.6

# ---------------------------------------------------------------- #
#
#

tempo_generazione = 43.2  # fissato

traiettorie_matrice = Traiettorie.run(n_porta_base, False, celle_per_lato)

for x in range(from_auto_test, to_auto_test + 1):
    if x % step_auto_test == 0:
        print("PROVE CON " + str(x) + " AUTO")
        n_auto = x

        n_port = n_porta_base
        BatchLib.run(n_port + x, n_auto, tempo_generazione, gui, celle_per_lato, traiettorie_matrice,
                     secondi_di_sicurezza)

print("\n\n\n\n\n\n\n")
print("FINE")
