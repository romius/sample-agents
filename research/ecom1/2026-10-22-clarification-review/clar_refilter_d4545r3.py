# CLAR-refilter predicate prototype (clarify-boundary answer side, china-brother lane 3)
# Rule: an instruction token ELIMINATES a candidate whose display name lacks it.
# Decisive iff >=1 sibling eliminated AND exactly one candidate survives.
# Negation-containing instructions are OUT OF SCOPE (return ambiguous): fixture c1 showed
# narrow negation scope yields decisive-for-the-WRONG-candidate (1->0 flip risk), wide scope
# breaks the 'not the ak20 set' shape symmetrically. Conservative default: CLAR stands.
# Run over corpus26 needs bobcat's ../s50/catalog.json + ../s43/corpus26.json.gz (local to him).

STOP = set('the a an of for with and or pls please need code sku answer only give me set kit bundle pack accessory accessories cleaning'.split())
# ^ generic packaging/kind words (bobcat corpus26 census d~1850): 'set'/'cleaning' describe the
# KIND of product, not WHICH variant; eliminating by them flipped 3 passing CLARs to losses.
NEG = ('without', 'not', 'no', 'except', 'excluding')


def toks(instruction):
    out = []
    for w in instruction.lower().replace(',', ' ').replace('.', ' ').split():
        w = w.strip(":;'\"-()[]")
        if w and w not in STOP and len(w) > 1:
            out.append(w)
    return out


def decide(instruction, survivors, pool_complete=True):
    # pool_complete=False: the lookup's returned list is truncated (Search total_matches
    # > len(results) or the default top-8 cap was hit) -> a second qualifier-matching
    # survivor may sit beyond the prefix (aika d4696) -> never rewrite, stay ambiguous.
    if len(survivors) < 2:
        return ('single', survivors[0] if survivors else None, 0)
    if not pool_complete:
        return ('ambiguous', None, 0)
    tk = toks(instruction)
    if any(t in NEG for t in tk):
        return ('ambiguous', None, 0)
    alive = list(survivors)
    for t in tk:
        m = [nm for nm in alive if t in nm.lower()]
        if m and len(m) < len(alive):
            alive = m
    if len(alive) == 1 and len(alive) < len(survivors):
        return ('decisive', alive[0], len(survivors) - 1)
    return ('ambiguous', None, len(survivors) - len(alive))
