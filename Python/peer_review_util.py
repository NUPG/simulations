# invert a dictionary of lists (assuming no duplicates)
def invert_dictlist(d):
    return dict( (v,k) for k in d for v in d[k] )

# invert a dictionary of lists (with duplicates)
def invert_dictlist_dup(d):
    values = set(a for b in d.values() for a in b)
    reverse_d = dict((new_key, [key for key,value in d.items() if new_key in value]) for new_key in values)
    return reverse_d
