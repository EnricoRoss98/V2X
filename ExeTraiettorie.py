import Traiettorie

#
#
# -------------------- VARIABILI MODIFICABILI -------------------- #

from_auto_test = 10  # (per simulazione impostare a 10)
to_auto_test = 200  # (per simulazione impostare a 100 o 200 se abbasatanza efficente)
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

traiettorie_matrice = Traiettorie.run(n_porta_base, gui, celle_per_lato)
for x in traiettorie_matrice:
    print(x)
