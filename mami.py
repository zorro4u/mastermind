""" <2021> https://github.com/zorro4u/mastermind
"""
import time
import random
from itertools import product, permutations as perm
from collections import Counter
from statistics import median, mode, multimode
from math import factorial as fact
from functools import lru_cache
from pathlib import Path
import pickle
import bz2
from os import system
system("color")


class setup_values:
    """ contains global values
    """
    # initial setup
    COLUMNS    = 4
    CHAR       = 6
    LIMIT      = 10
    REPETITION = True    # repetition of a character: yes
    NUMBERS    = True    # digits (or letters) as character: yes
    AUTOPLAY1  = True    # the code maker, automatic
    AUTOPLAY2  = False   # the code solver, automatic
    SHOW_HINT  = False   # give a hint in manual solver mode
    STATISTIC  = False   # a special mode to determine avg of attemptes
    ALGO       = 0       # solver algorithm: Random:0, Kooi:1, Irving:2, Knuth:3
    ALL        = False   # all algoritm in statistic mode
    TOA_help   = False   # use the toa_helper file // no speed advantage :-(
    RUNS       = 1000    # runs for statistic mode
    TOA_name   = 'toa'   # name of toa file (w/o .extension),  (bzip2-compressed .bz2)
    userSubDirPath = r'Documents\Code'   # location, directory of local toa file

    # common use
    letters  = 'abcdefghijklmnopqrstuvwxyz'.upper()
    digits   = '1234567890'
    char_set = ''        # will be set later on 'check_setup'
    max_variants = 10**7 # cut the range
    error_ct = 0

    # statistic mode
    algo_set = {
        0 : "random",
        1 : "Kooi",
        2 : "Irving",
        3 : "Knuth"
    }
    toa_loaded_len = 0
    toa_loaded = False   # toa file is loaded
    toa        = {}      # feedback dict: table_of_answers
    code_pool  = []
    code = ""


m = setup_values         # rename for easier use


# ==========================================================
def run_mastermind():
    """ Mastermind core routine
    """
    silent = m.STATISTIC

    # determines all solutions
    allvariants = gen_allvariants()
    variants    = allvariants.copy()
    code = ""

    # generates a random code to be found
    if silent:
        code = m.code
    elif m.AUTOPLAY1:
        code = gen_variant()
        print(f'{"code:":6}{"*" * m.COLUMNS}\n')
    elif not m.AUTOPLAY1:
        code = input_seq('Code: ', True)

        # hide the input
        up = f'\033[1A'
        right = f'\033[6C'  # len(input_str)
        code_str = f'{"*" * m.COLUMNS}'
        hide_code = up + right + code_str + '\n'
        print(hide_code)

    step, black = 0, 0
    while black < m.COLUMNS and step < m.LIMIT:
        step += 1

        # gets a attempt
        if silent or m.AUTOPLAY2:
            attempt = get_attempt(step, variants, allvariants)
        else:
            attempt = input_seq(f'?_{step:02}: ')

        # gets a feedback for 'attempt' vs. 'code'
        answer = black, _ = feedback(attempt, code)

        # Filters out those with the same answer pattern for the current attempt
        # from the current variant pool. The current attempt is omitted. The right
        # variant will always be there until the end.
        # (-> bottle neck)
        new_variants = [vari for vari in variants if feedback(vari, attempt) == answer]

        if not silent:
            show_attempt(step, attempt, new_variants, answer, variants)

        variants = new_variants

    else:
        if black != m.COLUMNS and not silent:
            show_gameover(code)

    return step


# ==========================================================
# CALCULATION Section

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


def get_attempt(step, variants, allvariants):
    """ selects an item from a list of variants:
    """
    if  m.ALGO == 0:
        return get_random_variant(step, variants)
    elif m.ALGO == 1:
        return get_kooi_variant(step, variants, allvariants)
    elif m.ALGO == 2:
        return get_irvi_variant(step, variants, allvariants)
    elif m.ALGO == 3:
        return get_knuth_variant(step, variants, allvariants)


def get_random_variant(step, variants):
    """ selects a random element from the 'variants' list
    """
    if step > 1 or not m.REPETITION:
        return random.sample(variants, 1)[0]    # string
    else:
        return first_pattern()


def get_kooi_variant(step, variants, allvariants):
    """ (1) Kooi, 1st best pattern '1123' or '1234'
    """
    if step > 1:
        if len(variants) != 1:
            #feedb = {allVar: len(Counter(feedback(allVar, var) for var in variants)) for allVar in allvariants}
            #toa_key = lambda allVar: feedb[allVar]
            toa_key = lambda allVar: len(Counter(feedback(allVar, var) for var in variants))

            attempt = max(allvariants, key = toa_key)
            #attempt_list = [key for (key, value) in feeb.items() if value == feedb[attempt]]

            return attempt
        else:
            return variants[0]   # last variant directly -> attempt = code
    else:
        return first_pattern()


def get_irvi_variant(step, variants, allvariants):
    """ (2) Irving, 1st best pattern '1123'
    """
    if step > 1:
        if len(variants) != 1:
            #feedb = {allVar: sum(value**2/lenVariants() for value in Counter(feedback(allVar, var) for var in variants).values()) for allVar in allvariants}
            #toa_key = lambda allVar: feedb[allVar]
            toa_key = lambda allVar: sum(value**2/lenVariants() for value in Counter(feedback(allVar, var) for var in variants).values())

            attempt = min(allvariants, key = toa_key)
            #attempt_list = [key for (key, value) in feedb.items() if value == feedb[attempt]]

            return attempt
        else:
            return variants[0]   # last variant directly -> attempt = code
    else:
        return first_pattern()


def get_knuth_variant(step, variants, allvariants):
    """ (3) Knuth, 1st best pattern: '1122' -- does not necessarily have to be calculated
    """
    if step > 1:
        if len(variants) != 1:
            #feedb = {allVar: max(Counter(feedback(allVar, var) for var in variants).values()) for allVar in allvariants}
            #toa_key = lambda allVar: feedb[allVar]

            # makes the table of answers, 1st: len(toa)=allvariants^2 !
            # ... 6/4: 1296^2 = 1_679_616 x call feedback()
            # returns the greatest value of histogram for the answers of allVar -> variants
            toa_key = lambda allVar: max(Counter(feedback(allVar,var) for var in variants).values())

            # returns the first variant with the smallest maxi-value of the set:
            # (allvariants : maxi-value)
            attempt = min(allvariants, key = toa_key)

            #attempt_list = [key for (key, value) in feedb.items() if value == feedb[attempt]]

            return attempt
        else:
            return variants[0]    # last variant directly -> attempt = code
    else:
        return first_pattern(1)


def first_pattern(scheme=0):
    """ pattern scheme:
        (0): '1123', '11223'
        (1): '1122', '11223'
    """
    if not m.REPETITION:
        return ''.join(map(str,[m.char_set[col] for col in range(m.COLUMNS)]))

    # with repetition
    even = not m.COLUMNS % 2    # even number of columns
    pattern = []
    i = 0
    for col in range(m.COLUMNS):
        pattern.append(m.char_set[i])

        # odd column position, next character
        if col % 2:
            i += 1

    # array -> string
    pattern = ''.join(map(str, pattern))

    # replace last character with next, '1122'->'1123'
    if scheme == 0 and even:
        pattern = pattern[:-1] + str(m.char_set[i])

    return pattern


@lru_cache()
def feedback(attempt, code):
    """ tests 'attempt' for 'code':
        black pin: char and position are correct
        white pin: char is correct, position is wrong

        call 'feedback' at 6/4:
        random 1,600
        knuth, irvi, kooi: 2,000,000
    """
    # if previous calculated and stored in database, use it
    if (attempt, code) in m.toa:
        return m.toa[attempt, code]

    # forms pairs from both lists [(0. 0.) (1. 1.) ...], then compares both elements
    black = sum(a==b for a,b in zip(attempt, code))

    # counts frequency of characters / histogram
    # returns the sum of the the smallest match
    white = sum(min(attempt.count(c), code.count(c)) for c in m.char_set)     # faster
    #white = sum((Counter(attempt) & Counter(code)).values())

    white -= black                        # avoid double counting of white (even if black)
    m.toa[attempt, code] = black, white   # write in table_of_answers database
    return black, white                   # integer


def lenVariants():
    """
    """
    if m.REPETITION:
        return m.CHAR ** m.COLUMNS
    else:
        return fact(m.CHAR) // fact(m.CHAR - m.COLUMNS)


# ==========================================================
# INPUT DATA CHECK Section

def check_setup():
    # max. 10 digits or 26 letters
    if m.NUMBERS and (m.CHAR > 10):       m.CHAR = 10
    elif not m.NUMBERS and m.CHAR > 26:   m.CHAR = 26

    # adjusts columns
    if not m.REPETITION and (m.COLUMNS > m.CHAR): m.COLUMNS = m.CHAR

    # makes the set of characters
    if m.NUMBERS: m.char_set = m.digits[:m.CHAR]     # cuts the string from the left
    else:         m.char_set = m.letters[:m.CHAR]

    # in manual mode no statistic option
    if not m.AUTOPLAY1 or not m.AUTOPLAY2:
        m.STATISTIC = False

    # game mode only with random algo
    if not m.STATISTIC:
        m.ALGO = 0

    # cut the complexity and set char down
    m.CHAR = max_char(m.CHAR)


def max_char(value):
    # cut the complexity and set char down
    # var=char**col .. char=var**1/col .. col=log(var,char)=log(var)/log(char)
    if m.REPETITION and value ** m.COLUMNS > m.max_variants:
        max = int(m.max_variants**(1/float(m.COLUMNS)))
        return max
    return value


# ==========================================================
# INPUT & OUTPUT Section

def show_setup():
    print(
        f'{"Digits":14}: {m.NUMBERS}\n'
        f'{"Columns":14}: {m.COLUMNS}\n'
        f'{"Characters":14}: {m.CHAR}\n'
        f'{"Attempt_limit":14}: {m.LIMIT}\n'
        f'{"Repetition":14}: {m.REPETITION}\n'
        f'{"Coder_autom":14}: {m.AUTOPLAY1}\n'
        f'{"Solver_auto":14}: {m.AUTOPLAY2}\n'
        f'{"Solver_hint":14}: {m.SHOW_HINT}\n'
        , end='')

    if m.AUTOPLAY1 and m.AUTOPLAY2:
        print(
            f'{"Statistic":14}: {m.STATISTIC}\n'
            f'{"Solver_algo":14}: {m.algo_set[m.ALGO]}\n'
            f'{"Algo_all":14}: {m.ALL}\n'
            f'{"TOA_file":14}: {m.TOA_help}\n'
            f'{"Runs":14}: {m.RUNS:,}\n'
            , end='')

    print(
        f'{"Solutions":14}: {lenVariants():,.0f}\n'
        f'{"-"*24}\n'
    )


def make_setup():
    """ show and set the global values for the game
    """
    x = input_bool(f'{"Digits ":.<15}{fg.grey}{" ["+str(m.NUMBERS)+"]":8}{fg.off}: ')
    if x != '': m.NUMBERS = x

    x = input_int(f'{"Columns ":.<15}{fg.grey}{" <"+str(m.COLUMNS)+">":8}{fg.off}: ')
    if x != '': m.COLUMNS = x

    if  m.NUMBERS:
        x = input_int(f'{"Characters ":.<15}{fg.grey}{" <"+str(m.CHAR)+">":8}{fg.off}: ', max=10, chk=True)
    else:
        x = input_int(f'{"Characters ":.<15}{fg.grey}{" <"+str(m.CHAR)+">":8}{fg.off}: ', max=26, chk=True)
    if x != '': m.CHAR = x

    x = input_int(f'{"Attempt_limit ":.<15}{fg.grey}{" <"+str(m.LIMIT)+">":8}{fg.off}: ', max=50)
    if x != '': m.LIMIT = x
    x = input_bool(f'{"Repetition ":.<15}{fg.grey}{" ["+str(m.REPETITION)+"]":8}{fg.off}: ')
    if x != '': m.REPETITION = x
    x = input_bool(f'{"Coder_autom ":.<15}{fg.grey}{" ["+str(m.AUTOPLAY1)+"]":8}{fg.off}: ')
    if x != '': m.AUTOPLAY1 = x
    x = input_bool(f'{"Solver_auto ":.<15}{fg.grey}{" ["+str(m.AUTOPLAY2)+"]":8}{fg.off}: ')
    if x != '': m.AUTOPLAY2 = x

    if not m.AUTOPLAY2:
        x = input_bool(f'{"Solver_hint ":.<15}{fg.grey}{" ["+str(m.SHOW_HINT)+"]":8}{fg.off}: ')
        if x != '': m.SHOW_HINT = x

    if m.AUTOPLAY1 and m.AUTOPLAY2:
        x = input_bool(f'{"Statistic ":.<15}{fg.grey}{" ["+str(m.STATISTIC)+"]":8}{fg.off}: ')
        if x != '': m.STATISTIC = x

        if m.STATISTIC:
            x = input_int('Rand:0 Kooi :1\n'f'{"Irvi:2 Knuth:3":<16}{fg.grey}{"<"+str(m.ALGO)+">":7}{fg.off}: ', min=0, max=3)
            if x != '': m.ALGO = x

            x = input_bool(f'{"Algo_all ":.<15}{fg.grey}{" ["+str(m.ALL)+"]":8}{fg.off}: ')
            if x != '': m.ALL = x

            x = input_bool(f'{"TOA_file ":.<15}{fg.grey}{" ["+str(m.TOA_help)+"]":8}{fg.off}: ')
            if x != '': m.TOA_help = x

            runs0 = f'{m.RUNS:,d}'
            runs = f'{" <" + runs0 + ">":8}'
            if len(runs)>8:    # change the format above 10,000
                runs = f'{" " + runs:8}'

            run_max = 100      # algo > 0 are time-consuming
            if m.ALL and m.RUNS > run_max:
                x = input_int(f'{"Runs ":.<15}{fg.grey}{runs}{fg.off}: ', max=run_max)
            else:
                x = input_int(f'{"Runs ":.<15}{fg.grey}{runs}{fg.off}: ', max=100000)
            if x != '': m.RUNS = x

    print(f'{"Solutions":23}: {lenVariants():,.0f}\n'\
        f'{"-"*30}\n')

    check_setup()
    toa_loader()


def show_attempt(step, attempt, new_variants, result, old_variants):
    black, white = result
    lenVari = len(new_variants)
    msg_feedb = f'-> b:{black} w:{white}'
    msg = msg_attempt = msg_vari = msg_end = step_right = step_high = ''

    if m.AUTOPLAY2:
        msg_attempt = f'?_{step:02}: {attempt} '

    else:
        step_high = '\033[1A'   # 1x
        if attempt in old_variants:
            step_right = f'\033[{6 + m.COLUMNS + 1}C'

        # The attempt is not in the reducing variants
        # and has already been cancelled.
        else:
            msg_attempt = f'?_{step:02}: {fg.red}{attempt}{fg.off} '

    tmp1 = f'{lenVari:,}:'
    if not m.AUTOPLAY2 and m.SHOW_HINT:
        tmp2 = f' | {tmp1:<5} '
        tmp3 = str(new_variants)
        if lenVari > 3:     # too many variants to show, only 3
            #tmp3 = str(random.sample(new_variants, 3)) + '\033[1D' + ', ...]'
            tmp3 = str(new_variants[:3]) + '\033[1D' + ', ...]'
        msg_vari = tmp2 + tmp3
    else:
        msg_vari = f' | {tmp1[:-1]:<5} '

    # not yet solved
    if black < m.COLUMNS and m.ALGO > 0:
        msg += msg_attempt + msg_feedb + msg_end

    # not yet solved, show variants
    elif black < m.COLUMNS:
        msg += msg_attempt + msg_feedb + msg_vari + msg_end

    # solved
    else:
        if m.AUTOPLAY2:
            msg_attempt = f'{msg_attempt:11}'
            step_high=''
        else:
            msg_attempt = f'?_{step:02}: {attempt} '    # same as input_str

        msg += fg.green + msg_attempt + '-> Done!' + fg.off
        step_right = ''

        code = 'Code: ' + attempt
        up = f'\033[{step + m.error_ct + 1}A'
        down = f'\033[{step + m.error_ct + 1}B'
        left = f'\033[{len(code)}D'
        show_code = up + fg.green + code + fg.off + down + left
        msg = show_code + msg

    # len(input_msg)    # 6 + 1x space
    # len(input_user)   # columns
    # jump_right=len(input_msg)+len(input_user)
    # ANSI escape code:
    # \33[4C jump 4x right (= ' '*4)
    # \33[1A jump 1x high
    # A B C D : high, down, right, left
    print (step_right + step_high + msg)


def input_seq(text, coder=False):
    """ Input code/attempt
    """
    while True:
        try:
            seq = input(text).upper()
            if len(seq) != m.COLUMNS:
                raise KeyboardInterrupt(f'{fg.magenta}Input to short/long...{fg.off}')

            for char in seq:
                if char not in m.char_set:
                    raise KeyboardInterrupt(f'{fg.magenta}Input not in char set...{fg.off}')

                if not m.REPETITION and seq.count(char) > 1:
                    raise KeyboardInterrupt(f'{fg.magenta}Input without repetitions...{fg.off}')

            return seq

        except KeyboardInterrupt as error:
            # find the right upper line to show the unhidden code at the end
            if not coder:
                m.error_ct += 1
            elif m.error_ct > 0:
                m.error_ct -= 1

            up = '\033[1A'
            down = '\033[1B'
            right = f'\033[{6 + m.COLUMNS + 1}C'
            left = f'\033[{6 + m.COLUMNS + 1}D'
            print(up + right + str(error))


def input_int(text, min=1, max=10, chk=False):
    while True:
        try:
            x = input(text)
            if x != '':
                x = int(x)
                if x < min or x > max:
                    x = int('error')

                if chk:
                    max = max_char(x)
                    if max < x:
                        x = int('error')

            elif chk:
                max = max_char(m.CHAR)
                if max < m.CHAR:
                    x = int('error')

            return x
        except ValueError:
            print(f'{fg.magenta}Only digits between {min}-{max} allowed...{fg.off}')


def input_bool(text):
    while True:
        try:
            x = input(text)
            if x != '':

                if x.lower()=="y" or x.lower()=="yes":
                    x = 1
                elif x.lower()=="n" or x.lower()=="no":
                    x = 0

                x = int(x)          # only digits
                if x < 0 or x > 1:  # only 0/1
                    x = int('error')

                return bool(x)
            return x
        except ValueError:
            print(f'{fg.magenta}Only 0/1/n/y allowed...{fg.off}')


def show_gameover(code):
    print('\n'
        f'{fg.red}-- GAME OVER --{fg.off}\n'
        f'The code was "{code}"\n'
    )


# ==========================================================
# STATISTIC Section

def show_statistics(stati):
    lenVari  = lenVariants()
    attemptes  = stati[0]
    duration = stati[1]
    alltime = stati[2]
    med1 = median(attemptes)      # mittlere Wert / the average value
    med2 = median(duration)
    avg1 = sum(attemptes)/len(attemptes)    # Durchschnitt / average
    avg2 = sum(duration)/len(duration)
    mod0 = mode(attemptes)        # Modus: häufigster Wert / the most frequent value
    mod1 = multimode(attemptes)   # [häufigsten Werte] / [the most common values]

    msg  = (
        #f'{"algo":13}: {m.algo_set[m.ALGO]}\n'
        #f'{"runs":13}: {m.RUNS:,}\n'
        f'{fg.cyan}{"avg. attemp.":13}: {avg1:.3f}{fg.off}\n'
        f'{"med. attemp.":13}: {med1:.1f}\n'
        f'{"mod. attemp.":13}: {mod1}\n'
        f'{"max. attemp.":13}: {max(attemptes)}\n'
        f'{"min. attemp.":13}: {min(attemptes)}\n'
        f'{fg.cyan}{"avg. msec":13}: {avg2:,.1f}{fg.off}\n'
        f'{"med. msec":13}: {med2:,.1f}\n'
        f'{"max. msec":13}: {max(duration):,.1f}\n'
        f'{"min. msec":13}: {min(duration):,.1f}\n'
        f'{"-"*25}\n'
        f'{"alltime sec":13}: {alltime:,.1f}\n\n'
    )
    print(msg, end='')


def toa_loader():
    if m.TOA_help: load_toa_file()
    elif m.toa_loaded:
        m.toa.clear()
        m.toa_loaded = False


def load_toa_file():
    """ TOA: dict( (attempt, code): (black, white), ... )
    ('1111','1111'):(4,0), ('1111','1112'):(3,0), ...
    toa[('1111','1111')] -> (4,0)
    """
    if m.toa_loaded: return

    m.TOA_name += '.bz2'
    dirPath = Path(Path.home(), m.userSubDirPath)
    filename = Path(dirPath, m.TOA_name)

    print(f'load table_of_answers ... ', end='')

    if Path(filename).is_file():
        file = bz2.BZ2File(filename, 'r')
        m.toa = pickle.load(file)
        file.close()
        print('done\n')
    else:
        print('\n')
    m.toa_loaded = True
    m.toa_loaded_len = len(m.toa)


def save_toa_file():
    dirPath = Path(Path.home(), m.userSubDirPath)
    filename = Path(dirPath, m.TOA_name)
    if m.toa_loaded_len < len(m.toa):
        print(f'\nsave table_of_answers ... ', end='')
        file = bz2.BZ2File(filename, 'w')
        pickle.dump(m.toa, file)
        file.close()
        print('done')


def run_statistic():
    print(f'{"*"*25}')
    print(f'{"algo":13}: {m.algo_set[m.ALGO]} ({m.ALGO})')
    print(f'{"runs":13}: {m.RUNS:,}')

    repeats = m.RUNS
    starttime0 = time.perf_counter()
    stat = [[0]*repeats for _ in range(2)]


    ''' Progress indicator '''
    progress = 0
    step = repeats // 10     # 10% Step
    print("*****", end="", flush=True)

    for run in range(repeats):
        progress += 1
        if progress == step:
            progress = 0
            print("**", end="", flush=True)  # 25 characters in total

        m.code = m.code_pool[run]
        starttime  = time.perf_counter()
        stat[0][run] = run_mastermind()
        stat[1][run] = (time.perf_counter() - starttime) * 1000   #msec

    stat.append((time.perf_counter() - starttime0))             #sec
    print()

    if m.STATISTIC: show_statistics(stat)
    else: m.STATISTIC = True            # reset of repeats==1


def run_statistic_all():
    temp = m.ALGO
    for algo in m.algo_set:
        m.ALGO = algo
        run_statistic()
    m.ALGO = temp


# ==========================================================
# COLOR

class fg:
    """ANSI escape foreground color (30-37)/90-97
    """
    grey    = '\033[90m'
    red     = '\033[91m'
    green   = '\033[92m'
    yellow  = '\033[93m'
    blue    = '\033[94m'
    magenta = '\033[95m'
    cyan    = '\033[96m'
    white   = '\033[97m'
    off     = '\033[0m'


class ColorList:
    """long list ANSI escape color sequence
    """
    # Reset
    Color_Off = "\033[0m"       # Text Reset

    # Regular Colors
    Black = "\033[0;30m"        # Black
    Red = "\033[0;31m"          # Red
    Green = "\033[0;32m"        # Green
    Yellow = "\033[0;33m"       # Yellow
    Blue = "\033[0;34m"         # Blue
    Purple = "\033[0;35m"       # Purple
    Cyan = "\033[0;36m"         # Cyan
    White = "\033[0;37m"        # White

    # Bold
    BBlack = "\033[1;30m"       # Black
    BRed = "\033[1;31m"         # Red
    BGreen = "\033[1;32m"       # Green
    BYellow = "\033[1;33m"      # Yellow
    BBlue = "\033[1;34m"        # Blue
    BPurple = "\033[1;35m"      # Purple
    BCyan = "\033[1;36m"        # Cyan
    BWhite = "\033[1;37m"       # White

    # Underline
    UBlack = "\033[4;30m"       # Black
    URed = "\033[4;31m"         # Red
    UGreen = "\033[4;32m"       # Green
    UYellow = "\033[4;33m"      # Yellow
    UBlue = "\033[4;34m"        # Blue
    UPurple = "\033[4;35m"      # Purple
    UCyan = "\033[4;36m"        # Cyan
    UWhite = "\033[4;37m"       # White

    # Background
    On_Black = "\033[40m"       # Black
    On_Red = "\033[41m"         # Red
    On_Green = "\033[42m"       # Green
    On_Yellow = "\033[43m"      # Yellow
    On_Blue = "\033[44m"        # Blue
    On_Purple = "\033[45m"      # Purple
    On_Cyan = "\033[46m"        # Cyan
    On_White = "\033[47m"       # White

    # High Intensty
    IBlack = "\033[0;90m"       # Black
    IRed = "\033[0;91m"         # Red
    IGreen = "\033[0;92m"       # Green
    IYellow = "\033[0;93m"      # Yellow
    IBlue = "\033[0;94m"        # Blue
    IPurple = "\033[0;95m"      # Purple
    ICyan = "\033[0;96m"        # Cyan
    IWhite = "\033[0;97m"       # White

    # Bold High Intensty
    BIBlack = "\033[1;90m"      # Black
    BIRed = "\033[1;91m"        # Red
    BIGreen = "\033[1;92m"      # Green
    BIYellow = "\033[1;93m"     # Yellow
    BIBlue = "\033[1;94m"       # Blue
    BIPurple = "\033[1;95m"     # Purple
    BICyan = "\033[1;96m"       # Cyan
    BIWhite = "\033[1;97m"      # White

    # High Intensty backgrounds
    On_IBlack = "\033[0;100m"   # Black
    On_IRed = "\033[0;101m"     # Red
    On_IGreen = "\033[0;102m"   # Green
    On_IYellow = "\033[0;103m"  # Yellow
    On_IBlue = "\033[0;104m"    # Blue
    On_IPurple = "\033[10;95m"  # Purple
    On_ICyan = "\033[0;106m"    # Cyan
    On_IWhite = "\033[0;107m"   # White




    #start = time.perf_counter_ns()
    #print(f'{(time.perf_counter_ns()-start):,.0f} nsec')
    #timeit('"-".join(str(n) for n in range(100))', number=10000)

# ==========================================================
# ==========================================================

def main():
    print('\n', __doc__)
    print(f'{fg.yellow}-- MasterMind --{fg.off}')

    first = True
    key = ''
    while key.lower() != 'n':
        print(f'{"="*24}\n')

        if first: show_setup()
        first = False

        x = input('Change setup? <y>  : ')
        print()
        if x.lower() == 'y':
            make_setup()

        check_setup()
        toa_loader()


        if not m.STATISTIC:
            run_mastermind()

        else:
            for run in range(m.RUNS):
                m.code_pool.append(gen_variant())

            if m.ALL:
                run_statistic_all()
            else:
                run_statistic()

        key = input('\nRepeat the game? <y/n> : ')

    if m.toa_loaded: save_toa_file()
    print('\n-- END --\n')


# ==========================================================

if __name__ == '__main__':
    main()
