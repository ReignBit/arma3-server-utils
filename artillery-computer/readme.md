# Artillery Computer for Ace3
A basic artillery computer to calculate a firing solution for the mortar in Ace, without using the the in-game artillery computer
Does not take into consideration wind.

Only supports the 82mm Mortar at the moment, although it should be relatively simple to add new / custom artillery pieces.

## Installation
- `pip install colorama`

## Usage
- `python arty.py`

You will need the following for it to calculate the solution:
- Target Range & Elevation
- Your elevation
- Azimuth
- Distance
- Target and your grid ref (for GridRef firing mode)

### Custom Rangetables
The only added rangetable is the 82mm_rangetable.csv, to add support for other artillery pieces simply copy paste and change the range entries
to match those for the artillery.

The software does not have support for selecting a rangetable (for now you can just replace the existing rangetable).