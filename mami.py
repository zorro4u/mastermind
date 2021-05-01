""" mastermind (console)

    Setup
    - code maker and code solver
    - manuel or automatic mode
    - changeable number of characters and columns
    - with or without repetition of characters
    - digits or letters encoded
    - automatic feedback
    - changeable solver strategy
    - seperate statistic mode available

    Solver Strategy
    - randomly selected item from possible variants
    - Knuth algoritm

    python 3.9, standard module
    github.com/stevie7g
"""
import time
import random
from itertools import product, permutations as perm
from collections import Counter
from statistics import median
from math import factorial as fact
from os import system
system("color")

class setup_values:
    """ contains global values for initial setup
    """
    CHAR       = 6
    COLUMNS    = 4
    LIMIT      = 10
    AUTOPLAY1  = True    # the code maker, automatic
    AUTOPLAY2  = True    # the code solver, automatic
    NUMBERS    = False    # digits (or letters) as character: yes
    REPETITION = True    # repetition of a character: yes
    STATISTIC  = False   # a special mode to determine avg of guesses
    KNUTH      = False   # use the Knuth solver, max 5 guesses (6*4), slowly

    letters  = 'abcdefghijklmnopqrstuvwxyz'.upper()
    digits   = '1234567890'

m = setup_values         # rename for easier use

# ==========================================================
def run_mastermind():
    """ Mastermind core routine
    """
    silent = m.STATISTIC

    # determines all solutions
    allvariants = gen_allvariants()
    variants    = allvariants.copy()

    # generates a random code to be found
    if silent or m.AUTOPLAY1:
        code = gen_variant()
    else:
        code = input_seq('Code : ',1)

    step, black = 0, 0
    while black < m.COLUMNS and step < m.LIMIT:
        step += 1

        # gets a guess
        if silent or m.AUTOPLAY2:
            guess = get_guess(step, variants, allvariants)
        else:
            guess = input_seq('<?> :  ')

        # gets a feedback for 'guess' vs. 'code'
        answer = black, white = feedback(guess, code)

        # Filters out those with the same answer pattern for the current attempt from the current variant pool.
        # The current attempt is omitted. The right variant will always be there until the end.
        variants = [vari for vari in variants if feedback(vari,guess) == answer]

        if not silent: show_guess(step, guess, variants, answer)
    else:
        if black != m.COLUMNS and not silent: show_gameover(code)

    return step


# ==========================================================

def gen_allvariants():
    """ generates a string set of all possible variants
        from 'char_set' with the number of 'columns'
        w/  repetition: allVariants = char ** columns                             = len(variants)
        w/o repetition: allVariants = factorial(char) // factorial(char-columns)  = len(variants)
    """
    if m.REPETITION:
        vari = product(m.char_set, repeat=m.COLUMNS)         # w/  rep. __ string tuple of variants
    else:
        vari = perm(m.char_set, m.COLUMNS)                   # w/o rep. __ string tuple of variants
    return [''.join(single_char) for single_char in vari]    # string list of all variants, tuple dissolve and merge


def gen_variant():
    """ generates a random variant as a string
        from 'char_set' with the number of 'columns'
    """
    if m.REPETITION:
        seq = random.choices(m.char_set, k=m.COLUMNS)  # w/ rep., list of char
    else:
        seq = random.sample(m.char_set, m.COLUMNS)     # w/o rep.
    return ''.join(map(str, seq))                      # string


def get_variant(variants):
    """ selects a random element from the 'variants' list
    """
    return random.sample(variants,1)[0]                # string


def get_guess(step, variants, allvariants):
    """ selects an item from a list:
        - randomly
        - Knuth algoritm
    """
    if  not m.KNUTH:
        guess = get_variant(variants)   # a random element from the reduced variant pool
    else:                               # Knuth algorithm
        if step > 1:
            if len(variants) != 1:
                key = lambda g: max(Counter(feedback(g, _) for _ in variants).values())
                guess = min(allvariants, key=key)   # Knuth, slowly
            else:
                guess = variants[0]                 # last variant directly -> guess = code
        elif m.NUMBERS:                             # special first guess for digits/letters
            guess = ''.join(map(str,[1 if i < m.COLUMNS/2 else 2 for i in range(m.COLUMNS)]))
        else:
            guess = ''.join('A' if i < m.COLUMNS/2 else 'B' for i in range(m.COLUMNS))
    return guess


def feedback(guess, code):
    """ tests 'guess' for 'code':
        black pin: char and position are correct
        white pin: char is correct, position is wrong
    """
    # counts frequency of characters / histogram
    # returns the sum of the the smallest match
    white = sum((Counter(guess) & Counter(code)).values())

    # forms pairs from both lists [(0. 0.) (1. 1.) ...], then compares both elements
    black = sum(a==b for a,b in zip(guess, code))

    white -= black                 # avoid double counting of white (even if black)
    return black, white            # integer return; string return e.g. ('x'*black + 'o'*white)


def lenVariants():
    """
    """
    if m.REPETITION:
        lenV = m.CHAR ** m.COLUMNS
    else:
        lenV = fact(m.CHAR) // fact(m.CHAR - m.COLUMNS)
    return lenV


def check_setup():
    # max. 10 digits or 26 letters
    if m.NUMBERS and (m.CHAR > 10):       m.CHAR = 10
    elif not m.NUMBERS and m.CHAR > 26:   m.CHAR = 26

    # adjust columns
    if not m.REPETITION and (m.COLUMNS > m.CHAR): m.COLUMNS = m.CHAR

    # new character pool
    if m.NUMBERS: m.char_set = m.digits[:m.CHAR]
    else:         m.char_set = m.letters[:m.CHAR]


# ==========================================================
# Input / Output

def show_setup():
    print(
        f'{"Characters":12}: {m.CHAR}\n'
        f'{"Columns":12}: {m.COLUMNS}\n'
        f'{"Repetition":12}: {m.REPETITION}\n'
        f'{"Coder autom":12}: {m.AUTOPLAY1}\n'
        f'{"Solver auto":12}: {m.AUTOPLAY2}\n'
        f'{"Digits used":12}: {m.NUMBERS}\n'
        f'{"Knuth solver":12}: {m.KNUTH}\n'
        f'{"Statistic":12}: {m.STATISTIC}\n'
        f'{"Limit":12}: {m.LIMIT}\n'
        f'{"Solutions:":12}: {lenVariants():,.0f}\n'
        f'{"-"*24}\n'
    )


def show_guess(step, guess, variants, result):
    black, white = result
    lenVari = len(variants)
    msg01   = f'#{step:02}: "{guess}" '
    msg02   = f'-> b:{black} w:{white}'
    msg05   = '\n'
    if m.AUTOPLAY2:
        msg03 = f' | remain. {lenVari:,.0f}'
        msg04 = f': {variants}'
        msg05 = ''
    else: msg03 = msg04 = ''

    if black < m.COLUMNS and lenVari > 9:     # not yet solved and too many variants to display
        msg = msg01 + msg02 + msg03 + msg05
    elif black < m.COLUMNS:                   # not resolved yet
        msg = msg01 + msg02 + msg03 + msg04 + msg05
    else:                                     # solved
        #duration = (time.perf_counter()-starttime)*1000     #msec
        msg = (
            f'{fg.green}' + msg01 + f'{fg.reset}\n'
            f'\n{fg.green}-- Done! --{fg.reset}'
            #f'\n{fg.green}-- Done! --{fg.reset}    in {duration:,.1f} msec'
        )
    print(msg)


def show_gameover(code):
    print(
        f'\n{fg.red}-- GAME OVER --{fg.reset}\n'
        f'The code was "{code}"\n'
    )


def show_code(code=''):
    print(
        #f'{"":6}' + ' '.join(code) + '\n'
        f'{"code:":6}{"* " *m.COLUMNS}\n'
    )


def show_statistics(stati):
    lenVari  = lenVariants()
    guesses  = stati[0]
    duration = stati[1]
    alltime = stati[2]
    med1 = median(guesses)
    med2 = median(duration)
    avg1 = sum(guesses)/len(guesses)
    avg2 = sum(duration)/len(duration)
    msg  = (
        f'{fg.cyan}{"med. guesses":13}: {med1:.1f}{fg.reset}\n'
        f'{"avg. guesses":13}: {avg1:.2f}\n'
        f'{"max. guesses":13}: {max(guesses)}\n'
        f'{"min. guesses":13}: {min(guesses)}\n'
        f'{fg.cyan}{"med. msec":13}: {med2:,.1f}{fg.reset}\n'
        f'{"avg. msec":13}: {avg2:,.1f}\n'
        f'{"max. msec":13}: {max(duration):,.1f}\n'
        f'{"min. msec":13}: {min(duration):,.1f}\n'
        f'{"-"*24}\n'
        f'{"alltime sec":13}: {alltime:,.1f}\n'
    )
    print(msg, end='')


def make_setup():
    """ show and set the global values for the game
    """

    check_setup()
    show_setup()

    x = input('Change setup? <y>  : ')
    print()
    if x.lower() != 'y': return

    x = input_int(f'{"Characters":12}{fg.grey}{"<"+str(m.CHAR)+">":7}{fg.reset}: ', min=1, max=26)
    if x != '': m.CHAR = x
    x = input_int(f'{"Columns":12}{fg.grey}{"<"+str(m.COLUMNS)+">":7}{fg.reset}: ', min=1, max=100)
    if x != '': m.COLUMNS = x
    x = input_int(f'{"Repetition":12}{fg.grey}{"["+str(m.REPETITION)+"]":7}{fg.reset}: ')
    if x != '': m.REPETITION = x
    x = input_int(f'{"Coder autom":12}{fg.grey}{"["+str(m.AUTOPLAY1)+"]":7}{fg.reset}: ')
    if x != '': m.AUTOPLAY1 = x
    x = input_int(f'{"Solver auto":12}{fg.grey}{"["+str(m.AUTOPLAY2)+"]":7}{fg.reset}: ')
    if x != '': m.AUTOPLAY2 = x
    x = input_int(f'{"Digits used":12}{fg.grey}{"["+str(m.NUMBERS)+"]":7}{fg.reset}: ')
    if x != '': m.NUMBERS = x
    x = input_int(f'{"Knuth solver":12}{fg.grey}{"["+str(m.KNUTH)+"]":7}{fg.reset}: ')
    if x != '': m.KNUTH = x
    x = input_int(f'{"Statistic":12}{fg.grey}{"["+str(m.STATISTIC)+"]":7}{fg.reset}: ')
    if x != '': m.STATISTIC = x
    x = input_int(f'{"Limit":12}{fg.grey}{"<"+str(m.LIMIT)+">":7}{fg.reset}: ', min=1, max=50)
    if x != '': m.LIMIT = x

    check_setup()

    print(f'{"Solutions":19}: {lenVariants():,.0f}\n'\
        f'{"-"*30}\n')


def input_int(text, min=0, max=1):
    while True:
        try:
            x = input(text)
            if x != '':
                x = int(x)
                if x > max:
                    x = max
                    print(f'Input set to {max}')
                elif x < min:
                    x = min
                    print(f'Input set to {min}')
            return x
        except ValueError:
            print('Only digits allowed...')


def input_seq(text, newline=False):
    """ Input code/guess
    """
    while True:
        try:
            seq = input(text).upper()
            if newline: print()
            if len(seq) != m.COLUMNS:
                raise KeyboardInterrupt('Input to short/long...\n')
            for char in seq:
                if char not in m.char_set: raise KeyboardInterrupt('Input not in char set...\n')
            return seq
        except KeyboardInterrupt as error: print(error)


class fg:     #ansi escape foreground color (30-37)/90-97
    grey    = '\033[90m'
    red     = '\033[91m'
    green   = '\033[92m'
    yellow  = '\033[93m'
    blue    = '\033[94m'
    magenta = '\033[95m'
    cyan    = '\033[96m'
    white   = '\033[97m'
    reset   = '\033[0m'


    #start = time.perf_counter_ns()
    #print(f'{(time.perf_counter_ns()-start):,.0f} nsec')
    #timeit('"-".join(str(n) for n in range(100))', number=10000)



# ==========================================================
# ==========================================================

def main():
    #print(__doc__)
    print(f'{fg.yellow}-- MasterMind --{fg.reset}')

    key = ''
    while key.lower() != 'y':
        print(f'{"="*24}\n')

        make_setup()

        if not m.STATISTIC:
            run_mastermind()

        else:
            repeats = input_int('How many repeats to find averages? : ', min=1, max=2000)
            print()

            if repeats == '': repeats = 1
            if repeats == 1: m.STATISTIC = False

            starttime0 = time.perf_counter()
            stat = [[0]*repeats for _ in range(2)]
            for i in range(repeats):
                starttime  = time.perf_counter()
                stat[0][i] = run_mastermind()
                stat[1][i] = (time.perf_counter() - starttime) * 1000   #msec
            stat.append((time.perf_counter() - starttime0))             #sec

            if m.STATISTIC: show_statistics(stat)
            else: m.STATISTIC = True            # reset of (repeats==1)

        key = input('\nQuit the game? <y> : ')
    print('\n-- END --\n')


if __name__ == '__main__': main()






