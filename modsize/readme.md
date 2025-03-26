# modsize
Collects the workshop file size for each mod in an Arma3 preset html file.

> This sums the file size as shown on the workshop page, thus this script is only really used
as a reference before downloading.

## Installation (Windows)
- optional: Create venv `python -m venv .venv`
    - optional-windows: Activate venv `.\.venv\Scripts\activate`
    - optional-linux: `./.venv/bin/activate`
- Install requirements: `pip install -r requirements.txt`

## Usage
`python modsize.py '<ARMA 3 PRESET FILEPATH>'`

Example:
`python modsize.py 'Arma3PresetExample.html`