""" Initialisation
"""
from pathlib import Path
import string

from .mami_lang import EN, GER, FRA                 # Language Package


class Init:
    """ Global Working Values
    """

    # ==========================================================
    # Initial User Values

    language   = 1       # Language of outputs: en:1, de:2, fr:3
    char       = 6
    columns    = 4
    limit      = 10
    repetition = True    # repetition of a character: yes
    numbers    = True    # digits (or letters) as character: yes
    autocoder  = True    # the code maker, automatic
    autosolver = False   # the code breaker, automatic
    show_hint  = True    # give a hint in manual solver mode
    statistic  = False   # a special mode to determine avg of guesses
    algo       = 1       # solver algorithm: Random:1, Knuth:2, Kooi:3, Irving:4
    algo_all   = True    # all algoritm in statistic mode
    stat_runs  = 100     # runs for statistic mode

    stat_store = False   # save statistic results to file (automatic from 5000 runs)
    tor_help   = True    # use the tor_helper file // Table_Of_Responses

    STAT_FILE  = "mami_stat"  # name of stored statistic file (w/o .extension ".txt")
    TOR_NAME   = "tor"        # name of loaded/stored TOR file (w/o .extension ".bz2")

    STAT_DIR   = ""           # SubDir to statistic file
    TOR_DIR    = "include"    # SubDir to TOR file

    MY_PATH    = Path.cwd()   # path to this project


    # ==========================================================
    # generally used variables/values/properties

    # available language packages
    LANG_DICT    = {1: EN, 2: GER, 3: FRA}
    LETTERS      = string.ascii_uppercase
    DIGITS       = "1234567890"

    MAX_VARIANTS = 10**7    # cut the range of char/col combinations
    MAX_RUN1     = 100_000  # limit the statistic runs
    MAX_RUN2     = 10_000   # algo > 1 are time-consuming
    STORE_STAT   = 5_000    # runs from which the statistic results are automatically saved to file

    prev_guesses = []    # contains all previous guesses
    error_ct   = 0       # for show input error
    char_set   = []      # [0,1,2,..] will be set later on 'check_setup'
    lang       = {}      # working language dictionary
    len_vari   = 0       # number of variants
    secret     = ""      # single code
    code_pool  = []      # all generated secrets
    tor        = {}      # feedback dict: Table_Of_Responses
    tor_imp    = {}      # imported TOR
    tor_loaded = False   # TOR file is loaded
    tor_loaded_len = 0   # number of loaded responses from file
    thread     = False   # statistic run in multi-thread/processor mode // bad realisation :-(

    # solver modes
    ALGO_SET = {
        1 : "Random",
        2 : "Knuth",
        3 : "Kooi",
        4 : "Irving",
    }

    fb_alternat = False  #  Feedb Variant with more counts but slowier
    fb_calls  = 0        # fb_call
    fb_used   = 0        # fbL_used
    fb_reused = 0        # fbL_reused
    fb_import = 0        # fbI_used
    fb_generated = 0     # fb_new_generate


# ==========================================================
