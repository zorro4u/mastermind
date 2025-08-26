""" File Handler
"""
from pathlib import Path
from datetime import datetime
import pickle
import bz2

from .mami_init import Init


class File(Init):
    """
    load_tor_file
    save_tor_file
    store_stat_header_to_file
    store_stat_to_file
    """

    @classmethod
    def load_tor_file(cls):
        """ TOR: {guess: {code: (black, white),..}, ... }
        """
        path_to_load = Path(cls.MY_PATH, cls.TOR_DIR)

        if cls.tor_help:
            if cls.tor_loaded:
                return

            filename = Path(path_to_load, cls.TOR_NAME + ".bz2")
            cls.tor_imp.clear()
            cls.tor.clear()
            tor = {}

            print("Table_Of_Responses " + cls.lang['loading'] + " ... ", end="", flush=True)

            if Path(filename).is_file():
                file = bz2.BZ2File(filename, "r")
                tor = pickle.load(file)
                file.close()
                print(cls.lang['done']+"\n")
            else:
                print(cls.lang['nfound']+"\n")

            cls.tor_imp = tor.copy()
            if not cls.fb_alternat:
                cls.tor = tor

            cls.tor_loaded = True
            cls.tor_loaded_len = sum([len(tor[x]) for x in tor])

        # without TOR_file
        elif cls.tor_loaded:
            cls.tor.clear()
            cls.tor_imp.clear()
            cls.tor_loaded = False
            cls.tor_loaded_len = 0


    @classmethod
    def save_tor_file(cls):
        """ save the TOR to file
        """
        if cls.tor_loaded:
            path_to_store = Path(cls.MY_PATH, cls.TOR_DIR)
            filename = Path(path_to_store, cls.TOR_NAME + ".bz2")

            tor_len = sum([len(v) for k, v in cls.tor.items()])

            if tor_len > cls.tor_loaded_len:
                print("\n" + "Table_Of_Responses " + cls.lang['storing'] + " ... ", end="")
                file = bz2.BZ2File(filename, "w")
                pickle.dump(cls.tor, file)
                file.close()
                print(cls.lang['done'])


    @classmethod
    def store_stat_header_to_file(cls):
        """ save stats header to file
        """
        path_to_store = Path(cls.MY_PATH, cls.STAT_DIR)
        msg_head = ""
        mode = "a"      # default: write attend

        # always save statistic as a new file
        if cls.stat_runs >= 5000:
            #mode = "w"  # write as new file
            pass

        if cls.stat_store:
            stat_file = Path(path_to_store, cls.STAT_FILE + ".txt")
            if stat_file.is_file():
                msg_head = "\n"

            date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            msg_date = (
                f'{"=" * 26}\n'
                f'[{date}]\n'
                f'{"=" * 26}\n'
            )
            msg_setup = (
                f'{cls.lang['rep']:18}: {cls.repetition}\n'
                f'{cls.lang['char']:18}: {cls.char}\n'
                f'{cls.lang['col']:18}: {cls.columns}\n'
                f'{cls.lang['solu'].capitalize():18}: {cls.len_vari:,d}\n'
                f'{"TOR_"+cls.lang['file']:18}: {cls.tor_help}\n'
                f'{cls.lang['runs'].capitalize():18}: {cls.stat_runs:,}\n\n'
            )
            msg_head += msg_date + msg_setup

            with open(stat_file, mode, encoding="utf-8") as file:
                file.write(msg_head)


    @classmethod
    def store_stat_to_file(cls, stat_msg):
        """ save the statistic values to file
        """
        path_to_store = Path(cls.MY_PATH, cls.STAT_DIR)
        stat_msg = stat_msg.replace("\033[96m", "")
        stat_msg = stat_msg.replace("\033[0m", "")
        stat_file = Path(path_to_store, cls.STAT_FILE + ".txt")
        with open(stat_file,"a", encoding="utf-8") as file:
            file.write(stat_msg)


    # ==========================================================
