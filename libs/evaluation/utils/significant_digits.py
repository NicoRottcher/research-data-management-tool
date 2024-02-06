# -*- coding: utf-8 -*-
"""
Scripts to derive significant digits
Created on Mon Dec 11 13:24:05 2023
@author: Forschungszentrum Jülich GmbH, Birk Fritsch
"""
import math


def round_half_up(n, decimals=0):
    """
    From https://realpython.com/python-rounding/
    """
    multiplier = 10**decimals
    return math.floor(n * multiplier + 0.5) / multiplier


def check_significant_digit(val, error):
    """
    Round your number based on significance after DIN 1333
    https://www2.physki.de/PhysKi/index.php/Signifikante_Stellen
    """
    n, c = 1, 0

    while error > n:
        n *= 10
        c -= 1
    while not (error / 30 <= n <= error / 3):
        n *= 0.1
        c += 1

    val = round_half_up(val, int(c))
    err = round_half_up(error, int(c))

    if val == int(val) and err == int(err):
        val = int(val)
        err = int(err)

    print(f"{val}±{err}")


#%%
if __name__ == "__main__":

    check_significant_digit(575.835435132, 0.000285)
    check_significant_digit(575.835435132, 2)
    check_significant_digit(575.835435132, 12)
    check_significant_digit(575.835435132, 66)
