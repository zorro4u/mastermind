""" Toolbox
    ColorSet, TimeConverter, ...
"""
from os import system
system("color")


# ==========================================================
# COLOR

class ColorList:
    """ ANSI escape foreground color (30-37)/90-97
    """
    grey    = "\033[90m"
    red     = "\033[91m"
    green   = "\033[92m"
    yellow  = "\033[93m"
    blue    = "\033[94m"
    magenta = "\033[95m"
    cyan    = "\033[96m"
    white   = "\033[97m"
    off     = "\033[0m"


# ==========================================================
# ToolBox

class Toolbox:
    """ collection of tools
    """

    @staticmethod
    def change_time_to_string(sec_to_convert):
        """
            TimeConverter
            0.321456 -> '0.321 sec'
            5.321456 -> '5.32 sec'
            45.32145 -> '45.3 sec'
            105.3214 -> '1m 41s'
            216105.3 -> '2d 12h 1m'
        """
        time_str = ""
        day = hour = minute = 0

        # comma formating
        if sec_to_convert < 0.001:
            second = round(sec_to_convert, 5)
        elif sec_to_convert < 0.5:
            second = round(sec_to_convert, 3)
        elif sec_to_convert < 10:
            second = round(sec_to_convert, 2)
        elif sec_to_convert < 60:
            second = round(sec_to_convert, 1)
        else:
            second = int(round(sec_to_convert))

        # second output, comma formated
        time_list = [second, " sec "]

        # splitted output above one minute
        if second >= 60:
            minute, second = divmod(second, 60)
            time_list = [minute, "m ", second, "s "]

        if minute >= 60:
            hour, minute = divmod(minute, 60)
            time_list = [hour, "h ", minute, "m "]

        if hour >= 24:
            day, hour = divmod(hour, 24)
            time_list = [day, "d ", hour, "h ", minute, "m"]

        # list to string
        for i in time_list:
            time_str += str(i)

        return time_str


        #start = time.perf_counter_ns()
        #print(f'{(time.perf_counter_ns()-start):,d} nsec')
        #timeit('"-".join(str(n) for n in range(100))', number=10_000)


    # ==========================================================
