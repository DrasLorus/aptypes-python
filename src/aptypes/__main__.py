from itertools import product as cartesian
import sys
import os
import hashlib

import numpy

from . import *

def pretty_print(a, b, file = sys.stdout):
    print(a, ':', b, file = file)

def pretty_print_couple(expr, file = sys.stdout):
    val_b = eval(expr)
    pretty_print(expr, '(' + str(val_b[0]) + ', ' + str(val_b[1]) + ')', file = file)
    return val_b

def check_equalty(expr, file = sys.stdout):
    val_x = pretty_print_couple(expr, file = file)
    print(' -- ', val_x[0] == val_x[1].value, file = file)

def tuple_former(x, c, W, I):
    return (x, c(x, W, I))

def tuple_auto_bits(x, c):
    return tuple_former(x, c, None, None)

def auto_eval_tuple(x: tuple, y: tuple, f):
    return (eval(f'x[0] {f} y[0]'), eval(f'x[1] {f} y[1]'))

def test_run(seed = 0, file = sys.stdout):
    rng = numpy.random.default_rng(seed = seed)

    a0 = eval((val_s := 'tuple_auto_bits(562.4, APFixed)'))
    pretty_print_couple(val_s, file = file)
    a1 = eval((val_s := 'tuple_auto_bits(562.4, APUfixed)'))
    pretty_print_couple(val_s, file = file)
    a2 = eval((val_s := 'tuple_former(156.21, APUfixed, 12, None)'))
    pretty_print_couple(val_s, file = file)
    b0 = eval((val_s := 'tuple_auto_bits(-89., APFixed)'))
    pretty_print_couple(val_s, file = file)
    b1 = eval((val_s := 'tuple_auto_bits(-9.9654, APFixed)'))
    pretty_print_couple(val_s, file = file)
    b2 = eval((val_s := 'tuple_former(156.21, APFixed, 12, None)'))
    pretty_print_couple(val_s, file = file)

    print(repr(a0[1]), file = file)

    val_a = [a0, a1, a2]
    val_b = [b0, b1, b2]

    rar = tuple_former(-2, APFixed, 2, 2)

    vec = []
    for a,b,o in cartesian(val_a, val_b,["'+'", "'-'", "'*'"]):

        val_s = f"auto_eval_tuple({a}, {b}, {o})".replace('Signed', 'APFixed').replace('Unsigned', 'APUfixed')
        try:
            vec.append(pretty_print_couple(val_s, file = file))
        #pylint: disable-next=broad-exception-caught
        except Exception:
            print(val_s, '=> Error', file = file)

    print(f'{rar[1].value} : {rar[1].bin}', file = file)
    print(f'{vec[0][1].value} : {vec[0][1].bin}', file = file)
    print(f'{b1[1].value} : {b1[1].bin}', file = file)

    bbb = APFixed(0, 8, 3)
    try:
        bbb.saturate(8)
    except ValueError:
        print('ValueError successfully detected', file = file)

    val_s = 'APUfixed(vec[8][1].truncate(18)).truncate(3, lsb=False)'
    pretty_print(val_s, eval(val_s), file = file)

    try:
        gg = eval(val_s)
        _ = -gg
    except NotImplementedError:
        print('NotImplementedError successfully detected', file = file)

    val_s = 'vec[8][1].truncate(18).saturate(14)'
    e1    = eval(val_s)
    print('e1 = ', end='', file = file)
    pretty_print(val_s, eval(val_s), file = file)

    pretty_print('APUfixed(e1).saturate(1)', eval('APUfixed(e1).saturate(1)'), file = file)

    val_s = 'tuple_auto_bits(-1. + 56.j, APComplex)'
    pretty_print(val_s, eval(val_s), file = file)

    val_s = 'tuple_auto_bits((-1., 56.), APComplex)'
    pretty_print(val_s, eval(val_s), file = file)

    for val_x in rng.random((20, 2)):
        x, y = numpy.round(val_x * (2**3 - 1) * 2 - (2**3 - 1)) / 2
        _, y = numpy.round(val_x * (2**4 - 1) * 2 - (2**4 - 1))
        val_s = f'({x:.1f} * {y:.1f}, APFixed({x:.1f}, 4, 3) * APFixed({y:.1f}, 5, 5))'
        check_equalty(val_s, file = file)

    for val_x in rng.random((20, 4)):
        re0, im0, _, _ = numpy.round(val_x * (2**3 - 1) * 2 - (2**3 - 1)) / 2
        _, _, re1, im1 = numpy.round(val_x * (2**4 - 1) * 2 - (2**4 - 1))
        val_s = f'(({re0:.1f}+{im0:.1f}j) * ({re1:.1f}+{im1:.1f}j), APComplex({re0:.1f}+{im0:.1f}j, 4, 3) * APComplex({re1:.1f}+{im1:.1f}j, 5, 5))'
        check_equalty(val_s, file = file)

    for val_x in rng.random((20, 3)):
        re0, im0, _ = numpy.round(val_x * (2**3 - 1) * 2 - (2**3 - 1)) / 2
        _, _, val = numpy.round(val_x * (2**4 - 1) * 2 - (2**4 - 1))
        val_s = f'(({re0:.1f}+{im0:.1f}j) * {val:.1f}, APComplex({re0:.1f}+{im0:.1f}j, 4, 3) * APFixed({val:.1f}, 5, 5))'
        check_equalty(val_s, file = file)

    for val_x in rng.random((20, 4)):
        re0, im0, _, _ = numpy.round(val_x * (2**4 - 1)) / 2
        _, _, re1, im1 = numpy.round(val_x * (2**5 - 1))
        val_s = f'(({re0:.1f}+{im0:.1f}j) * ({re1:.1f}+{im1:.1f}j), APUcomplex({re0:.1f}+{im0:.1f}j, 4, 3) * APUcomplex({re1:.1f}+{im1:.1f}j, 5, 5))'
        try:
            check_equalty(val_s, file = file)
        except ValueError:
            pretty_print(val_s, (eval(val_s[1:].split(",")[0]), "Error: Negative result"), file = file)

    for val_x in rng.random((20, 3)):
        re0, im0, _ = numpy.round(val_x * (2**4 - 1)) / 2
        _, _, val = numpy.round(val_x * (2**5 - 1))
        val_s = f'(({re0:.1f}+{im0:.1f}j) * {val:.1f}, APUcomplex({re0:.1f}+{im0:.1f}j, 4, 3) * APUfixed({val:.1f}, 5, 5))'
        check_equalty(val_s, file = file)

    ###

    for val_x in rng.random((20, 4)):
        re0, im0, _, _ = numpy.round(val_x * (2**3 - 1) * 2 - (2**3 - 1)) / 2
        _, _, re1, im1 = numpy.round(val_x * (2**4 - 1) * 2 - (2**4 - 1))
        val_s = f'(({re0:.1f}+{im0:.1f}j) + ({re1:.1f}+{im1:.1f}j), APComplex({re0:.1f}+{im0:.1f}j, 4, 3) + APComplex({re1:.1f}+{im1:.1f}j, 5, 5))'
        check_equalty(val_s, file = file)

    for val_x in rng.random((20, 4)):
        re0, im0, _, _ = numpy.round(val_x * (2**3 - 1) * 2 - (2**3 - 1)) / 2
        _, _, re1, im1 = numpy.round(val_x * (2**4 - 1) * 2 - (2**4 - 1))
        val_s = f'(({re0:.1f}+{im0:.1f}j) - ({re1:.1f}+{im1:.1f}j), APComplex({re0:.1f}+{im0:.1f}j, 4, 3) - APComplex({re1:.1f}+{im1:.1f}j, 5, 5))'
        check_equalty(val_s, file = file)

    for val_x in rng.random((20, 3)):
        re0, im0, _ = numpy.round(val_x * (2**3 - 1) * 2 - (2**3 - 1)) / 2
        _, _, val = numpy.round(val_x * (2**4 - 1) * 2 - (2**4 - 1))
        val_s = f'(({re0:.1f}+{im0:.1f}j) + {val:.1f}, APComplex({re0:.1f}+{im0:.1f}j, 4, 3) + APFixed({val:.1f}, 5, 5))'
        check_equalty(val_s, file = file)

    for val_x in numpy.abs(rng.random((20, 4))):
        re0, im0, _, _ = numpy.round(val_x * (2**4 - 1)) / 2
        _, _, re1, im1 = numpy.round(val_x * (2**5 - 1))
        val_s = f'(({re0:.1f}+{im0:.1f}j) + ({re1:.1f}+{im1:.1f}j), APUcomplex({re0:.1f}+{im0:.1f}j, 4, 3) + APUcomplex({re1:.1f}+{im1:.1f}j, 5, 5))'
        try:
            check_equalty(val_s, file = file)
        except ValueError:
            pretty_print(val_s, (eval(val_s[1:].split(",")[0]), "Error: Negative result"), file = file)

    for val_x in rng.random((20, 3)):
        re0, im0, _ = numpy.round(val_x * (2**4 - 1)) / 2
        _, _, val = numpy.round(val_x * (2**5 - 1))
        val_s = f'(({re0:.1f}+{im0:.1f}j) + {val:.1f}, APUcomplex({re0:.1f}+{im0:.1f}j, 4, 3) + APUfixed({val:.1f}, 5, 5))'
        check_equalty(val_s, file = file)

    print(APFixed(-2**3, 4, 4, scaling='external').bitstrained_add(-1.5, 7, 5), file = file)

    print('ok', file = file)

def log(file: str):
    with open(file, 'w', encoding='utf-8') as f:
        test_run(seed = 4568, file = f)

if __name__ == '__main__':
    ORIGINAL_SHA256 = 'f305e3e4baa658729a24290dd98e8cc2cb78b0de996036b12a2cd082ce8167d8'

    log('output.dat')

    with open('output.dat', 'rb') as output:
        output_data   = output.read()
        output_sha256 = hashlib.sha256(output_data).hexdigest()

    if ORIGINAL_SHA256 == output_sha256:
        print('\033[32;1m-- SUCCESS --\033[0m')
        os.remove('output.dat')
    else:
        print('\033[31;1m-- FAILURE --\033[0m')
