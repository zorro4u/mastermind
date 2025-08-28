""" Mastermind Core Routine
"""
import random
from itertools import product, permutations as perm
from collections import Counter
from functools import lru_cache

from .mami_setup import Setup


class Calculation(Setup):
    """
    start_mastermind
    gen_allvariants
    gen_variants
    feedback
    get_guess
    random_mode
    knuth_mode
    kooi_mode
    irvi_mode
    first_pattern
    """

    @classmethod
    def start_mastermind(cls, code=""):
        """ Mastermind core routine
        """
        columns = cls.columns

        # determines all solutions
        allvariants = cls.gen_allvariants()
        variants    = allvariants.copy()
        #variants    = deepcopy(allvariants)

        # generates a single random code to be found
        if not code:
            if cls.autocoder:
                code = cls.gen_variant()
                print(f'{cls.lang['secret']+":":6}{"*" * columns}\n')
            else:
                msg_input = cls.lang['secret'].upper() + ": " + "_" * columns + f"\33[{columns}D"
                code = cls.input_seq(msg_input, True)

                # hide the input
                up = "\033[1A"
                code_hide = cls.lang['secret'] + ": " + "*" * columns
                print(up + code_hide + "\n")

        cls.secret = code
        prev_guesses = []
        step = black = 0
        while black < columns and step < cls.limit:
            step += 1

            # gets a guess
            if cls.statistic or cls.autosolver:
                guess = cls.get_guess(step, variants, allvariants)
            else:
                guess = cls.input_seq(f'?_{step:02}: ')

            # gets a feedback for 'guess' vs. 'code'
            answer = black, _ = cls.feedback(guess, code)

            # Filters out those with the same answer pattern for the current guess
            # from the current variant pool. The current guess is omitted. The right
            # variant will always be there until the end.
            # (-> bottle neck)
            new_variants = [vari for vari in variants if cls.feedback(guess, vari) == answer]

            if not cls.statistic:
                cls.show_guess(step, guess, new_variants, answer, variants)

            # ready for a new guess
            variants = new_variants
            prev_guesses.append(guess)

            cls.prev_guesses = prev_guesses

        if black != columns and not cls.statistic:
            cls.show_gameover(code)

        # clear working variables
        cls.prev_guesses = []
        cls.error_ct = 0

        return step


    @classmethod
    def gen_allvariants(cls):
        """ generates a string set of all possible variants
            from 'char_set' with the number of 'columns'
            w/  repetition: cartesian product
            w/o repetition: permutation
            product('ABCD', repeat=2) = AA AB AC AD BA BB BC BD CA CB CC CD DA DB DC DD
            permutations('ABCD', 2) =   AB AC AD BA BC BD CA CB CD DA DB DC
        """
        columns  = cls.columns
        char_set = cls.char_set

        #string tuple of variants,
        # product:     (cartesian product, equivalent to a nested for-loop)
        # permutation: (r-length tuples, all possible orderings, no repeated elements)
        vari = product(char_set, repeat=columns) if cls.repetition else perm(char_set, columns)

        # merge the single list to string & added to list of vari_strings
        return ["".join(map(str, i)) for i in vari]


    @classmethod
    def gen_variant(cls):
        """ generates a random variant as a string
            from 'char_set' with the number of 'columns'
        """
        col = cls.columns
        char_set = cls.char_set

        ## list of char
        seq = random.choices(char_set, k=col) if cls.repetition else random.sample(char_set, col)

        return "".join(map(str, seq))   # string


    @classmethod
    @lru_cache()   # not on processor mode
    def feedback(cls, guess, code):
        """ feedback switcher
        """
        if not cls.fb_alternat:
            return cls.feedback_0(guess, code)
        else:
            return cls.feedback_1(guess, code)


    @classmethod
    @lru_cache()   # not on processor mode
    def feedback_0(cls, guess, code):
        """ tests 'guess' for 'code':
            black pin: char and position are correct
            white pin: char is correct, position is wrong

            TOR: {guess: {code: (black, white),.. }, ... }
        """
        # if previous calculated and stored in database, use it
        try:
            return cls.tor[guess][code]
        except KeyError:
            pass

        # forms pairs from both lists [(0. 0.) (1. 1.) ...], then compares both elements
        black = sum(x==y for x, y in zip(guess, code))

        # counts frequency of characters / histogram
        # returns the sum of the the smallest match
        white = sum(min(guess.count(x), code.count(x)) for x in cls.char_set)

        # avoid double counting of white (even if black)
        white -= black

        # store in Table_Of_Responses database
        try:
            cls.tor[guess]
        except KeyError:
            cls.tor[guess] = {}
        finally:
            cls.tor[guess][code] = black, white

        return black, white       # integer


    @classmethod
    @lru_cache()   # not on processor mode
    def feedback_1(cls, guess, code):
        """ tests 'guess' for 'code':
            black pin: char and position are correct
            white pin: char is correct, position is wrong

            feedback = var^2
            'feedback' at 6/4:
            random 1,600
            knuth, irvi, kooi: 2,000,000

            TOR: {guess: {code: (black, white),.. }, ... }

            routine with more statistic counter, slowier
        """
        tor = cls.tor     # array/dict: this is a pointer operation to the same object, not a copy
        tor_imp = cls.tor_imp     # file imported TOR

        # if previous calculated and stored in database, use it
        # change into int_transformed_numbers, smaller database
        # but the change _here_ costs a lot of time
        #c = int(code) if cls.numbers else int(w2n(code))
        #g = int(guess) if cls.numbers else int(w2n(guess))
        c = code
        g = guess

        cls.fb_calls += 1       # feedb calls
        cls.fb_reused += 1      # fbL_reused

        try:
            black, white = tor[g][c]
        except KeyError:
            cls.fb_reused -= 1  # fbL_reused
            cls.fb_used += 1    # fbL_used

            cls.fb_import += 1  # fbI_used
            try:
                black, white = tor_imp[g][c]
            except KeyError:
                cls.fb_import -= 1     # found fb in imported TOR
                cls.fb_generated += 1  # new fb generated

                # forms pairs from both lists [(0. 0.) (1. 1.) ...], then compares both elements
                black = sum(x==y for x, y in zip(guess, code))

                # counts frequency of characters / histogram
                # returns the sum of the the smallest match
                white = sum(min(guess.count(x), code.count(x)) for x in cls.char_set)     # faster
                #white = sum((Counter(guess) & Counter(code)).values())

                # avoid double counting of white (even if black)
                white -= black

            # store in Table_Of_Responses database (with int_transformed_numbers)
            try:
                tor[g]
            except KeyError:
                tor[g] = {}
            finally:
                tor[g][c] = black, white

        #cls.tor = tor    # not necessary, array/dict: this is a pointer operation

        return black, white       # integer


    @classmethod
    def get_guess(cls, step, variants, allvariants):
        """ selects an item from a list of variants:
        """
        algo = cls.algo

        if algo == 1:
            return cls.random_mode(step, variants)
        if algo == 2:
            return cls.knuth_mode(variants, allvariants)
        if algo == 3:
            return cls.kooi_mode(variants, allvariants)
        if algo == 4:
            return cls.irvi_mode(variants, allvariants)


    @classmethod
    def random_mode(cls, step, variants):
        """ (1) selects a random element from the 'variants' list
            random modify: calculate the first one, only in manual mode
        """
        if  cls.statistic or step > 1:
            return random.sample(variants, 1)[0]    # string

        # step == 1, special first pattern
        else:
            # returns the one with the maximal elimination
            # 1122, 1123, 1234, random
            if cls.repetition:
                first = [cls.first_pattern(0), cls.first_pattern(1), cls.first_pattern(2)]
                        #,random.sample(variants, 1)[0]]
            else:
                first = [cls.first_pattern()]   # 1234

            res = []
            for guess in first:
                answer = cls.feedback(guess, cls.secret)
                new_variants = [vari for vari in variants if cls.feedback(guess, vari) == answer]
                res.append((guess, len(new_variants)))

            return min(res, key=lambda x: x[1])[0]


    @classmethod
    def knuth_mode(cls, variants, allvariants):
        """ (2) Knuth (worst-case-strategy), five-guess-algo
            1st best pattern: '1122' -- does not necessarily have to be calculated
            this realisation based: https://github.com/Joshua-Noble/Mastermind-Solver
        """
        # first
        if len(variants) == len(allvariants):
            return cls.first_pattern(0)
        # last
        if len(variants) == 1:
            return variants[0]

        best_max = []
        for allvari in allvariants:
            # skip previous guesses
            if not allvari in cls.prev_guesses:
                # store feedbacks (allvari_vs_variants) and vari
                # sorted by feedback
                # [((0,0),v1), ((0,0),v9), ((0,1),v21), ...]
                #data = [(feedback(allvari, var), var) for var in variants]
                #data = sorted(data, key=lambda x: x[0])   # sort by first element

                # variants grouped by feedbacks
                # groups: [(feedb1, group1),..]
                # [((0,0), [v1,v9,...]), ((0,1), [v10,v21,v87,...]), ...]
                #groups = groupby(data, lambda x: x[0])    # group by first element

                # counts lenght of group1/group2/...
                # and returns the highest
                #max_grp = 0
                #for _, group in groups:
                #    max_grp = max(max_grp, len(list(group)))

                histo = Counter(cls.feedback(allvari, var) for var in variants)
                max_grp = max(histo.values())

                # store allvari and its max_grp,
                # the feedback with the greatest response
                best_max.append((allvari, max_grp))

        # the lowest of high group counts // the worst case
        min_grp = min(best_max, key=lambda x: x[1])[1]

        # the important last part to reduce the average ...
        # get the min_variant for the best worst-case-senario
        # primary from the current (reduced) pool / variants
        # otherwise the first one from the general pool / allvariants
        first = True
        next_guess = ""
        for allvari, max_grp in best_max:
            if max_grp == min_grp:
                if allvari in variants:
                    next_guess = allvari
                    break
                if first:
                    next_guess = allvari
                    first = False

        return next_guess


    @classmethod
    def kooi_mode(cls, variants, allvariants):
        """ (3) Kooi (most-parts-strategy), most best average
            1st best pattern '1123' or '1234'
        """
        # first
        if len(variants) == len(allvariants):
            return cls.first_pattern(1)
        # last
        if len(variants) == 1:
            return variants[0]

        fdb_counter = []
        for allvari in allvariants:
            # skip previous guesses
            if not allvari in cls.prev_guesses:
                # store feedbacks (allvari_vs_variants)
                # [(0,0), (0,0), (0,1), ...]

                # Counter(): merge feedbs and count it, dict((0,0):ct1, (0,1):ct2, ...)
                # len(): counts the feedbacks in the dict
                # store allvari and its feedback_counter
                count_fdb = len(Counter(cls.feedback(allvari, var) for var in variants))

                fdb_counter.append((allvari, count_fdb))

        # the highest feedback_counter
        max_fdb = max(fdb_counter, key=lambda x: x[1])[1]

        # the important last part to reduce the average ...
        # get the max_variant ...
        # primary from the current (reduced) pool / variants
        # otherwise the first one from the general pool / allvariants
        first = True
        next_guess = ""
        for allvari, count_fdb in fdb_counter:
            if count_fdb == max_fdb:
                if allvari in variants:
                    next_guess = allvari
                    break
                if first:
                    next_guess = allvari
                    first = False

        return next_guess


    @classmethod
    def irvi_mode(cls, variants, allvariants):
        """ (4) Irving (expected-size-strategy), 1st best pattern '1123'
        """
        # first
        if len(variants) == len(allvariants):
            return cls.first_pattern(1)
        # last
        if len(variants) == 1:
            return variants[0]

        exp_size = []
        for allvari in allvariants:
            # skip previous guesses
            if not allvari in cls.prev_guesses:
                histo = Counter(cls.feedback(allvari, var) for var in variants)
                expsize = 0
                for value in histo.values():
                    expsize += value**2
                expsize /= cls.len_vari
                exp_size.append((allvari, expsize))

        # the lowest
        min_size = min(exp_size, key=lambda x: x[1])[1]

        # the important last part to reduce the average ...
        # get the min_variant ...
        # primary from the current (reduced) pool / variants
        # otherwise the first one from the general pool / allvariants
        first = True
        next_guess = ""

        for allvari, expsize in exp_size:
            if expsize == min_size:
                if allvari in variants:
                    next_guess = allvari
                    break
                if first:
                    next_guess = allvari
                    first = False

        return next_guess


    @classmethod
    def first_pattern(cls, scheme=0):
        """ pattern scheme:
            (0): '1122', '11223'
            (1): '1123', '11223'
            (2): '1234'
        """
        columns =  cls.columns
        char_set = cls.char_set
        char =     cls.char

        if not cls.repetition or (scheme == 2 and columns <= char):
            return "".join(map(str,[char_set[col] for col in range(columns)]))

        # with repetition
        pattern = []
        i = 0
        for col in range(columns):
            i = i if i < char else char-1
            pattern.append(char_set[i])

            # odd column position, next character
            if col % 2:
                i += 1

        # array -> string
        pattern = "".join(map(str, pattern))

        # replace last character with next, '1122'->'1123'
        even = not columns % 2    # if even number of columns = 1 else 0
        if scheme != 0 and even and columns <= char:
            pattern = pattern[:-1] + str(char_set[i])

        return pattern


# ==========================================================
