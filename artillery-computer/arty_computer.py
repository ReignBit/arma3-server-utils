import csv
from typing import List, Tuple
from datetime import datetime
import math
from colorama import just_fix_windows_console, Fore
just_fix_windows_console()

class FailedFiringSolutionError(Exception):
    def __init__(self, msg):
        self.error = msg
        super().__init__(msg)

class GridRef:
    def __init__(self, e, n):
        self.e = e
        self.n = n

    def __str__(self):
        return f"({self.e},{self.n})"

    def __repr__(self):
        return f"({self.e},{self.n})"

def calc_azimuth(a: GridRef, b: GridRef) -> Tuple[float, float]:
    diff_e = b.e - a.e
    diff_n = b.n - a.n

    # Calculate the straight-line distance (hypotenuse)
    calculated_distance = math.sqrt(diff_e**2 + diff_n**2) * 100

    # Handle special cases where the angle is exactly 90° or 270° 
    if diff_e > 0 and diff_n == 0:
        return calculated_distance, 90   # Directly East
    if diff_e < 0 and diff_n == 0:
        return calculated_distance, 270  # Directly West
    if diff_e == 0 and diff_n > 0:
        return calculated_distance, 0    # Directly North
    if diff_e == 0 and diff_n < 0:
        return calculated_distance, 180  # Directly South

    # Calculate the azimuth angle using atan2, which correctly accounts for quadrants
    azimuth = math.degrees(math.atan2(diff_e, diff_n))  # atan2(y, x) avoids division by zero

    # Ensure azimuth is in the 0-360° range
    if azimuth < 0:
        azimuth += 360

    return calculated_distance, azimuth
def calc_elev_diff(a, b):
    if a > b:
        return a - b
    return b - a

class Solution:
    POSSIBLE_OUTDATED_PERIOD = 60*60*60 # 1 hour
    def __init__(self, art_pos: GridRef, art_elev: int, tgt_pos: GridRef, tgt_elev: int, name="Unnamed Solution", azimuth=-1, distance=-1):
        self.artillery_pos = art_pos
        self.target_pos = tgt_pos

        self.artillery_elev = art_elev
        self.target_elev = tgt_elev
        self.elevation_diff = calc_elev_diff(art_elev, tgt_elev)
        
        # TODO: Possibly in the future
        self.temperature = 15.0
        self.air_density = 0.0
        self.humidity    = 0.0

        # solution
        self.charge  = 0

        if self.artillery_pos and self.target_pos:
            self.calc_dist, self.azimuth = calc_azimuth(self.artillery_pos, self.target_pos)
            self.azimuth_mildot = round((self.azimuth * 6400) / 360)
        else:
            self.calc_dist = distance
            self.azimuth = azimuth
            self.azimuth_mildot = azimuth
        self.elevation = 0
        self.time_of_flight = 0
        
        # metadata
        self.name = name
        self.time_solved = 0
        self.solved_for: ArtilleryComputer = None

    @classmethod
    def from_distance(cls, azimuth: int, distance: int, art_elev: int, tgt_elev: int, name="Unnamed Solution"):
        return cls(None, art_elev, None, tgt_elev, name, azimuth=azimuth, distance=distance)

    def __str__(self):
        return f"""
    {Fore.LIGHTBLACK_EX}ARTILLERY GRIDREF:
        {Fore.GREEN}{self.artillery_pos or 'MANUAL'} @ {self.artillery_elev}m ASL
    {Fore.LIGHTBLACK_EX}TARGET GRIDREF:
        {Fore.GREEN}{self.target_pos or 'MANUAL'} @ {self.target_elev}m ASL
    {Fore.LIGHTBLACK_EX}Distance:
        {Fore.GREEN}~{self.calc_dist:.2f}m
    {Fore.LIGHTBLACK_EX}Azimuth:
        {Fore.GREEN}{self.azimuth:.2f}° / {self.azimuth_mildot}mil{Fore.RESET}
Solution: {'Not Calculated' if self.time_solved == 0 else 'C:' + str(self.charge) + ', A:' + str(self.azimuth_mildot) + ', E: ' + str(self.elevation) + ' in ~' + str(self.time_of_flight) + 's'}"""
    
    def solve(self, charge, elev, tof=0.0):
        """Provide the firing solution data"""
        self.charge = charge
        self.elevation = elev
        self.time_solved = datetime.now()
        self.time_of_flight = tof

    def save(self, filename):
        with open(filename, "w") as f:
            f.write()

    def is_old(self):
        if self.time_solved == 0:
            return False
        return datetime.now() - self.time_solved > Solution.POSSIBLE_OUTDATED_PERIOD


class ArtilleryComputer:
    def __init__(self, table_name):
        self.table_name = table_name
        self._rangetable = []
        self.load_table()

        self.solutions = {}

    def load_table(self):
        with open(self.table_name) as csvfile:
            csv_f = csv.reader(csvfile)
            next(csv_f, None)
            for row in csv_f:
                charge,range,elev,d_elev,d_tof,tof = row
                charge = int(charge)
                range = int(range)
                elev = int(elev)
                d_elev = float(d_elev)
                d_tof = float(d_tof)
                tof = float(tof)
                
                if len(self._rangetable) <= charge:
                    self._rangetable.append({})

                self._rangetable[charge][range] = {"elev": elev, "d_elev": d_elev, "d_tof": d_tof, "tof": tof}
        
        total = sum([len(j.keys()) for j in [x for x in self._rangetable]])
        print(f"Loaded {len(self._rangetable)} charges, total {total} range values.")

    def new_solution(self, art_grid: GridRef, art_elev: int, tgt_grid: GridRef, tgt_elev: int, name) -> Solution:
        print(f"New solution started \"{name}\"")
        return Solution(art_grid, art_elev, tgt_grid, tgt_elev, name)
    
    def new_manual_solution(self, azimuth: int, distance: int, art_elev: int, tgt_elev: int, name) -> Solution:
        print(f"New manual solution started \"{name}\"")
        return Solution.from_distance(azimuth, distance, art_elev, tgt_elev, name)

    def update_atmos(self, solution, temp, air_d, air_h):
        # TODO: Add atmospherics here
        pass

    def print_possible_charges(self, solution: Solution, ) -> None:
        """Prints a list of possible charges and ToFs for the given distance."""
        possible = []
        tofs = []
        tgt_dist = solution.calc_dist
        for i, charge in enumerate(self._rangetable, start=0):
            last = 0
            for range, d in charge.items():
                if range == tgt_dist:
                    possible.append(i)
                    tofs.append(d['tof'])
                    break
                
                if last != 0:
                    if last < tgt_dist < range:
                        possible.append(i)
                        tofs.append(d['tof'])
                        break

                last = range
        
        print("Possible charges for solution:")
        for c,t in zip(possible, tofs):
            print(f"\t{c}: ~{t}s")

    def calc_firing_solution(self, solution: Solution, preferred_charge="lowest"):
        """Calculate the firing data for supplied solution. Optionally pass
        `preferred_charge` with one of the following to change the chosen charge:
         - lowest : lowest charge available
         - highest: highest charge (good for high terrain)
         - low_tof: based on the lowest time of flight
         - high_tof: based on the highest time of flight"""
        
        if len(self._get_possible_charges(solution)) == 0:
            # No firing solutions availble
            raise FailedFiringSolutionError("No solution possible for given parameters.")

        final_elev = 0
        
        prefer_map = {
            "lowest": self._fs_lowest,
            "highest": self._fs_highest,
            "low_tof": self._fs_low_tof,
            "high_tof": self._fs_high_tof
        }

        possible = []
        tgt_dist = solution.calc_dist
        for i, charge in enumerate(self._rangetable, start=0):
            last = 0
            last_d = {}
            for range, d in charge.items():
                if range == tgt_dist:
                    possible.append([(i, range, d)])
                    break
                
                if last != 0:
                    if last < tgt_dist < range:
                        possible.append([(i, last, last_d), (i, range, d)])
                        break

                last = range
                last_d = d

        possible = prefer_map.get(preferred_charge, self._fs_lowest)(possible)
        final_charge, final_elev, final_tof = self._fire_solution(solution, possible)
        solution.solve(final_charge, final_elev, final_tof)

    def _fs_lowest(self, possible_charges):
        print("Preferring lowest charge.")
        return possible_charges[0]
    
    def _fs_highest(self, possible_charges):
        print("Preferring highest charge.")
        return possible_charges[-1]
    
    def _fs_low_tof(self, possible_charges):
        print("Preferring low time of flight.")
        lowest = 9999
        d = None
        for charge in possible_charges:
            if charge[-1][2]['tof'] < lowest:
                lowest = charge[-1][2]['tof']
                d = charge
        print(charge)
        return d
    
    def _fs_high_tof(self, possible_charges):
        print("Preferring high time of flight.")
        highest = 0
        for charge in possible_charges:
            if charge[-1][2]['tof'] > highest:
                highest = charge[-1][2]['tof']
                d = charge
        return d

    def _fire_solution(self, solution: Solution, possible_data) -> Tuple[int, int, float]:
        elev = 0
        tof = 0

        selected_range_data = possible_data  # we want to pick the lowest charge
        if len(selected_range_data) == 1:
            # We have exact solution available
            print("Exact solution available.")
            elev = selected_range_data[0][2]['elev']
            tof = selected_range_data[0][2]['tof']
        else:
            # Need to interp between 2 available ranges
            print("Interpolating from ranges.")
            
            #(lower_range_elev - higher_range_elev) / 5 * diff / 10
            
            e1 = selected_range_data[0][2]['elev']
            e2 = selected_range_data[1][2]['elev']
            t = solution.calc_dist
            r1 = selected_range_data[0][1]

            elev = e1 - ( ( (e1 - e2) / 5 ) * ((t - r1) / 10) )

            #TODO: Interp tof as well using d_tof
            tof = selected_range_data[1][2]['tof']

        d = (solution.elevation_diff / 100) * selected_range_data[0][2]['d_elev']
        if solution.artillery_elev > solution.target_elev:
            elev = elev + d
        else:
            elev = elev - d
        return selected_range_data[0][0], round(elev), tof

    def _get_possible_charges(self, solution: Solution) -> List[int]:
        possible = []
        tgt_dist = solution.calc_dist
        for i, charge in enumerate(self._rangetable, start=0):
            last = 0
            for range, d in charge.items():
                if range == tgt_dist:
                    possible.append(i)
                    break
                
                if last != 0:
                    if last < tgt_dist < range:
                        possible.append(i)
                        break
                last = range
        return possible

class Mk6Mortar_ArtilleryComputer(ArtilleryComputer):
    def __init__(self):
        super().__init__("82mm_rangetable.csv")
    