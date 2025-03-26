"""
    modsize.py

    Get the total file size of an Arma3 mod preset.

    This only shows the file size as indicated on the Steam Workshop page, and does not take into
    account download size.

    How to launch:
        python modsize.py <arma3modpresetfile.html>

    Returns:
        List of parsed urls and their file size,
        final total of all mods in the preset.
"""

from bs4 import BeautifulSoup
import sys
import requests
from lxml import html

def parse_mod_html(filename):
    """
        Parse Mod HTML file to extract workshop ids.
        Returns:
            ParseResult: (id,name) workshop ids of mods in the preset.
    """
    bs: BeautifulSoup = None
    try:
        with open(filename, 'r') as f:
            d = f.read()
            bs = BeautifulSoup(d, 'html.parser')

    except (IOError, FileNotFoundError) as e:
        print(f"Error\tFailed to read mod preset file ({filename})\nReason: {e}")
        exit(10)

    mods = []
    found_non_steam_mod = 0
    for row in bs.find_all("tr", {'data-type': 'ModContainer'}):
        name = row.find_next("td", {'data-type': 'DisplayName'}).text
        url = row.find_next("a").text
        id = int(url.split("?id=")[-1])
        steam = bool(row.find("span", {'class': 'from-steam'}))
        if steam:
            print(f"Found\t{id}\t\t{name}")
            mods.append(url)
        else:
            print(f"Found\t{id}\t\t{name}")
            print("Not a steam workshop mod! Unable to move automatically.")
            found_non_steam_mod += 1
    return (mods, found_non_steam_mod)


def get_download_size(url):
    r = requests.get(url)
    tree = html.fromstring(r.text)

    size = tree.xpath("//div[@class='detailsStatsContainerRight']//div[@class='detailsStatRight']/text()")
    parsed = float(size[0].split(" ")[0])
    if "GB" in size[0]:
        parsed = parsed * 1024
    elif "KB" in size[0]:
        parsed = parsed / 1024

    print(url, parsed)
    return (size[0], parsed)


if len(sys.argv) < 1:
    print("Missing modpreset.html path!")
    exit(1)

mods = parse_mod_html(sys.argv[1]) 
total = 0
for mod in mods[0]:
    _, a = get_download_size(mod)
    total = total + a
print("===== TOTAL MOD PRESET SIZE =====")
print(f"{total:.2f} MB ({(total / 1024):.2f} GB)")


