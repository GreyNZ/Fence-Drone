from copy import copy
import time
import numpy as np


######    QUESTION 1 Project Euler     #####

def multiples_3and5(target):
    """
    If we list all the natural numbers below 10 that are multiples of 3 or 5, we get 3, 5, 6 and 9. The sum of these multiples is 23.
    Find the sum of all the multiples of 3 or 5 below 1000.
    """
    t0 = time.time()
    total = 0
    for i in range(2,target):
        if i % 3 == 0 or i % 5 == 0:
            total += i
    time_taken = time.time() - t0
    return total, time_taken




######    QUESTION 5 Project Euler     #####

def smallest_div_brute(val):
    """
    2520 is the smallest number that can be divided by each of the numbers from 1 to 10 without any remainder.
    What is the smallest positive number that is evenly divisible by all of the numbers from 1 to 20?
    """
    found = False
    current = val # no point checking numbers less than largest number
    numbers = [i for i in range(2,val+1)] # no point checking 0,1
    t0 = time.time()
    while not found:
        if len([i for i in numbers if current % i != 0]) == 0:
            found = True
        else:
            current += 1
    time_taken = time.time() - t0
    return current, time_taken





def janky_KN_primes(val):
    """
    2520 is the smallest number that can be divided by each of the numbers from 1 to 10 without any remainder.
    What is the smallest positive number that is evenly divisible by all of the numbers from 1 to 20?
    using barely remebered discrete math from 1st year......
    """
    found = False
    current = val # no point checking numbers less than largest number
    numbers = [i for i in range(2,val+1)] # no point checking 0,1
    kn_numbers = copy(numbers)
    t0 = time.time()
    for i in numbers: # this loop lowers the numbers to check by removing numbers accounted for in larger numbers eg if number is divisible by 100 its also divisible by 10
        for j in numbers:
            if i != j and j % i == 0:
                try:
                    kn_numbers.remove(i)
                except ValueError:
                    pass
    while not found:
        if len([i for i in kn_numbers if current % i != 0]) == 0:
            found = True
        else:
            current += 1
    time_taken = time.time() - t0
    return current, time_taken



######    QUESTION 10 Project Euler     #####

def sum_primes_brute(val):
    """
    The sum of the primes below 10 is 2 + 3 + 5 + 7 = 17.
    Find the sum of all the primes below two million.
    """
    total = 2 #just starting with 2 as its prime assuming target over 2 this lets me filter even numbers as they are not prime (half computation time)
    t0 = time.time()
    for candidate in range(3,val+1, 2): #filters out even numbers
        prime = True
        for i in range(2,int(np.sqrt(candidate).round()) + 1): #only check to root of candidate
            if candidate % i == 0:
                prime = False
        if prime:
            total += candidate
    print(f"time taken: {time.time() - t0}")
    print(f"total: {total}")



### Sieve

def sievePrimes(target):
    """I used the internet for help on this one, couldent think how to make it much faster tan v1"""
    t0 = time.time()
    sum, sieve = 0, [True] * target
    for p in range(2, target):
        if sieve[p]:
            sum += p
            for i in range(p*p, target, p):
                sieve[i] = False
    time_taken = time.time() - t0
    return sum, time_taken


def main():
    a, b = sievePrimes(2000000)
    print(f"sievePrimes(2000000): {a}\nTime taken: {b}\n")

main()

