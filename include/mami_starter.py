""" Start Switcher
"""
import time
from concurrent import futures as fs
#import multiprocessing as mp

from .mami_calc import Calculation


class Starter(Calculation):
    """
    start_game
    start_statistic
    start_statistic_loop
    """

    @classmethod
    def start_game(cls):
        """ starts statistic or single mode
        """
        cls.load_tor_file()

        if cls.statistic:
            cls.start_statistic()
        else:
            cls.start_mastermind()

        cls.save_tor_file()


    @classmethod
    def start_statistic(cls):
        """ starts the statistic run for all algorithms
        """
        cls.store_stat_header_to_file()

        # generate all secrets
        cls.code_pool = [cls.gen_variant() for _ in range(cls.stat_runs)]

        algo_set = cls.ALGO_SET if cls.algo_all else [cls.algo]

        temp = cls.algo
        for algo in algo_set:
            cls.algo = algo         # for later use in calculation and output
            cls.start_statistic_loop(algo)
        cls.algo = temp


    @classmethod
    def start_statistic_loop(cls, algo):
        """ starts the statistic run for selected algorithm
        """
        print(f'{"*" * 26}')
        print(f'{"algo":10}: {cls.ALGO_SET[algo]} ({algo})')

        repeats = cls.stat_runs

        # keep the generated response or not?
        # later algos calculation time benefits from
        # distorts the time statistics between the algos
        if cls.tor_loaded and not cls.fb_alternat:
            #cls.tor = cls.tor_imp.copy()
            pass
        elif cls.tor_loaded and cls.fb_alternat:
            #cls.tor.clear()
            pass
        elif not cls.tor_loaded:
            #cls.tor.clear()
            pass

        if cls.fb_alternat:
            cls.fb_calls = 0
            cls.fb_used = cls.fb_reused = 0
            cls.fb_import = cls.fb_generated = 0

        # stat_array [
        #   [run0(step), run1(), ..],
        #   [run0(duration), run1(), ..]]
        stat = [[],[]]

        # Progress indicator
        print(f'{"*" * 6}', end="", flush=True)

        starttime0 = time.perf_counter()
        if not cls.thread:
            progress = 0
            # 10% steps
            step = repeats // 10 if repeats > 9 else 1
            #input(step)

            for code in cls.code_pool:
                progress += 1
                if progress == step:
                    progress = 0
                    print("**", end="", flush=True)  # 10*2 + start = 26 characters in total

                starttime  = time.perf_counter()
                stat[0].append(cls.start_mastermind(code))
                stat[1].append((time.perf_counter() - starttime) * 1000)   #msec

        else:
            def worker1(codelist, codelists):
                a = 20 // len(codelists)
                stat = [[],[]]
                for code in codelist:
                    starttime  = time.perf_counter()
                    stat[0].append(cls.start_mastermind(code))
                    stat[1].append((time.perf_counter() - starttime) * 1000)   #msec
                print(f'{"*" * a}', end="", flush=True)
                return stat

            # threeading without positiv effect
            # multiprocessing also without effect and problems with capseled data managment
            threads = 4
            part = repeats // threads + 1
            codelists = [cls.code_pool[i*part: (i+1)*part] for i in range(threads)]
            while not codelists[-1]:
                codelists.pop()

            with fs.ThreadPoolExecutor(max_workers=threads) as executor:
                futures = [executor.submit(worker1, codelist, codelists) for codelist in codelists]
                results = [future.result() for future in fs.as_completed(futures)]

            for a, b in results:
                stat[0].extend(a)
                stat[1].extend(b)

        stat.append(time.perf_counter() - starttime0)   # type: ignore // sec

        print()
        cls.show_statistics(stat)


# ==========================================================
