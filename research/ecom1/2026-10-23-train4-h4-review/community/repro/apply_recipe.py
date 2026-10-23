def apply(source, recipe):
    for edit in recipe["edits"]:
        old = edit["old"]
        new = edit["new"]
        count = edit["count"]
        found = source.count(old)
        if found != count:
            raise ValueError("edit occurrence mismatch: expected %d, found %d" % (count, found))
        source = source.replace(old, new)
    return source
