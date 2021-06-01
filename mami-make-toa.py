""" mastermind, make files w/ feedbacks (table_of_answers)

    even as set of digits an uppercase letters
    stores as <toa+Char+Col.pkl> and
    overall   <toa+00.pkl> ... (bzip2 compressed)

    makes the table of answers, 
    len(toa) = allvariants^2 ! ... 4/6: 1296^2 = 1,679,616 

    # brute-force algorithms:
    # columns/characters:(solutions w/ rep.) --> ^2 = answers
    # 2/26:(700)  3/26:(17,500)
    # 4/9:(6,500) 4/10:(10,000).. 4/15:(50,600).. 4/26:(457,000)
    # 5/6:(7,800)_ 5/7:(16,800)__ 5/8:(32,800) 5/9:(59,000)
    # 6/4:(4,100)  6/5:(15,600)   6/6:(46,700)
    # 7/3:(2,200)  7/4:(16,400)   7/5:(78,100)
    # 8/3:(6,500)  8/4:(65,500)
    # 9/2:(500)    9/3:(19,700)
    # 8Tsd  -> 64Mio, 1GB file
    # 16Tsd -> 256Mio
    # 33Tsd -> 1Mrd

    python 3.9, standard module
    github.com/stevie7g <2021>
"""
from collections import Counter
from itertools import product
from functools import lru_cache
from pathlib import Path
import pickle
import bz2
import dbm
import shelve
import csv

class setup_values:
    # columns
    COL_min = 4
    COL_max = 4

    # characters
    CHA_min = 10
    CHA_max = 10

    userSubDirPath = r'Documents\Programming'   # location directory of toa file
    toa_fn         = 'toa.pkl'                  # name of toa file

    numbers = True                              # starts with digits / letters
    digits  = '1234567890'
    letters = 'abcdefghijklmnopqrstuvwxyz'.upper()
    toa  = {}
    temp = []
      
m = setup_values         # rename for easier use

# ==========================================================
def make_table_of_answers():
    """ char, m.numbers -> m.char_set
        columns
    """
    toa = {}             # local dict (temporary)
    for columns in range(m.COL_min, m.COL_max+1):
        for char in range(m.CHA_min, m.CHA_max+1):
            for a in range(1):              # for digits and uppercase_letters
                check_setup(char)           # set the right char_set
                if m.numbers: m.type = 'd'
                else:         m.type = 'l'
                allvariants = [''.join(x) for x in product(m.char_set, repeat=columns)]
                print(f'{columns}x{char}: {len(allvariants):,.0f} --> {len(allvariants)**2:,.0f}\nworking in progress ...')
                for a in allvariants:
                    for b in allvariants:
                        feedback(a,b)       # {('111','222'):(1,0), ...}

#                    save_temp_file(columns, char)
#                    m.toa.clear()
#                save_toa_file(columns, char)   # store digits/letters split file
                m.numbers = not m.numbers       # change the char_set
            save_toa_file(columns, char)        # store columns/char split file
#        m.toa.clear()                           # new columns -> new dictionary
#    save_toa_file('00')                        # store the overall dict
    m.numbers = not m.numbers                   # set to original


@lru_cache()
def feedback(guess, code):
    if (guess, code) in m.toa: return m.toa[guess, code]
    black = sum(a==b for a,b in zip(guess, code))
    white = sum(min(guess.count(c), code.count(c)) for c in m.char_set) - black
    m.toa[guess, code] = black, white           # stored in the global dict
    return black, white


def check_setup(char):
    # max. 26 letters & 10 columns,     26^10 = ca. 1.4*10^14 -> 2*10^28 feedbacks (toa)
    if m.CHA_max > 26: m.CHA_max = 26
    if m.COL_max > 10: m.COL_max = 10

    if m.CHA_min > m.CHA_max: m.CHA_min = m.CHA_max
    if m.COL_min > m.COL_max: m.COL_min = m.COL_max

    # max. 10 digits or 26 letters
    if m.numbers and (char > 10):     char = 10
    elif not m.numbers and char > 26: char = 26

    # makes the set of characters
    if m.numbers: m.char_set = m.digits[:char]
    else:         m.char_set = m.letters[:char]
    
    load_toa_file()


def save_temp_file(col='', cha=''):
    dirPath = Path(Path.home(), m.userSubDirPath)
    fn = m.toa_fn[:-4] + str(col) + str(cha) + m.type + '.tmp'
    filename = Path(dirPath, fn)
    print(m.toa)#,input()

    with open(filename, 'w') as file:
        for k,v in m.toa.items():
            file.write(f'{k};{v}\n')  # semikolon seperated csv
    m.temp = {}
    with open(filename, 'r') as file:
#        temp = csv.DictReader(file, delimiter=';')
        temp = csv.reader(file, delimiter=';', quotechar="'", quoting=csv.QUOTE_NONE)
        for k,v in temp: 
            print(k,v)
            m.temp[k] = v
#            m.temp.update(temp)

#    with open(filename,'rb') as file:
#        m.temp.append(pickle.load(file))
    print(m.temp),input()
#    print(f'{fn} with {len(m.toa):,.0f} saved')


def save_toa_file(col='', cha='', ):
    print(f'saving in progress ...')
    dirPath = Path(Path.home(), m.userSubDirPath)
    fn = m.toa_fn[:-4] + str(col) + str(cha) + m.type + m.toa_fn[-4:] #+ '.bz2'
    filename = Path(dirPath, fn)

#    file = bz2.BZ2File(filename, 'w')
#    pickle.dump(m.toa, file)
#    file.close()
    with open(filename,'wb') as file:
        pickle.dump(m.toa, file)
    print(f'{fn} with {len(m.toa):,.0f} saved\n')

    
def load_toa_file(col='', cha=''):
    dirPath = Path(Path.home(), m.userSubDirPath)
    fn = m.toa_fn[:-4] + str(col) + str(cha) + m.toa_fn[-4:] #+ '.bz2'
    filename = Path(dirPath, fn)
    data = {}
    if Path(filename).is_file():
        print(f'load {fn} ...')
#        file = bz2.BZ2File(filename, 'r')
#        m.toa = pickle.load(file)
#        file.close()
        with open(filename,'rb') as file:
            m.toa = pickle.load(file)
        print(f'{len(m.toa):,.0f} loaded\n')
    return data


# ----------------------------------------------------------
    
def collection_of_somethings():
    """
    """
    char = 6
    columns = 4
    check_setup()
    allvariants = [''.join(x) for x in product(m.char_set, repeat=columns)]
    variants    = allvariants
    
    # dict by pattern
    # 'ABCD'->1234='1111', 'AABC'->1123='211', 'AABB'->1122='22', 'AAAB'->1112='31', 'AAAA'->1111='4'
    #dic_pattern = dict.fromkeys((''.join(map(str,sorted(Counter(allVar).values()))) for allVar in allvariants),0)     
    dic_pattern = {''.join(map(str,sorted(Counter(allVar).values()))):0 for allVar in allvariants}     
    print(dic_pattern),input('---')
    
    # dict by answers
    #dic_fb = dict.fromkeys(((black, white) for black in range(columns+1) for white in range(columns+1 - black)),0)
    dic_fb = {(black, white):0 for black in range(columns+1) for white in range(columns+1 - black)}
    dic_fb.pop((columns-1, 1))
    print(dic_fb),input('---')
    
    # dict by pattern vs. feedback
    dic_patt_fb = {}
    #dic_patt_fb = {''.join(map(str, sorted(Counter(allVar).values(),reverse=True))): dict(Counter(feedback(allVar, var) for var in variants)) for allVar in allvariants if ''.join(map(str, sorted(Counter(allVar).values(), reverse=True))) not in dic_patt_fb}
    for allVar in allvariants:
        pattern = ''.join(map(str, sorted(Counter(allVar).values(), reverse=True)))
        if pattern not in dic_patt_fb:
            dic_patt_fb[pattern] = dict(Counter(feedback(allVar, var) for var in variants))
    print(dic_patt_fb),input('---')    
        
    # dict by feedback vs. pattern 
    dic_fb_patt = {}
    for allVar in allvariants:
        pattern = ''.join(map(str, sorted(Counter(allVar).values(), reverse=True)))
        tmp = dict(Counter(feedback(allVar, var) for var in variants))
        for ans, count in tmp.items():
            if ans not in dic_fb_patt:
                dic_fb_patt[ans] = {pattern:count}
            else:
                dic_fb_patt[ans].update({pattern:count})
                #dic_fb_patt[ans][pattern] = count
                #for k,v in dic_fb_patt.items():
                #    if k == ans: v[pattern] = count   
    tmp.clear()
    print(dic_fb_patt),input('===')
    

# ==========================================================
def main():

    print('making the "Table of Answers" ...\n')
    make_table_of_answers()
    print('-- END --')


if __name__ == '__main__': main()
