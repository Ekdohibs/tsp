import networkx as nx
import scipy as sc
import numpy as np

def initGraph(Adj):
    G = nx.Graph()
    
    for l in range(Adj):
        for c in range(Adj[l]):
            G.add_edge(l, c, weight = Adj[l][c])
    
    return G

def subG(G, x):
    nbN = len(G.nodes())
    subG = nx.Graph()
    for (d, a) in G.edges():
        subG.add_edge(d, a, weight = G[d][a]['weight'] * x[min(d, a)*nbN+max(d,a)])
    
    return subG

def addSubTour(A_ub, b_ub, G, part):
    nbN = len(G.nodes())
    
    newCstr = [0]*len(G.edges())

    for d in part:
        for a in range(nbN):
            if(a not in part):
                newCstr[min(d, a)*nbN + max(d, a)] = 1

    return A_ub.append(newCstr), b_ub.append(2)

def separation(Adj):
    G = initGraph(Adj)
    nbN, nbE = len(Adj), len(Adj)*(len(Adj)-1)/2
    
    c = Adj.reshape(nbE)
    A_eq = np.ones((nbN, nbE))
    b_eq = np.ones((nbN, 1))
    
    A_ub = []
    b_ub = []
    res = sc.optimize.linprog(c, A_eq = A_eq, b_eq = b_eq, bounds=((0, 1)))
    x = res.x

    while(True):
        sG = subG(G, x)
        cutV, part = nx.stoer_wagner(sG)
        if(cutV >= 2):
            break
        A_ub, b_ub = addSubTour(A_ub, b_ub, G, part[0])
        
        res = sc.optimize.linprog(c, A_eq = A_eq, b_eq = b_eq, A_ub = A_ub, b_ub = b_ub, bounds=((0, 1)))
        x = res.x

    return x, res.fun
