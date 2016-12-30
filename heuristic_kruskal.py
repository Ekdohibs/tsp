import networkx as nx
import matplotlib.pyplot as plt

def kruskal(G):
    root = [i for i in range(len(G.nodes()))]
    sizeComponent = [1 for i in range(len(G.nodes()))]
    
    spanningTree = nx.Graph()

    def findRoot(nd):
        if root[nd] == nd:
            return nd
        root[nd] = findRoot(root[nd])
        return root[nd]

    def merge(comp1, comp2):
        if sizeComponent[comp1] < sizeComponent[comp2]:
            root[comp1] = comp2
            sizeComponent[comp2] += sizeComponent[comp1]
        else:
            root[comp2] = comp1
            sizeComponent[comp1] += sizeComponent[comp2]

    for a, b, w in sorted(G.edges(data=True), key=lambda u: u[2]['weight']):
        if findRoot(a) != findRoot(b):
            merge(root[a], root[b])
            spanningTree.add_edge(a, b, w)

    return spanningTree, findRoot(0)

def heuristic(G):
    spG, root = kruskal(G)
    tour = nx.Graph()

    def walk(nd, anc):
        nonlocal tour, G
        #print('w', nd, len(spG[nd]), anc)

        if(nd != root and len(spG[nd]) == 1): #only ancestor
            return nd
        
        iInit = 0
        if(spG.neighbors(nd)[0] == anc):
            iInit += 1
        
        nxt = spG.neighbors(nd)[iInit]
        tour.add_edge(nd, nxt, weight = G[nd][nxt]['weight'])
        
        leaf = walk(nxt, nd)

        for iNxt in range(iInit+1, len(spG.neighbors(nd))):
            nxt = spG.neighbors(nd)[iNxt]
            if(nxt != anc):
                #arc de remonté :
                tour.add_edge(leaf, nxt, weight = G[leaf][nxt]['weight'])
                #on redescend dans l'arbre
                leaf = walk(nxt, nd)

        return leaf

    leaf = walk(root, -1)
    tour.add_edge(root, leaf, weight = G[leaf][root]['weight'])

    size = 0
    for d, a in tour.edges():
        size += tour[d][a]['weight']
    #print('taille tour :', len(tour.edges()))
    #nx.draw(tour)
    #plt.show()
    #print('size :', size)
    return size, tour

