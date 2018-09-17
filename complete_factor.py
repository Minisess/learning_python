"""
A short python program that defines two functions for finding the factors of a number

factor_once: which breaks an int into two factors
factor_completely: which breaks an int into a list of prime factors
"""


from math import sqrt


def factor_once(fac: int)-> list:
    """
    factors any integer into a series of tuples containing two factors each
    is used by the factor completely function
    """
    results = [(1, fac)]
    for fact1 in range(1, int(sqrt(fac)) + 1):
        for fact2 in range(1, int((fac / 2) + 1)):
            if fact1 * fact2 == fac:
                results.append((fact1, fact2))

    return results


def factor_completely(int_to_factor: int)-> list:
    """
    depends on factor_once function
    loops over every factor of a number and break it down into a list of only prime numbers needed to be multiplied together

    :param int_to_factor: needs to be an whole number
    :return: returns a list of prime numbers that need to be multiplied to produce the original number
    """
    step_one = factor_once(int_to_factor).pop()
    if len(step_one) == 1:
        return [x for x in step_one]
    beginning = step_one
    while True:
        results = []
        for factor in beginning:
            next_step = list(factor_once(factor).pop())
            if 1 in next_step:
                next_step.remove(1)
            results.extend(list(next_step))
        if len(results) == len(beginning):
            break
        beginning = results
    return results

