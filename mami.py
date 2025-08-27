""" <2021, 2025> https://github.com/zorro4u/mastermind
"""
from include import ColorList as fg
from include import Starter

# ==========================================================

class Mastermind(Starter):
    """ start it with run()
    """

    @classmethod
    def run(cls):
        """ mastermind main call
        """
        first = True
        key   = True
        while key:
            if first:
                cls.show_setup()
            cls.question_change_setup(first)

            cls.start_game()

            key = cls.question_repeat_game()
            first = False

        print("\n-- " + cls.lang['end'].upper() + " --\n")


# ==========================================================

def main():
    """ starts mastermind
    """
    print("\n", __doc__)
    print(f'{fg.yellow}-- MasterMind --{fg.off}')
    print(f'{"=" * 24}\n')

    Mastermind.run()

# ==========================================================

if __name__ == '__main__':
    main()
