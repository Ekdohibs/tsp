import networkx as nx
from scipy.optimize import linprog
import numpy as np
from min_cut import stoer_wagner_nx

def initGraph(Adj):
    G = nx.Graph()
    
    for l in range(len(Adj)):
        for c in range(l):
            G.add_edge(l, c, weight = Adj[l][c])
    return G

def initObj(G):
    c = []
    extToEdge = {}
    for e in G.edges():
        extToEdge[ (e[0], e[1]) ] = len(c)
        extToEdge[ (e[1], e[0]) ] = len(c)
        c.append(G[ e[0] ][ e[1] ]['weight'])

    return c, extToEdge

def initCstr(G, extToEdge):
    nbN, nbE = len(G.nodes()), len(G.edges())
    b_eq = 2*np.ones((nbN, 1))
    A_eq = np.zeros((nbN, nbE))

    for nd in G.nodes():
        for nei in G[nd]:
            A_eq[nd][ extToEdge[(nd, nei)] ] = 1

    return A_eq, b_eq

def subG(G, x, extToEdge):
    nbN = len(G.nodes())
    subG = nx.Graph()
    for (d, a) in G.edges():
        if(x[ extToEdge[(d, a)] ] != 0):
            subG.add_edge(d, a, weight = G[d][a]['weight'] * x[ extToEdge[(d, a)] ])
    
    return subG

def addSubTour(A_ub, b_ub, G, cut, extToEdge):
    nbN = len(G.nodes())
    
    newCstr = [0]*len(G.edges())
     
    for d in cut[0]:
        for a in cut[1]:
            newCstr[ extToEdge[(d, a)] ] = -1

    A_ub.append(newCstr)
    b_ub.append(-2)

eps = 1e-9
def connected_components(G):
    nodes = G.nodes()
    d = {}
    for i in range(len(nodes)):
        d[nodes[i]] = i
    mat = [[0] * len(nodes) for i in range(len(nodes))]
    for u, v, r in G.edges_iter(data = True):
        mat[d[u]][d[v]] = mat[d[v]][d[u]] = r['weight']
    ccs = []
    seen = [False] * len(nodes)
    for i in range(len(nodes)):
        if seen[i]: continue
        seen[i] = True
        stack = [i]
        cc = [i]
        while len(stack) > 0:
            r = stack.pop()
            for j in range(len(nodes)):
                if mat[r][j] > eps and not seen[j]:
                    seen[j] = True
                    stack.append(j)
                    cc.append(j)
        ccs.append(cc)
    return [[nodes[u] for u in cc] for cc in ccs]

def separation(Adj):
    G = initGraph(Adj)
    
    c, extToEdge = initObj(G)
    
    A_eq, b_eq = initCstr(G, extToEdge)
   
    A_ub = []
    b_ub = []
    res = linprog(c, A_eq = A_eq, b_eq = b_eq, bounds=((0, 1)))
    x = res.x
    print(x) 
    n = 0
    while(n < 100):
        sG = subG(G, x, extToEdge)
        ccs = connected_components(sG)
        print(ccs)
        if len(ccs) > 1:
            if len(ccs) == 2:
                addSubTour(A_ub, b_ub, G, (ccs[0], ccs[1]), extToEdge)
            else:
                for i in range(len(ccs)):
                    addSubTour(A_ub, b_ub, G, (ccs[i], sum([ccs[j] for j in range(len(ccs)) if i != j], [])), extToEdge)
        else:
            cutV, cut = stoer_wagner_nx(sG)
            print(cutV, cut)
            if(cutV >= 2):
                break
            addSubTour(A_ub, b_ub, G, cut, extToEdge)
        
        res = linprog(c, A_eq = A_eq, b_eq = b_eq, A_ub = A_ub, b_ub = b_ub, bounds=((0, 1)))
        x = res.x
        
        n += 1


    return x, res.fun
