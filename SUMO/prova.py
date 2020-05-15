step_len = 0.072
step = 0.0
for i in range(0, 100):
    step += step_len
    # print(step / step_len)
    if int(step / step_len) % 2 == 0:
        print(i)
        print("")
