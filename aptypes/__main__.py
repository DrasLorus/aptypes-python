import numpy

from itertools import product as cartesian

from . import *

def prettyPrint(a, b):
    print(a, ':', b)

def prettyPrintCouple(expr):
    B = eval(expr)
    prettyPrint(expr, '(' + str(B[0]) + ', ' + str(B[1]) + ')')
    return B
    
def checkEqualty(expr):
    X = prettyPrintCouple(expr)
    print(' -- ', X[0] == X[1].value)

def fntF(x, c, W, I):
    return (x, c(x, W, I))

def fntS(x, c):
    return fntF(x, c, None, None)

def fun(x: tuple, y: tuple, f):
    return (eval(f'x[0] {f} y[0]'), eval(f'x[1] {f} y[1]'))

def main():


    a0 = eval((S := 'fntS(562.4, APFixed)'))
    prettyPrintCouple(S)
    a1 = eval((S := 'fntS(562.4, APUfixed)'))
    prettyPrintCouple(S)
    a2 = eval((S := 'fntF(156.21, APUfixed, 12, None)'))
    prettyPrintCouple(S)
    b0 = eval((S := 'fntS(-89., APFixed)'))
    prettyPrintCouple(S)
    b1 = eval((S := 'fntS(-9.9654, APFixed)'))
    prettyPrintCouple(S)
    b2 = eval((S := 'fntF(156.21, APFixed, 12, None)'))
    prettyPrintCouple(S)

    A = [a0, a1, a2]
    B = [b0, b1, b2]

    rar = fntF(-2, APFixed, 2, 2)


    vec = []
    for a,b,o in cartesian(A, B,["'+'", "'-'", "'*'"]):
        S = f"fun({a}, {b}, {o})"
        try:
            vec.append(prettyPrintCouple(S))
        except Exception:
            print(S, '=> Error')

    print(f'{rar[1].value} : {rar[1].bin}')
    print(f'{vec[0][1].value} : {vec[0][1].bin}')
    print(f'{b1[1].value} : {b1[1].bin}')

    bbb = APFixed(0, 8, 3)
    try:
        bbb.saturate(8)
    except ValueError:
        print('ValueError successfully detected')

    S = 'APUfixed(vec[8][1].truncate(18)).truncate(3, lsb=False)'
    prettyPrint(S, eval(S))

    try:
        gg = eval(S)
        ggg = -gg
    except NotImplementedError:
        print('NotImplementedError successfully detected')

    S = 'vec[8][1].truncate(18).saturate(14)'
    e1 = eval(S)
    print('e1 = ', end='')
    prettyPrint(S, eval(S))

    prettyPrint('APUfixed(e1).saturate(1)', eval('APUfixed(e1).saturate(1)'))

    S = 'fntS(-1. + 56.j, APComplex)'
    prettyPrint(S, eval(S))

    S = 'fntS((-1., 56.), APComplex)'
    prettyPrint(S, eval(S))

    for X in numpy.random.random_sample((20, 2)):
        x, y = numpy.round(X * (2**3 - 1) * 2 - (2**3 - 1)) / 2
        _, y = numpy.round(X * (2**4 - 1) * 2 - (2**4 - 1))
        S = f'({x:.1f} * {y:.1f}, APFixed({x:.1f}, 4, 3) * APFixed({y:.1f}, 5, 5))'
        checkEqualty(S)

    for X in numpy.random.random_sample((20, 4)):
        re0, im0, _, _ = numpy.round(X * (2**3 - 1) * 2 - (2**3 - 1)) / 2
        _, _, re1, im1 = numpy.round(X * (2**4 - 1) * 2 - (2**4 - 1))
        S = f'(({re0:.1f}+{im0:.1f}j) * ({re1:.1f}+{im1:.1f}j), APComplex({re0:.1f}+{im0:.1f}j, 4, 3) * APComplex({re1:.1f}+{im1:.1f}j, 5, 5))'
        checkEqualty(S)

    for X in numpy.random.random_sample((20, 3)):
        re0, im0, _ = numpy.round(X * (2**3 - 1) * 2 - (2**3 - 1)) / 2
        _, _, val = numpy.round(X * (2**4 - 1) * 2 - (2**4 - 1))
        S = f'(({re0:.1f}+{im0:.1f}j) * {val:.1f}, APComplex({re0:.1f}+{im0:.1f}j, 4, 3) * APFixed({val:.1f}, 5, 5))'
        checkEqualty(S)

    for X in numpy.random.random_sample((20, 4)):
        re0, im0, _, _ = numpy.round(X * (2**4 - 1)) / 2
        _, _, re1, im1 = numpy.round(X * (2**5 - 1))
        S = f'(({re0:.1f}+{im0:.1f}j) * ({re1:.1f}+{im1:.1f}j), APUcomplex({re0:.1f}+{im0:.1f}j, 4, 3) * APUcomplex({re1:.1f}+{im1:.1f}j, 5, 5))'
        try:
            checkEqualty(S)
        except ValueError:
            prettyPrint(S, (eval(S[1:].split(",")[0]), "Error: Negative result"))

    for X in numpy.random.random_sample((20, 3)):
        re0, im0, _ = numpy.round(X * (2**4 - 1)) / 2
        _, _, val = numpy.round(X * (2**5 - 1))
        S = f'(({re0:.1f}+{im0:.1f}j) * {val:.1f}, APUcomplex({re0:.1f}+{im0:.1f}j, 4, 3) * APUfixed({val:.1f}, 5, 5))'
        checkEqualty(S)

###

    for X in numpy.random.random_sample((20, 4)):
        re0, im0, _, _ = numpy.round(X * (2**3 - 1) * 2 - (2**3 - 1)) / 2
        _, _, re1, im1 = numpy.round(X * (2**4 - 1) * 2 - (2**4 - 1))
        S = f'(({re0:.1f}+{im0:.1f}j) + ({re1:.1f}+{im1:.1f}j), APComplex({re0:.1f}+{im0:.1f}j, 4, 3) + APComplex({re1:.1f}+{im1:.1f}j, 5, 5))'
        checkEqualty(S)

    for X in numpy.random.random_sample((20, 4)):
        re0, im0, _, _ = numpy.round(X * (2**3 - 1) * 2 - (2**3 - 1)) / 2
        _, _, re1, im1 = numpy.round(X * (2**4 - 1) * 2 - (2**4 - 1))
        S = f'(({re0:.1f}+{im0:.1f}j) - ({re1:.1f}+{im1:.1f}j), APComplex({re0:.1f}+{im0:.1f}j, 4, 3) - APComplex({re1:.1f}+{im1:.1f}j, 5, 5))'
        checkEqualty(S)

    for X in numpy.random.random_sample((20, 3)):
        re0, im0, _ = numpy.round(X * (2**3 - 1) * 2 - (2**3 - 1)) / 2
        _, _, val = numpy.round(X * (2**4 - 1) * 2 - (2**4 - 1))
        S = f'(({re0:.1f}+{im0:.1f}j) + {val:.1f}, APComplex({re0:.1f}+{im0:.1f}j, 4, 3) + APFixed({val:.1f}, 5, 5))'
        checkEqualty(S)

    for X in numpy.abs(numpy.random.random_sample((20, 4))):
        re0, im0, _, _ = numpy.round(X * (2**4 - 1)) / 2
        _, _, re1, im1 = numpy.round(X * (2**5 - 1))
        S = f'(({re0:.1f}+{im0:.1f}j) + ({re1:.1f}+{im1:.1f}j), APUcomplex({re0:.1f}+{im0:.1f}j, 4, 3) + APUcomplex({re1:.1f}+{im1:.1f}j, 5, 5))'
        try:
            checkEqualty(S)
        except ValueError:
            prettyPrint(S, (eval(S[1:].split(",")[0]), "Error: Negative result"))

    for X in numpy.random.random_sample((20, 3)):
        re0, im0, _ = numpy.round(X * (2**4 - 1)) / 2
        _, _, val = numpy.round(X * (2**5 - 1))
        S = f'(({re0:.1f}+{im0:.1f}j) + {val:.1f}, APUcomplex({re0:.1f}+{im0:.1f}j, 4, 3) + APUfixed({val:.1f}, 5, 5))'
        checkEqualty(S)

    print(APFixed(-2**3, 4, 4, scaling='external').__add__(-1.5, 7, 5))

    print('ok')


if __name__ == '__main__':
    main()