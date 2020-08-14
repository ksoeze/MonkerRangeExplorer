#!/usr/bin/env python3
from monker_automation.analysis import current_spot

if __name__ == '__main__':
    #current_spot("DEFAULT")
    current_spot("MADE_HANDS")
    #current_spot("DRAWS_BLOCKERS")
    #current_spot("MADE_HANDS", "DRAWS_BLOCKERS", False)
    #current_spot("MADE_HANDS","BLOCKERS", False)
    #current_spot("DRAWS", "MADE_HANDS", False)
    #current_spot("DRAWS", "BLOCKERS", False)
    #current_spot("BLOCKERS", "MADE_HANDS", False)
    #current_spot("BLOCKERS")
    #current_spot("DRAWS")