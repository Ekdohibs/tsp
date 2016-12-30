import networkx as nx

def nearN(G):
    vCur = 0
    seen = set([0])
    tour = nx.Graph()

    for i in range(len(G.nodes()) - 1):
        nxt, w = 0, 1e9 
        for nei in range(len(G.nodes())):
            if (nei not in seen and G[vCur][nei]['weight'] < w):
                nxt, w = nei, G[vCur][nei]['weight']
        seen.add(nxt)
        tour.add_edge(vCur, nxt, weight=w)
        vCur = nxt
        
    tour.add_edge(vCur, 0, weight=G[vCur][0]['weight'])

    size = 0
    for (d, a) in tour.edges():
        size += tour[d][a]['weight']
    return size, tour
