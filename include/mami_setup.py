""" Setup Maker
    input, output, data check
"""
from statistics import median, multimode
from math import log, factorial as fact
from collections import Counter

from .mami_file import File
from .mami_tools import ColorList as fg   # ColorSet
from .mami_tools import ToolBox as tb           # TimeConverter


class Setup(File):
    """
    show_setup
    change_setup
    show_guess
    show_statistics
    question_change_setup
    question_repeat_game
    show_gameover
    check_setup
    max_char
    max_col
    len_variants
    input_seq
    input_int
    input_bool
    """

    @classmethod
    def show_setup(cls):
        """ show the initial setup after starting the program
        """
        cls.check_setup()

        lang = cls.lang
        msg_setup = (
            f'{lang['lang1'].capitalize():18}: {lang['short']}\n'
            f'{lang['rep']:18}: {not cls.repetition}\n'
            f'{lang['dig']:18}: {cls.numbers}\n'
            f'{lang['char']:18}: {cls.char}\n'
            f'{lang['col']:18}: {cls.columns}\n'
            f'{lang['limit'].capitalize():18}: {cls.limit}\n'
            f'{lang['coder'].capitalize():18}: {cls.autocoder}\n'
            f'{lang['solver'].capitalize():18}: {cls.autosolver}\n'
        )

        if cls.autosolver and cls.algo > 1:
            msg_setup += f'{lang['algo'].capitalize():18}: {cls.ALGO_SET[cls.algo]}\n'

        if cls.algo == 1:
            msg_setup += f'{lang['hint'].capitalize():18}: {cls.show_hint}\n'

        msg_setup += f'{lang['stat']:18}: {cls.statistic}\n'

        if cls.statistic:
            msg_setup += f'{lang['algo_all']:18}: {cls.algo_all}\n'

            if not cls.algo_all and not (cls.autosolver and cls.algo_all > 1):
                msg_setup += f'{lang['algo'].capitalize():18}: {cls.ALGO_SET[cls.algo]}\n'

            msg_setup += (
                f'{"TOR_"+lang['file']:18}: {cls.tor_help}\n'
                f'{lang['runs'].capitalize():18}: {cls.stat_runs:,}\n'
            )
            #msg_setup += (f'{lang['thread']:18}: {cls.thread}\n')

        msg_setup += (
            f'{lang['solu'].capitalize():18}: {cls.len_variants():,d}\n'
            #f'{lang['feedb'].capitalize():18}: {cls.len_variants()**2:,d}\n'
            f'{"-" * 33}'
        )

        print(msg_setup)
        #cls.load_tor_file()


    @classmethod
    def change_setup(cls):
        """ user can show and set the values for the game
        """
        lang = cls.lang
        max_run1 = cls.MAX_RUN1
        max_run2 = cls.MAX_RUN2

        print()

        print(f'# {lang['lang1'].capitalize()}')
        msg = f'  {lang['lang2']+" ":.<19}{fg.grey}{" <"+str(cls.language)+">":8}{fg.off}: '
        x = cls.input_int(msg, max_in=len(cls.LANG_DICT))
        cls.language = x if x != "" else cls.language
        lang = cls.LANG_DICT[1] | cls.LANG_DICT[cls.language]

        msg = (f'# {lang['rep']+" ":.<19}{fg.grey}'
               f'{" ["+str(not cls.repetition)+"]":8}{fg.off}: ')
        x = cls.input_bool(msg)
        cls.repetition = not x if x != "" else cls.repetition

        msg = f'# {lang['dig']+" ":.<19}{fg.grey}{" ["+str(cls.numbers)+"]":8}{fg.off}: '
        x = cls.input_bool(msg)
        cls.numbers = x if x != "" else cls.numbers

        maxi = 10 if cls.numbers else 26
        msg = f'# {lang['char']+" ":.<19}{fg.grey}{" <"+str(cls.char)+">":8}{fg.off}: '
        x = cls.input_int(msg, max_in=maxi, chk_char=True)
        cls.char = x if x != "" else cls.char

        if not cls.repetition:
            maxi = cls.char
        msg = f'# {lang['col']+" ":.<19}{fg.grey}{" <"+str(cls.columns)+">":8}{fg.off}: '
        x = cls.input_int(msg, max_in=maxi, chk_col=True)
        cls.columns = x if x != "" else cls.columns

        msg = (f'# {lang['limit'].capitalize()+" ":.<19}{fg.grey}'
               f'{" <"+str(cls.limit)+">":8}{fg.off}: ')
        x = cls.input_int(msg, max_in=50)
        cls.limit = x if x != "" else cls.limit

        msg = (f'# {lang['coder'].capitalize()+" ":.<19}{fg.grey}'
               f'{" ["+str(cls.autocoder)+"]":8}{fg.off}: ')
        x = cls.input_bool(msg)
        cls.autocoder = x if x != "" else cls.autocoder

        msg = (f'# {lang['solver'].capitalize()+" ":.<19}{fg.grey}'
               f'{" ["+str(cls.autosolver)+"]":8}{fg.off}: ')
        x = cls.input_bool(msg)
        cls.autosolver = x if x != "" else cls.autosolver

        if cls.autosolver:
            print(f'# {lang['alg_A']}')
            msg = f'  {lang['alg_B']+" ":.<19}{fg.grey}{" <"+str(cls.algo)+">":8}{fg.off}: '
            x = cls.input_int(msg, max_in=len(cls.ALGO_SET))
            cls.algo = x if x != "" else cls.algo
        elif not cls.statistic:
            cls.algo = 1      # manual mode only with random algo

        if cls.algo==1:
            msg = (f'# {lang['hint'].capitalize()+" ":.<19}'
                   f'{fg.grey}{" ["+str(cls.show_hint)+"]":8}{fg.off}: ')
            x = cls.input_bool(msg)
            cls.show_hint = x if x != "" else cls.show_hint

        msg = f'# {lang['stat']+" ":.<19}{fg.grey}{" ["+str(cls.statistic)+"]":8}{fg.off}: '
        x = cls.input_bool(msg)
        cls.statistic = x if x != "" else cls.statistic


        if cls.statistic:
            msg = (f'# {lang['algo_all']+" ":.<19}{fg.grey}'
                   f'{" ["+str(cls.algo_all)+"]":8}{fg.off}: ')
            x = cls.input_bool(msg)
            cls.algo_all = x if x != "" else cls.algo_all

            if not cls.algo_all and not cls.autosolver:
                print(f'# {lang['alg_A']}')
                msg = (f'  {lang['alg_B']+" ":.<19}{fg.grey}'
                       f'{" <"+str(cls.algo)+">":8}{fg.off}: ')
                x = cls.input_int(msg, min_in=0, max_in=5)
                cls.algo = x if x != "" else cls.algo

            msg = (f'# {"TOR_"+lang['file']+" ":.<19}{fg.grey}'
                   f'{" ["+str(cls.tor_help)+"]":8}{fg.off}: ')
            x = cls.input_bool(msg)
            cls.tor_help = x if x != "" else cls.tor_help

            _run = f'{cls.stat_runs:,d}'
            runs = f'{" <" + _run + ">":8}'
            if len(runs) > 8:    # change the format above 10,000
                runs = f'{" " + runs:8}'

            if cls.algo_all and cls.stat_runs > max_run2:
                msg = f'# {lang['runs'].capitalize()+" ":.<19}{fg.grey}{runs}{fg.off}: '
                x = cls.input_int(msg, max_in=max_run2)
            else:
                msg = f'# {lang['runs'].capitalize()+" ":.<19}{fg.grey}{runs}{fg.off}: '
                x = cls.input_int(msg, max_in=max_run1)
            cls.stat_runs = x if x != "" else cls.stat_runs

            #msg = (f'(15) {lang['thread']+" ":.<19}{fg.grey}'
            #       f'{" ["+str(cls.thread)+"]":8}{fg.off}: ')
            #x = input_bool(msg)
            #cls.thread = x if x != "" else cls.thread

        print(f'# {lang['solu'].capitalize():27}: {cls.len_variants():,d}')
        #print(f'{lang['feedb'].capitalize():27}: {cls.len_variants()**2:,d}')
        print(f'{"-" * 35}\n')

        cls.lang = lang
        cls.check_setup()

        # run the game after press a button
        msg = "[ Start ] <--| "
        print('\33[2A')                     # cursor: 2up, and 1down for print() = 1up
        key = cls.input_bool(msg)
        key = key if key != "" else True    # input [enter] = 'yes'
        print(f'\33[1A{" "*(len(msg)+10)}\33[{len(msg)+10}D')   # 1up, erase msg, jump left
        if not key:
            print("\33[2A")     # 1up
            cls.question_change_setup()


    @classmethod
    def show_guess(cls, step, guess, new_variants, result, old_variants):
        """ show the guess & feedback
        """
        black, white = result
        len_vari = len(new_variants)
        msg_feedb = f'-> {cls.lang['black'][0]}:{black} {cls.lang['white'][0]}:{white}'
        msg = msg_guess = msg_vari = msg_end = step_right = step_up = ""

        if cls.autosolver:
            msg_guess = f'?_{step:02}: {guess} '

        else:
            step_up = "\033[1A"   # 1x
            if guess in old_variants:
                step_right = f'\033[{6 + cls.columns + 1}C'

            # The guess is not in the reducing variants
            # and has already been cancelled.
            else:
                msg_guess = f'?_{step:02}: {fg.red}{guess}{fg.off} '

        tmp1 = f'{len_vari:,}:'

        if cls.show_hint and cls.algo == 1:
            tmp2 = f' | {tmp1:<5} '
            tmp3 = str(new_variants)
            if len_vari > 3:     # too many variants to show, only 3
                tmp3 = str(new_variants[:3]) + "\033[1D" + ", ...]"
            msg_vari = tmp2 + tmp3
        else:
            msg_vari = f' | {tmp1[:-1]:<5} '


        # not yet solved, show variants
        if black < cls.columns:
            msg = msg_guess + msg_feedb + msg_vari + msg_end


        # solved
        else:
            if cls.autosolver:
                msg_guess = f'{msg_guess}'
                step_up = ""
            else:
                msg_guess = f'?_{step:02}: {guess} '    # same as input_str

            last = fg.green + msg_guess + "-> " + cls.lang['done'].capitalize() + " !" + fg.off
            step_right = ""

            code = cls.lang['secret'].upper()+": " + guess
            up   = f'\033[{step + cls.error_ct + 1}A'
            down = f'\033[{step + cls.error_ct + 1}B'
            left = f'\033[{len(code)}D'
            show_code = up + fg.green + code + fg.off + down + left
            msg = show_code + last

        # len(input_msg)    # 6 + 1x space
        # len(input_user)   # columns
        # jump_right=len(input_msg)+len(input_user)
        # ANSI escape code:
        # \33[4C jump 4x right (= " "*4)
        # \33[1A jump 1x up
        # A B C D : up, down, right, left

        print (step_right + step_up + msg)


    @classmethod
    def show_statistics(cls, stati):
        """ show statistics
        """
        algo_set = cls.ALGO_SET
        algo     = cls.algo
        guesses  = stati[0]
        duration = stati[1]
        #duration = change_time_to_string(stati[1]/1000)
        #alltime = stati[2]
        alltime1 = tb.change_time_to_string(stati[2])
        avg1 = sum(guesses)/len(guesses)     # arithm. Durchschnitt / average
        avg2 = sum(duration)/len(duration)
        med1 = median(guesses)               # zentraler Wert / the average value
        med2 = median(duration)
        mod1 = multimode(guesses)            # häufigste Werte / the most common values
        #mod0 = mode(guesses)                # Modus:häufigster Wert / the most frequent value
        msg_fb = ""

        avg2 = f'{avg2:,.0f}' if avg2>100 else f'{avg2:,.1f}'
        med2 = f'{med2:,.0f}' if med2>100 else f'{med2:,.1f}'

        histo = list(Counter(guesses).items())
        histo = sorted(histo, key=lambda x: x[0], reverse=False)
        hstr = ""
        for k, v in histo:
            hstr += str(k) + "|" + f'{v:,d}' + " "

        msg0 = (
            f'{"*" * 26}\n'
            f'{"algo":10}: {algo_set[algo]} ({algo})\n'
            #f'{"runs":10}: {stat_runs:,}\n'
            #f'{"*" * 26}\n'
        )

        msg = (
            #f'{Counter(guesses)}\n'
            f'{"histo":10}: {hstr}\n'
            #f'{"algo":10}: {algo_set[algo]}\n'
            #f'{"runs":10}: {stat_runs:,}\n'
            f'{fg.cyan}{"average":10}: {avg1:.3f}{fg.off}\n'
            f'{"median":10}: {med1:.1f}\n'
            f'{"modus":10}: {mod1}\n'
            f'{"max.":10}: {max(guesses)}\n'
            f'{"min.":10}: {min(guesses)}\n'
            f'{fg.cyan}{"avg. msec":10}: {avg2}{fg.off}\n'
            f'{"med. msec":10}: {med2}\n'
            #f'{"max. msec":10}: {max(duration):,.1f}\n'
            #f'{"min. msec":10}: {min(duration):,.1f}\n'
            #f'{"max.":10}: {change_time_to_string(max(duration)/1000)}\n'
            #f'{"min.":10}: {change_time_to_string(min(duration)/1000)}\n'
        )
        if cls.fb_alternat:
            msg_fb = (
                f'{"fb_calls":10}: {cls.fb_calls:,d}\n'
                #f'{"fb_combi":10}: {cls.len_variants()**2:,d}\n'
                f'{"fb.reused":10}: {cls.fb_reused:,d}\n'
                f'{"fb.gener.":10}: {cls.fb_generated:,d}\n'
                f'{"fb.import":10}: {cls.fb_import:,d}\n'
                #f'{"fb.used":10}: {cls.fb_used:,d}\n'
                f'{"fb.loaded":10}: {cls.tor_loaded_len:,d}\n'
            )
        msg_end = (
            f'{"-" * 26}\n'
            #f'{"alltime sec":10}: {alltime:,.1f}\n\n'
            f'{"alltime":10}: {alltime1}\n\n'
        )
        msg += msg_fb + msg_end

        print(msg, end="")

        if cls.stat_store:
            stat_msg = msg0 + msg
            cls.store_stat_to_file(stat_msg)


    @classmethod
    def question_change_setup(cls, first=True):
        """ show the setup question and delete it after input
        """
        msg_input = f'{cls.lang['setup']+" ? ":20}'
        key = cls.input_bool(msg_input)
        key = True if key == "" else key
        key_chg = not key
        if key_chg:
            cls.change_setup()

        else:
            len_input = len(msg_input) + 1              # +1: clear normal user input

            if first:
                msg = f'{" " * (len_input + 20)}'       # only erasing with 'space'
            else:
                msg = f'{"-" * len_input}{" " * 20}\n'  # 20: clear crazy long user input

            step_up = "\033[1A"   # ANSI escape code. 1x up
            print(step_up + msg)


    @classmethod
    def question_repeat_game(cls):
        """ show the question and delete the show
        """
        msg_input = f'\n{cls.lang['repeat'].capitalize()+" ?":20}'
        key = cls.input_bool(msg_input)
        return True if key == "" else key


    @classmethod
    def show_gameover(cls, code):
        """ show the string
        """
        print("\n"
            f'{fg.red}-- GAME OVER --{fg.off}\n'
            f'{cls.lang['thecode']} {code}\n'
        )


    # ==========================================================

    @classmethod
    def check_setup(cls):
        """ check the dependencies
        """
        # set language // union two dict (prio: the last)
        cls.lang = cls.LANG_DICT[1] | cls.LANG_DICT[cls.language]

        # max. 10 digits or 26 letters
        if cls.numbers and (cls.char > 10):
            cls.char = 10
        elif not cls.numbers and cls.char > 26:
            cls.char = 26

        # adjusts columns
        if not cls.repetition and (cls.columns > cls.char):
            cls.columns = cls.char

        # makes a set of characters
        if cls.numbers:
            cls.char_set = list(cls.DIGITS[:cls.char])  # cuts the string from the left
        else:
            cls.char_set = list(cls.LETTERS[:cls.char])
            #cls.dic_ld = dict(zip(cls.LETTERS, [ord(x) for x in cls.LETTERS]))
            #cls.dic_dl = {v: k for k, v in cls.dic_ld.items()}
            #cls.char_set = list(cls.dic_dl.keys())[:cls.char]

        # in statistic option no manual mode
        #if cls.statistic:
        #    cls.autocoder = True
        #    cls.autosolver = True

        # in manual mode no statistic option
        #if not cls.autocoder or not cls.autosolver:
        #    cls.statistic = False

        # game mode only with random algo
        if not cls.statistic and not cls.autosolver:
            cls.algo = 1

        # always save statistic
        if cls.statistic and cls.stat_runs >= cls.STORE_STAT:
            cls.stat_store = True

        # game mode without TOR helper file
        if not cls.statistic:
            cls.tor_help = False

        # cut the complexity and set char/col down
        cls.char = cls.max_char(cls.char)
        cls.columns = cls.max_col(cls.columns)


    @classmethod
    def max_char(cls, char):
        """ cut the complexity and set char down
            (1): var=char**col .. char=var**1/col .. col=log(var,char)=log(var)/log(char)
            (2): var=char!//(char-col)! .. no inverse function exist
        """
        if cls.repetition:
            variants = char ** cls.columns
            if variants > cls.MAX_VARIANTS:
                char = int(cls.MAX_VARIANTS**(1/float(cls.columns)))
            return char

        else:
            variants = fact(char) // fact(char - cls.columns)
            while variants > cls.MAX_VARIANTS:
                char -= 1
                variants = fact(char) // fact(char - cls.columns)
            return char


    @classmethod
    def max_col(cls, col):
        """ cut the complexity and set char down
            var=char**col .. char=var**1/col .. col=log(var,char)=log(var)/log(char)
        """
        if cls.repetition:
            variants = cls.char ** col
            if variants > cls.MAX_VARIANTS:
                col = int(log(cls.MAX_VARIANTS, cls.char))
            return col

        else:
            variants = fact(cls.char) // fact(cls.char - col)
            while variants > cls.MAX_VARIANTS:
                col -= 1
                variants = fact(cls.char) // fact(cls.char - col)
            return col


    @classmethod
    def len_variants(cls):
        """ returns the theoretical lenght of all variants
            w/  repetition: char ** columns                             = len(variants)
            w/o repetition: factorial(char) // factorial(char-columns)  = len(variants)
            x**y = x^y -- factorial(5) = 5! = 5*4*3*2*1
        """
        repetition = cls.repetition
        columns =    cls.columns
        char =       cls.char

        cls.len_vari = char ** columns if repetition else fact(char) // fact(char - columns)

        return cls.len_vari


    # ==========================================================

    @classmethod
    def input_seq(cls, text, manu_coder=False):
        """ returns the code/guess string as input value
        """
        while True:
            try:
                seq = input(text).upper()
                if len(seq) != cls.columns:
                    raise KeyboardInterrupt(f'{fg.magenta}{cls.lang['in1']}...{fg.off}')

                for char in seq:
                    if char not in cls.char_set:
                        raise KeyboardInterrupt(f'{fg.magenta}{cls.lang['in2']}...{fg.off}')

                    if not cls.repetition and seq.count(char) > 1:
                        raise KeyboardInterrupt(f'{fg.magenta}{cls.lang['in3']}...{fg.off}')

                return seq

            except KeyboardInterrupt as error:
                # find the right upper line to show the unhidden code at the end
                if not manu_coder:
                    cls.error_ct += 1
                elif cls.error_ct > 0:
                    cls.error_ct -= 1

                up = "\033[1A"
                right = f'\033[{6 + cls.columns + 4}C'
                print(up + right + str(error))


    @classmethod
    def input_int(cls, text, min_in=1, max_in=10, **chk):
        """ returns an integer as input value
        """
        while True:
            try:
                x = input(text)

                if x != "":
                    x = int(x)
                    if x < min_in or x > max_in:
                        x = int("error")  # Exception ValueError

                    # check the range of allowed complexity
                    if "chk_char" in chk and chk["chk_char"]:
                        max_in = cls.max_char(x)
                    elif "chk_col" in chk and chk["chk_col"]:
                        max_in = cls.max_col(x)

                    if x > max_in:
                        x = int("error")

                # no input but setup error
                elif "chk_char" in chk and chk["chk_char"]:
                    max_in = cls.max_char(cls.char)
                    if cls.char > max_in:
                        x = int("error")
                elif "chk_col" in chk and chk["chk_col"]:
                    max_in = cls.max_col(cls.columns)
                    if cls.columns > max_in:
                        x = int("error")

                return x
            except ValueError:
                print(f'{fg.magenta}{cls.lang['only1']}: {min_in}-{max_in}{fg.off}')


    @classmethod
    def input_bool(cls, text):
        """ returns a boolean as input value
        """
        while True:
            try:
                x = input(text)

                if x != "":

                    # input as letter -> digit
                    y = ["y", "yes"] + cls.lang['yes']
                    n = ["n", "no", "2"] + cls.lang['no']
                    if x.lower() in y:
                        x = 1
                    elif x.lower() in n:
                        x = 0
                    x = int(x)

                    if x < 0 or x > 1:    # only 0/1
                        x = int("error")  # Exception ValueError

                    return bool(x)
                return x
            except ValueError:
                print(f'{fg.magenta}{cls.lang['only2']}{fg.off}')


# ==========================================================
