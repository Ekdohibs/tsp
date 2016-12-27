from __future__ import division, print_function
from math import ceil, sqrt, cos, acos

def parse_line(l):
    if ":" not in l:
        return (l.strip(), "")
    w = l.index(":")
    prefix = l[:w]
    dat = l[w+1:]
    return (prefix.strip(), dat.strip())

def euc(x, y):
    return sum((u-v)**2 for u,v in zip(x,y))**0.5

def read_n_ints(f, n):
    l = []
    for line in f:
        l += list(map(int, line.split()))
        if len(l) >= n:
            assert (len(l) == n)
            return l

def parse_file(f):
    for line in f:
        pref, dat = parse_line(line)
        if pref == "": continue
        elif pref == "NAME": continue
        elif pref == "COMMENT": continue
        elif pref == "TYPE": assert (dat.split()[0] == "TSP")
        elif pref == "DIMENSION": nodes = [None] * int(dat)
        elif pref == "EDGE_WEIGHT_TYPE": ewt = dat
        elif pref == "EDGE_WEIGHT_FORMAT": ewf = dat
        elif pref == "DISPLAY_DATA_TYPE": continue
        elif pref == "EOF": break
        elif pref == "FIXED_EDGES_SECTION": raise ValueError
        elif pref == "NODE_COORD_TYPE": continue
        elif pref == "NODE_COORD_SECTION":
            for _, lline in zip(range(len(nodes)), f):
                w = lline.split()
                nodes[int(w[0]) - 1] = list(map(float, w[1:]))
        elif pref == "EDGE_WEIGHT_SECTION":
            if ewf == "UPPER_ROW":
                data = read_n_ints(f, (len(nodes) * (len(nodes) - 1)) // 2)
                k = 0
                for i in range(len(nodes) - 1):
                    nodes[i] = data[k:k+len(nodes)-i-1]
                    k += len(nodes)-i-1
            elif ewf == "UPPER_DIAG_ROW":
                data = read_n_ints(f, (len(nodes) * (len(nodes) + 1)) // 2)
                k = 0
                for i in range(len(nodes)):
                    nodes[i] = data[k:k+len(nodes)-i]
                    k += len(nodes)-i
            elif ewf == "LOWER_DIAG_ROW":
                data = read_n_ints(f, (len(nodes) * (len(nodes) + 1)) // 2)
                k = 0
                for i in range(len(nodes)):
                    nodes[i] = data[k:k+i+1]
                    k += i + 1
            elif ewf == "FULL_MATRIX":
                data = read_n_ints(f, len(nodes)**2)
                for i in range(len(nodes)):
                    nodes[i] = data[len(nodes)*i:len(nodes)*(i+1)]
            else:
                print(ewf)
                assert False
        elif pref == "DISPLAY_DATA_SECTION":
            for _, lline in zip(range(len(nodes)), f):
                continue
        else:
            print(pref)
            assert False
    # Failsafe
    if len(nodes) > 5000:
        raise ValueError
    if ewt == "EUC_2D":
        return [[int(euc(nodes[i], nodes[j])+0.5) for i in range(len(nodes))] for j in range(len(nodes))]
    elif ewt == "CEIL_2D":
        return [[int(ceil(euc(nodes[i], nodes[j]))) for i in range(len(nodes))] for j in range(len(nodes))]
    elif ewt == "ATT":
        return [[int(ceil(euc(nodes[i], nodes[j])/sqrt(10))) for i in range(len(nodes))] for j in range(len(nodes))]
    elif ewt == "GEO":
        PI = 3.141592
        def ll(u):
            deg = int(u[0])
            min = u[0]-deg
            lat = PI * (deg + 5.0 * min / 3.0 ) / 180.0
            deg = int(u[1])
            min = u[1]-deg
            long = PI * (deg + 5.0 * min / 3.0 ) / 180.0
            return (lat, long)
        def ddd(u,v):
            if u == v: return 0
            RRR = 6378.388
            q1 = cos(u[1]-v[1])
            q2 = cos(u[0]-v[0])
            q3 = cos(u[0]+v[0])
            return int(RRR * acos(0.5*((1.0+q1)*q2 - (1.0-q1)*q3)) + 1.0)
        return [[ddd(ll(nodes[i]),ll(nodes[j])) for i in range(len(nodes))] for j in range(len(nodes))]
    elif ewt == "EXPLICIT" and ewf == "UPPER_ROW":
        return [[0 if i == j else nodes[min(i,j)][max(i,j)-min(i,j)-1] for i in range(len(nodes))] for j in range(len(nodes))]
    elif ewt == "EXPLICIT" and ewf == "LOWER_DIAG_ROW":
        return [[nodes[max(i,j)][min(i,j)] for i in range(len(nodes))] for j in range(len(nodes))]
    elif ewt == "EXPLICIT" and ewf == "UPPER_DIAG_ROW":
        return [[nodes[min(i,j)][max(i,j)-min(i,j)] for i in range(len(nodes))] for j in range(len(nodes))]
    elif ewt == "EXPLICIT" and ewf == "FULL_MATRIX":
        return nodes
    else:
        print(ewt)
        assert False

if __name__ == '__main__':
    import os
    for name in os.listdir("TSPLIB"):
        if not name.endswith(".tsp"): continue
        with open("TSPLIB/" + name, "r") as f:
            print(name, end = " ")
            try:
                mat = parse_file(f)
                for i in range(len(mat)):
                    assert (mat[i][i] == 0)
                    for j in range(i + 1, len(mat)):
                        assert (mat[i][j] == mat[j][i])
                print("ok")
            except ValueError:
                print("skipped")
        
