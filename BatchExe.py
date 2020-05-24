import BatchLib
#
#
# -------------------- VARIABILI MODIFICABILI -------------------- #

from_auto_test = 100  # (per simulazione impostare a 10)
to_auto_test = 100  # (per simulazione impostare a 100 o 200 se abbasatanza efficente)
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
        BatchLib.run(n_porta_base + x, x, tempo_generazione, gui, max_auto_insieme)

print("\n\n\n\n\n\n\n")
print("FINE")
