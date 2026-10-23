import base64
def lz(data):
    """LZ in _lz's format: c<128 -> literal run of c+1 bytes; c>=128 -> copy c-124 (4..131) bytes from
    distance d (2 bytes, big-endian, 4..65535) back in the output; length <= d because _lz copies o[p:p+len].
    Optimal parse (shortest encoding) by dynamic programming over match candidates."""
    n = len(data)
    index, cands = {}, [None] * n
    for i in range(n):
        best = []  # (longest match length, distance) per earlier occurrence
        if i + 4 <= n:
            for p in reversed(index.get(data[i:i + 4], [])[-256:]):
                d = i - p
                if d > 65535:
                    break
                if d < 4:
                    continue
                k = 4
                lim = min(131, d, n - i)
                while k < lim and data[p + k] == data[i + k]:
                    k += 1
                best.append((k, d))
        index.setdefault(data[i:i + 4], []).append(i)
        cands[i] = best
    INF = float("inf")
    cost = [INF] * (n + 1)
    step = [None] * (n + 1)
    cost[n] = 0
    for i in range(n - 1, -1, -1):
        # literal runs of 1..128 bytes
        for L in range(1, min(128, n - i) + 1):
            c = 1 + L + cost[i + L]
            if c < cost[i]:
                cost[i], step[i] = c, ("lit", L)
        for k, d in cands[i]:
            for L in range(4, k + 1):
                c = 3 + cost[i + L]
                if c < cost[i]:
                    cost[i], step[i] = c, ("m", L, d)
    out, i = bytearray(), 0
    while i < n:
        s = step[i]
        if s[0] == "lit":
            out.append(s[1] - 1)
            out.extend(data[i:i + s[1]])
            i += s[1]
        else:
            out.append(s[1] + 124)
            out.extend((s[2] >> 8, s[2] & 255))
            i += s[1]
    return bytes(out)


