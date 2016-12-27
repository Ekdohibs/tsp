import networkx as nx
import scipy as sc
import numpy as np


def numEdge(d, a):
    return min(d, a)*nbN + max(d, a)

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
        c.append(G[ e[0] ][ e[1] ]['weight'])
        extToEdge[ e[0] ][ e[1] ] = len(c) - 1
        extToEdge[ e[1] ][ e[0] ] = len(c) - 1

    return c, extToEdge

def subG(G, x, extToEdge):
    nbN = len(G.nodes())
    subG = nx.Graph()
    for (d, a) in G.edges():
        subG.add_edge(d, a, weight = G[d][a]['weight'] * x[ extToEdge[d][a] ])
    
    return subG

def addSubTour(A_ub, b_ub, G, part, extToEdge):
    nbN = len(G.nodes())
    
    newCstr = [0]*len(G.edges())

    for d in part:
        for a in range(nbN):
            if(a <> d and (a not in part)):
                newCstr[ extToEdge[d][a] ] = 1

    return A_ub.append(newCstr), b_ub.append(2)

def separation(Adj):
    G = initGraph(Adj)
    nbN, nbE = len(G.nodes()), len(G.edges())
    
    c, extToEdge = initObj(G)
    A_eq = np.ones((nbN, nbE))
    b_eq = np.ones((nbN, 1))
   
    #mettre des 0 sur les arêtes (noeud, noeud)...

    A_ub = []
    b_ub = []
    res = sc.optimize.linprog(c, A_eq = A_eq, b_eq = b_eq, bounds=((0, 1)))
    x = res.x

    while(True):
        sG = subG(G, x, extToEdge)
        cutV, part = nx.stoer_wagner(sG)
        if(cutV >= 2):
            break
        A_ub, b_ub = addSubTour(A_ub, b_ub, G, part[0], extToEdge)
        
        res = sc.optimize.linprog(c, A_eq = A_eq, b_eq = b_eq, A_ub = A_ub, b_ub = b_ub, bounds=((0, 1)))
        x = res.x

    return x, res.fun
