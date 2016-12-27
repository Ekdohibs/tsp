
def memoize(f):
    d = {}
    def wrap(*a):
        if a in d: return d[a]
        r = f(*a)
        d[a] = r
        return r
    return wrap

def solve_exact(adj):
    n = len(adj)
    r = (1 << n) - 1
    @memoize
    def sv(seen, x):
        if seen == r: return adj[0][x]
        return min(sv(seen | (1 << j), j) + adj[x][j] for j in range(1, n) if seen & (1 << j) == 0)
    return sv(1, 0)

if __name__ == '__main__':
    from parser import parse_file
    for data, result in [("burma14", 3323), ("gr17", 2085), ("gr21", 2707)]:
        with open("TSPLIB/" + data + ".tsp", "r") as f:
            adj = parse_file(f)
        assert (solve_exact(adj) == result)
        print("ok")

