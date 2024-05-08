def fetkovich():
    pass



# vogel
def alternate_pwf_pr(pwf, pr):
    pwfdivpr = pwf / pr
    return pwfdivpr


llamada = alternate_pwf_pr(1765, 2085)
print(llamada)



def q_max(qo):
    qomax = qo * (1 - 0.2 * (alternate_pwf_pr(1765, 2085)) - 0.8 * (alternate_pwf_pr(1765, 2085)) ** 2)
    return qomax


llamada = q_max(282)
print(llamada)


# practice
def productivity_index(qo, pr, pwf):
    j = qo / (pr - pwf)
    return j


llamada = productivity_index(282, 2085, 1765)
print(llamada)
def ipr():
    pass
