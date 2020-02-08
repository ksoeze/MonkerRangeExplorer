#!/usr/bin/env python3

#from monker_automation.views import test
#from monker_automation.range import test
#from monker_automation.gui import test
#from monker_automation.analysis import test
#from monker_automation.board import test
from monker_automation.tree import start_walker


def main():
    start_walker()


if __name__ == '__main__':
    main()
    #cProfile.run(main(), sort='cumtime')
