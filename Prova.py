import math

celle_occupate = []
ang = 90 % 180
ang = - ang
x_auto = 3 * 0.75
y_auto = 5 * 0.75
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
a1 = [round(a1[0] * math.cos(ang) - a1[1] * math.sin(ang), 4), round(a1[0] * math.sin(ang) + a1[1] * math.cos(ang), 4)]
a2 = [round(a2[0] * math.cos(ang) - a2[1] * math.sin(ang), 4), round(a2[0] * math.sin(ang) + a2[1] * math.cos(ang), 4)]
b1 = [round(b1[0] * math.cos(ang) - b1[1] * math.sin(ang), 4), round(b1[0] * math.sin(ang) + b1[1] * math.cos(ang), 4)]
b2 = [round(b2[0] * math.cos(ang) - b2[1] * math.sin(ang), 4), round(b2[0] * math.sin(ang) + b2[1] * math.cos(ang), 4)]
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
