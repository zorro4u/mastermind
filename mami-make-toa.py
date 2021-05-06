""" mastermind, make files w/ feedbacks (table_of_answers)

    even as set of digits an uppercase letters
    stores as <toa+Char+Col.pkl> and
    overall   <toa+00.pkl> ... (bzip2 compressed)

    python 3.9, standard module
    github.com/stevie7g <2021>
"""
from itertools import product
from functools import lru_cache
from pathlib import Path
import pickle
import bz2

class setup_values:
    # characters
    CHA_min = 6
    CHA_max = 6

    # columns
    COL_min = 4
    COL_max = 4

    userSubDirPath = r'Documents\Programming'   # location directory of toa file
    toa_fn         = 'toa.pkl'                  # name of toa file

    numbers = False                             # starts with letters
    digits  = '1234567890'
    letters = 'abcdefghijklmnopqrstuvwxyz'.upper()
    toa  = {}

m = setup_values         # rename for easier use

# ==========================================================
def make_table_of_answers():
    """ m.CHAR, m.numbers -> m.char_set
        m.COLUMNS
    """
    toa = {}             # local dict (temporary)
    for m.CHAR in range(m.CHA_min, m.CHA_max+1):
        for m.COLUMNS in range(m.COL_min, m.COL_max+1):
            for a in range(2):              # for digits and uppercase_letters
                check_setup()               # set the right char_set
                allvariants = [''.join(x) for x in product(m.char_set, repeat=m.COLUMNS)]
                for a in allvariants:
                    for b in allvariants:
                        toa[a,b] = (feedback(a,b))
                m.numbers = not m.numbers   # change the char_set
            save_toa_file(toa,m.CHAR,m.COLUMNS)    # store a split file
            toa.clear()
    save_toa_file(m.toa,'00')               # store the overall dict
    m.numbers = not m.numbers               # set to original


@lru_cache()
def feedback(guess, code):
    if (guess, code) in m.toa: return m.toa[guess, code]
    black = sum(a==b for a,b in zip(guess, code))
    white = sum(min(guess.count(c), code.count(c)) for c in m.char_set) - black
    m.toa[guess, code] = black, white       # stored in the global dict
    return black, white


def check_setup():
    # max. 26 letters
    if m.CHA_max > 26: m.CHA_max = 26
    # max. 10 columns,     26^10 = ca. 1.4*10^14 -> 2*10^28 feedbacks (toa)
    if m.COL_max > 10: m.COL_max = 10

    if m.CHA_min > m.CHA_max: m.CHA_min = m.CHA_max
    if m.COL_min > m.COL_max: m.COL_min = m.COL_max

    # max. 10 digits or 26 letters
    if m.numbers and (m.CHAR > 10):       m.CHAR = 10
    elif not m.numbers and m.CHAR > 26:   m.CHAR = 26

    # makes the set of characters
    if m.numbers: m.char_set = m.digits[:m.CHAR]
    else:         m.char_set = m.letters[:m.CHAR]


def save_toa_file(data, cha='', col=''):
    dirPath = Path(Path.home(), m.userSubDirPath)
    fn = m.toa_fn[:-4] + str(cha) + str(col) + m.toa_fn[-4:]
    filename = Path(dirPath, fn)
    file = bz2.BZ2File(filename, 'w')
    pickle.dump(data, file)
    file.close()
    print(f'{fn} with {len(data):,.0f} saved\n',end='')

# ==========================================================
def main():
    print('making the "Table of Answers" ...')
    make_table_of_answers()
    print('\n-- END --\n')


if __name__ == '__main__': main()
