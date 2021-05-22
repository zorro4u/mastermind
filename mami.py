""" mastermind game (console)

    Setup
    - code maker and code solver
    - manual or automatic mode
    - changeable number of characters and columns
    - with or without repetition of characters
    - digits or letters encoded
    - automatic or manual feedback
    - changeable solver strategy
    - can use an extern helper file with precalculated answers
    - seperate statistic mode available

    Solver Strategy
    - randomly selected element from possible variants
    - Knuth algoritm
    - Irving algorithm
    - Kooi algorithm

    [References]
        Reto Fahrni, Mastermind Perfekte Strategie dank Computer
        https://silo.tips/download/mastermind-perfekte-strategie-dank-computer
        https://www.onlinespiele-sammlung.de/mastermind/about-mastermind.php
        https://codebreaker-mastermind-superhirn.blogspot.com/
        Vivian van Oijen, Genetic Algorithms Playing Mastermind
        http://dspace.library.uu.nl/handle/1874/367005
        https://dspace.library.uu.nl/bitstream/handle/1874/367005/bachelorthesis_vivianvanoijen.pdf
        https://www.researchgate.net/publication/228975782_Near-optimal_strategies_for_the_game_of_Logik
        Barteld Kooi, yet-another-mastermind-strategy
        https://research.rug.nl/en/publications/yet-another-mastermind-strategy
        https://pure.rug.nl/ws/portalfiles/portal/9871441/icgamaster.pdf
        Lotte Berghman, Efficient solutions for Mastermind using genetic algorithms
        http://www.rosenbaum-games.de/3m/p1/Mastermind/2009Berghman01.pdf

    python 3.9, standard module
    github.com/stevie7g <2021>
"""
import time
import random
from itertools import product, permutations as perm
from collections import Counter
from statistics import median
from math import factorial as fact
from getpass import getpass
from os import system
system("color")

from functools import lru_cache
from pathlib import Path
import pickle
import bz2

class setup_values:
    """ contains global values for initial setup
    """
    CHAR       = 6
    COLUMNS    = 4
    LIMIT      = 10
    REPETITION = True    # repetition of a character: yes
    NUMBERS    = True    # digits (or letters) as character: yes
    AUTOPLAY1  = True    # the code maker, automatic
    AUTOPLAY2  = True    # the code solver, automatic
    AUTOFEEDB  = 1       # feedback for the guess, automatic
    ALGO       = 0       # solver algorithm: Random:0, Kooi:1, Irving:2, Knuth:3
    TOA_help   = 0       # use the toa_helper file
    STATISTIC  = False   # a special mode to determine avg of guesses

    letters  = 'abcdefghijklmnopqrstuvwxyz'.upper()
    digits   = '1234567890'
    char_set = ''        # will be set later on 'check_setup'

    toa        = {}      # feedback dict: table_of_answers
    toa_loaded = False   # toa file is loaded

    userSubDirPath = r'Documents\Programming'   # location directory of toa file -- !! CUSTOMIZE HERE !!
    toa_fn         = 'toa.pkl'                  # name of toa file, (bzip2-compressed pickle file)

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
        code = input_seq('Code: ', newline=1, hide=1)

    step, black = 0, 0
    while black < m.COLUMNS and step < m.LIMIT:
        step += 1

        # gets a guess
        if silent or m.AUTOPLAY2:
            guess = get_guess(step, variants, allvariants)
        else:
            guess = input_seq('<?> : ')

        # gets a feedback for 'guess' vs. 'code'
        if silent or m.AUTOFEEDB:
            answer = black, white = feedback(guess, code)
        else:
            if m.AUTOPLAY2: print(f'\n#{step:02}: "{guess}"   ',end='')
            answer = black, white = input_feedback()
            
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


def get_guess(step, variants, allvariants):
    """ selects an item from a list of variants:
    """
    if  m.ALGO  == 0:
        return get_random_variant(variants)
    elif m.ALGO == 1:
        return get_kooi_variant(step, variants, allvariants)
    elif m.ALGO == 2:
        return get_irvi_variant(step, variants, allvariants)
    elif m.ALGO == 3:
        return get_knuth_variant(step, variants, allvariants)


def get_1st_variant(variants):
    """ returns the first element from the 'variants' list / (human linear style)
    """
    return variants[0]


def get_random_variant(variants):
    """ selects a random element from the 'variants' list
    """
    return random.sample(variants,1)[0]                # string
    #return get_1st_variant(variants)


def get_knuth_variant(step, variants, allvariants):
    """ Knuth, 1st best pattern: '1122' -- does not necessarily have to be calculated
    """
    if step > 1:
        if len(variants) != 1:
            #feedb = {allVar: max(Counter(feedback(allVar, var) for var in variants).values()) for allVar in allvariants}
            #toa_key = lambda allVar: feedb[allVar]

            # makes the table of answers, 1st: len(toa)=allvariants^2 ! ... 6/4: 1296^2 = 1_679_616 x call feedback()
            # returns the greatest value of histogram for the answers of allVar -> variants
            toa_key = lambda allVar: max(Counter(feedback(allVar,var) for var in variants).values())

            # returns the first variant with the smallest maxi-value of the set: (allvariants : maxi-value)
            guess = knuth = min(allvariants, key = toa_key)

            #guess_list = [key for (key, value) in feedb.items() if value == feedb[guess]]

            return guess
        else:
            return variants[0]                  # last variant directly -> guess = code
    elif m.NUMBERS:                             # special first guess for digits/letters    TODO: case of REPETITION=False ?
        return ''.join(map(str,[1 if i < m.COLUMNS/2 else 2 for i in range(m.COLUMNS)]))
    else:
        return ''.join('A' if i < m.COLUMNS/2 else 'B' for i in range(m.COLUMNS))


def get_irvi_variant(step, variants, allvariants):
    """ Irving, 1st best pattern '1123'
    """
    if step > 1:
#    if step > 0:
        if len(variants) != 1:
            #feedb = {allVar: sum(value**2/lenVariants() for value in Counter(feedback(allVar, var) for var in variants).values()) for allVar in allvariants}
            #toa_key = lambda allVar: feedb[allVar]
            toa_key = lambda allVar: sum(value**2/lenVariants() for value in Counter(feedback(allVar, var) for var in variants).values())
            guess = irvi = min(allvariants, key = toa_key)
            #guess_list = [key for (key, value) in feedb.items() if value == feedb[guess]]
            return guess
        else:
            return variants[0]                  # last variant directly -> guess = code
    elif m.NUMBERS:                             # special first guess for digits/letters    TODO: case of REPETITION=False ?
        if m.COLUMNS == 3: return '123'
        if m.COLUMNS == 4: return '1123'
        if m.COLUMNS == 5: return '11223'
        if m.COLUMNS == 6: return '112234'
    else:
        return ''.join('A' if i < m.COLUMNS/2 else 'B' for i in range(m.COLUMNS))


def get_kooi_variant(step, variants, allvariants):
    """ Kooi, 1st best pattern '1123' or '1234'
    """
    if step > 1:
#    if step > 0:
        if len(variants) != 1:
            #feedb = {allVar: len(Counter(feedback(allVar, var) for var in variants)) for allVar in allvariants}
            #toa_key = lambda allVar: feedb[allVar]
            toa_key = lambda allVar: len(Counter(feedback(allVar, var) for var in variants))
            guess = kooi = max(allvariants, key = toa_key)
            #guess_list = [key for (key, value) in feeb.items() if value == feedb[guess]]
            return guess
        else:
            return variants[0]                  # last variant directly -> guess = code
    elif m.NUMBERS:                             # special first guess for digits/letters    TODO: case of REPETITION=False ?
        if m.COLUMNS == 3: return '123'
        if m.COLUMNS == 4: return '1123'
        if m.COLUMNS == 5: return '11223'
        if m.COLUMNS == 6: return '112234'
    else:
        return ''.join('A' if i < m.COLUMNS/2 else 'B' for i in range(m.COLUMNS))


@lru_cache()
def feedback(guess, code):
    """ tests 'guess' for 'code':
        black pin: char and position are correct
        white pin: char is correct, position is wrong

        call 'feedback' at 6/4:
        random 1,600
        knuth, irvi, kooi: 2,000,000
    """
    # if previous calculated and stored in database, use it
    if (guess, code) in m.toa:
        return m.toa[guess, code]

    # forms pairs from both lists [(0. 0.) (1. 1.) ...], then compares both elements
    black = sum(a==b for a,b in zip(guess, code))

    # counts frequency of characters / histogram
    # returns the sum of the the smallest match
    white = sum(min(guess.count(c), code.count(c)) for c in m.char_set)     # faster
    #white = sum((Counter(guess) & Counter(code)).values())

    white -= black                      # avoid double counting of white (even if black)
    m.toa[guess, code] = black, white   # write in table_of_answers database
    return black, white                 # integer


def lenVariants():
    """
    """
    if m.REPETITION:
        return m.CHAR ** m.COLUMNS
    else:
        return fact(m.CHAR) // fact(m.CHAR - m.COLUMNS)


def check_setup():
    # max. 10 digits or 26 letters
    if m.NUMBERS and (m.CHAR > 10):       m.CHAR = 10
    elif not m.NUMBERS and m.CHAR > 26:   m.CHAR = 26

    # adjusts columns
    if not m.REPETITION and (m.COLUMNS > m.CHAR): m.COLUMNS = m.CHAR

    # makes the set of characters
    if m.NUMBERS: m.char_set = m.digits[:m.CHAR]     # cuts the string from the left
    else:         m.char_set = m.letters[:m.CHAR]

    # dict of feedback
    m.dic_fb = {(black, white):0 for black in range(m.COLUMNS+1) for white in range(m.COLUMNS+1 - black)}
    m.dic_fb.pop((m.COLUMNS-1, 1))


# ==========================================================
# Input / Output

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
    x = input_int(f'{"Digits use":12}{fg.grey}{"["+str(m.NUMBERS)+"]":7}{fg.reset}: ')
    if x != '': m.NUMBERS = x
    x = input_int(f'{"Coder autom":12}{fg.grey}{"["+str(m.AUTOPLAY1)+"]":7}{fg.reset}: ')
    if x != '': m.AUTOPLAY1 = x
    x = input_int(f'{"Solver auto":12}{fg.grey}{"["+str(m.AUTOPLAY2)+"]":7}{fg.reset}: ')
    if x != '': m.AUTOPLAY2 = x
    x = input_int(f'{"Feedback auto":14}{fg.grey}{"["+str(m.AUTOFEEDB)+"]":5}{fg.reset}: ')
    if x != '': m.AUTOFEEDB = x
    x = input_int('Rand:0 Kooi :1\n'f'{"Irvi:2 Knuth:3":15}{fg.grey}{"<"+str(m.ALGO)+">":4}{fg.reset}: ', min=0, max=3)
    if x != '': m.ALGO = x
    x = input_int(f'{"TOA file use":13}{fg.grey}{"["+str(m.TOA_help)+"]":6}{fg.reset}: ')
    if x != '': m.TOA_help = x
    x = input_int(f'{"Statistic":12}{fg.grey}{"["+str(m.STATISTIC)+"]":7}{fg.reset}: ')
    if x != '': m.STATISTIC = x
    x = input_int(f'{"Limit":12}{fg.grey}{"<"+str(m.LIMIT)+">":7}{fg.reset}: ', min=1, max=50)
    if x != '': m.LIMIT = x

    check_setup()

    print(f'{"Solutions":19}: {lenVariants():,.0f}\n'\
        f'{"-"*30}\n')

    if m.TOA_help: load_toa_file()
    elif m.toa_loaded:
        m.toa.clear()
        m.toa_loaded = False


def show_setup():
    print(
        f'{"Characters":12}: {m.CHAR}\n'
        f'{"Columns":12}: {m.COLUMNS}\n'
        f'{"Repetition":12}: {m.REPETITION}\n'
        f'{"Digits use":12}: {m.NUMBERS}\n'
        f'{"Coder autom":12}: {m.AUTOPLAY1}\n'
        f'{"Solver auto":12}: {m.AUTOPLAY2}\n'
        f'{"Feedbk auto":12}: {m.AUTOFEEDB}\n'
        f'{"Solver algo":12}: {m.ALGO}\n'
        f'{"TOA file use":12}: {m.TOA_help}\n'
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
    #if m.AUTOPLAY2:        # shows the remaining variants
    if 1 == 1:
        msg03 = f' | remain. {lenVari:,.0f}'
        msg04 = f': {variants}'
        msg05 = ''
    else: 
        msg03 = msg04 = ''
        msg05 = '\n'

    if black < m.COLUMNS and (lenVari > 10 or m.ALGO > 0):  # not yet solved and too many variants to display
        msg = msg01 + msg02 + msg03 + msg05
    elif black < m.COLUMNS:                                 # not resolved yet, displayed variants
        msg = msg01 + msg02 + msg03 + msg04 + msg05
    else:                                                   # solved
        msg = (
            f'{fg.green}' + msg01 + f'{fg.reset}\n'
            f'\n{fg.green}-- Done! --{fg.reset}'
        )
    print(msg)


def show_statistics(stati):
    lenVari  = lenVariants()
    guesses  = stati[0]
    duration = stati[1]
    alltime  = stati[2]
    med1 = median(guesses)
    med2 = median(duration)
    avg1 = sum(guesses)/len(guesses)
    avg2 = sum(duration)/len(duration)
    msg  = (
        f'{fg.cyan}{"med. guesses":13}: {med1:.1f}{fg.reset}\n'
        f'{"avg. guesses":13}: {avg1:.3f}\n'
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


def show_code(code=''):
    print(
        #f'{"":6}' + ' '.join(code) + '\n'
        f'{"Code:":6}{"* " *m.COLUMNS}\n'
    )


def show_gameover(code):
    print(
        f'\n{fg.red}-- GAME OVER --{fg.reset}\n'
        f'The code was "{code}"\n'
    )


def input_feedback():
    """ black/white
    """
    while True:
        try:
            fb = input('<bw>: ')
            #if len(fb) == 2:                    # max: '99' feedback
            x = int(fb)
            if (int(fb[0]), int(fb[1])) in m.dic_fb:
                return int(fb[0]), int(fb[1])
            else: 
                raise ValueError
        except ValueError: 
            print('Not a correct input...')


def input_int(text, min=0, max=1):
    """ for setup and statistic repeats
    """
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


def input_seq(text, newline=False, hide=0):
    """ Input code/guess
    """
    while True:
        try:
            if hide: seq = getpass(text).upper()
            else: seq = input(text).upper()            
            if newline: print()
            if len(seq) != m.COLUMNS:
                raise KeyboardInterrupt('Input to short/long...\n')
            for char in seq:
                if char not in m.char_set: raise KeyboardInterrupt('Input not in char set...\n')
            return seq
        except KeyboardInterrupt as error: print(error)


def load_toa_file():
    dirPath = Path(Path.home(), m.userSubDirPath)
    filename = Path(dirPath, m.toa_fn)
    if m.toa_loaded: return
    print(f'load table_of_answers ...')
    if Path(filename).is_file():
        file = bz2.BZ2File(filename, 'r')
        m.toa = pickle.load(file)
        file.close()
    m.toa_loaded = True
    m.toa_loaded_len = len(m.toa)
    print(f'{len(m.toa):,.0f} loaded\n')


def save_toa_file():
    dirPath = Path(Path.home(), m.userSubDirPath)
    filename = Path(dirPath, m.toa_fn)
    if m.toa_loaded_len < len(m.toa):
        print(f'\nsave table_of_answers ...')
        file = bz2.BZ2File(filename, 'w')       # compressed with bzip2
        pickle.dump(m.toa, file)
        file.close()
        print(f'{len(m.toa):,.0f} saved\n',end='')


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
            repeats = input_int('How many repeats to find averages? : ', min=1, max=5000)
            print()

            if repeats == '': repeats = 1
            if repeats == 1:  m.STATISTIC = False

            starttime0 = time.perf_counter()
            stat = [[0]*repeats for _ in range(2)]
            for i in range(repeats):
                starttime  = time.perf_counter()
                stat[0][i] = run_mastermind()
                stat[1][i] = (time.perf_counter() - starttime) * 1000   #msec
            stat.append((time.perf_counter() - starttime0))             #sec

            if m.STATISTIC: show_statistics(stat)
            else: m.STATISTIC = True            # reset of repeats==1

        key = input('\nQuit the game? <y> : ')

    if m.toa_loaded: save_toa_file()
    print('\n-- END --\n')


if __name__ == '__main__': main()
