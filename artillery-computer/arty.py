# arty.py
# A script to calculate a firing solution for 82mm Mk6 mortars in ArmA 3 using the Ace 3 mortar system.

from arty_computer import Mk6Mortar_ArtilleryComputer, Solution, GridRef, FailedFiringSolutionError
import csv
import traceback
from typing import Tuple
from colorama import just_fix_windows_console, Fore
just_fix_windows_console()


def get_option(prompt, options=False, num=False, first_char_only=False):
    o = ""
    while True:
        o = input(Fore.LIGHTBLACK_EX + prompt + Fore.GREEN)
        if not num:
            if options:
                if o.lower() in options:
                    o = o[0] if first_char_only else o
                    break
            break
        try:
            o = int(o)
            break
        except ValueError as e:
            print(e)
            continue
    print(Fore.RESET, end='')
    return o

if __name__ == "__main__":

    mk6 = Mk6Mortar_ArtilleryComputer()


    manual = get_option("GRID / DIST [GRID]:", ["grid", "dist", "g", "d"], first_char_only=True)
    manual = True if manual == "d" else False
    while True:
        sol = None
        if manual:
            azi = get_option("AZIMUTH :", num=True)
            dist = get_option("DISTANCE :", num=True)
            art_e = get_option("ART_ELEV :", num=True)
            tgt_e = get_option("TGT_ELEV :", num=True)
            name = get_option("SOL NAME :")

            sol = mk6.new_manual_solution(azi, dist, art_e, tgt_e, name)

        else:
            art_g = get_option("ART 6-GRIDREF [XXX YYY]:")
            tgt_g = get_option("TGT 6-GRIDREF [XXX YYY]:")
            art_e = get_option("ART_ELEV :", num=True)
            tgt_e = get_option("TGT_ELEV :", num=True)
            name = get_option("SOL NAME :")

            sol = mk6.new_solution(GridRef(*[int(x) for x in art_g.split(" ")]), art_e, GridRef(*[int(x) for x in tgt_g.split(" ")]), tgt_e, name)

        mk6.print_possible_charges(sol)
        try:
            mk6.calc_firing_solution(sol)
            print(sol)
            save = get_option(f"SAVE SOLUTION ({name}.csv) [Y/N]?")
            if save.lower() in ['y', 'yes']:
                sol.save(f"{name}.csv")

        except FailedFiringSolutionError as e:
            print(Fore.RED, e.error, Fore.RESET)

    # test_sol = mk6.new_solution(GridRef(183,154), 48, GridRef(188,158), 22, "Charkia N Defense")
    # print(test_sol)
    # mk6.update_atmos(test_sol, 19.9, 200, 12.7)
    # mk6.print_possible_charges(test_sol)
    # mk6.calc_firing_solution(test_sol, preferred_charge="lowest")
    # print(test_sol)
    # print("=====================\n\n")

    # distance_sol = mk6.new_manual_solution(913, 640, 48, 22, "Manual Test")
    # print(distance_sol)
    # mk6.print_possible_charges(distance_sol)
    # mk6.calc_firing_solution(distance_sol)
    # print(distance_sol)