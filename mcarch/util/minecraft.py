import re
import itertools

def key_mc_version(a):
    """Takes a Minecraft version and returns a key for sorting it"""
    a0 = None
    # turn the the letter at the beginning of a minecraft version into a number
    # infdev/indev first
    if a[0] == 'i': a0 = 0
    elif a[0] == 'a': a0 = 1
    elif a[0] == 'b': a0 = 2
    else: a0 = 3

    # TODO: compare infdev versions
    if a0 == 0:
        return a < b
    if a0 != 3:
        # if it's an alpha or beta version, strip the first character off and then compare
        # the versions normally
        a = a[1:]

    return [a0] + [int("".join(y)) for x, y in itertools.groupby(a, key=str.isdigit) if x]

def key_mod_version(vsn):
    """Takes a mod version and returns a key for sorting it"""
    return [int(x) for x in re.split(r'\D+', vsn) if x.isdigit()]

