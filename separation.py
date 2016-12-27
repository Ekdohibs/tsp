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

    return A_ub.append(newCstr), b_ub.append(-2)

def separation(Adj):
    G = initGraph(Adj)
    
    c, extToEdge = initObj(G)
    
    A_eq, b_eq = initCstr(G, extToEdge)
   
    A_ub = []
    b_ub = []
    res = linprog(c, A_eq = A_eq, b_eq = b_eq, bounds=((0, 1)))
    x = res.x
    print(x) 
    n = 100
    while(n < 100):
        sG = subG(G, x, extToEdge)
        cutV, cut = stoer_wagner_nx(sG)
        print(cutV, cut)
        if(cutV >= 2):
            break
        A_ub, b_ub = addSubTour(A_ub, b_ub, G, cut, extToEdge)
        
        res = linprog(c, A_eq = A_eq, b_eq = b_eq, A_ub = A_ub, b_ub = b_ub, bounds=((0, 1)))
        x = res.x
        
        n += 1


    return x, res.fun
