import requests
import time
from bs4 import BeautifulSoup

def showProgress(i, length, size=50):
    """Will print an updating progress bar as i goes from 0 to length"""
    n = "\n"
    r = "\r"
    string1 = (int(size*i/length)*"#")+(int(size*(length-i)/length)*'_') 
    string2 = "%.1f" % (100*i/length)
    print(f"[{string1}]  {string2}% Completed", end=f"{n if i == length else r}")

def get_list(url, paths):
    """Extracts a list of items from url making use of an array of paths to the given items.
    Paths is a list of lists of css selectors, i.e [[div#id.className1.className2, p]]"""
    doc = requests.get(url).text
    soup = BeautifulSoup(doc, "html.parser")
    names = []
    for path in paths:
        enclosing = path[0]
        arr = soup.select(enclosing)
        del path[0]
        while len(path):
                arr = [a.select(path[0])[0] for a in arr]
                del path[0]
        n = [a.text.strip() for a in arr]
        names.extend(n)
    return names

def list_representation(l):
    """Returns a string representation of a list, without oxford comma.
    [a,b,c,d] => 'a, b, c and d' """
    if not len(l):
        return l
    elif len(l) == 1:
        return l[0]
    else:
        return f"{', '.join(l[0:-1])} and {l[-1]}"   

def rmChar(s, char):
    """Removes instances of char from s"""
    return "".join(s.split(char))

def rmKeys(d,keys):
    """Removes each key in keys from dict d, convert value to int"""
    return {k:int(d[k]) for k in d if k not in keys}
def rmKeysF(d,keys):
    """Removes each key in keys from dict d, convert value to float"""
    newD = {}
    for k,v in d.items():
        if k not in keys: 
            try:
                newV = int(v)
            except:
                newV = float(v)
            newD[k] = newV
    return newD
def setParams(URL, params):
    """Adds each parameter in params to the URL"""
    if "?" in URL:
        base,ps = URL.split("?")
        ps = ps.split("&")
        toBeAdded = dict([p.split("=") for p in ps])
        for k in params:
            toBeAdded[k] = params[k]
        base += "?"
        for k in toBeAdded:
            base += f"{k}={toBeAdded[k]}&"
    else:
        base += "?"
        for k in params:
            base += f"{k}={params[k]}&"
    base = base[:-1]
    return base
def numToPos(i):
    """Returns i as a string representation"""
    return ["0th", "1st", "2nd", "3rd", *[f"{i}th" for i in range(4,15)]][i]
        