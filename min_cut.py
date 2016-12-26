
def stoer_wagner(adj):
    """
       Takes adjacency matrix, and returns min cut and its weight.
       Running time: O(|V|^3)
    """
    adj0 = adj
    adj = [list(l) for l in adj]
    n = len(adj)
    take = [False] * n
    rep = [i for i in range(n)]
    best_cut = None
    best_cut_weight = float('inf')
    for phase in range(n-1,-1,-1):
        assert(n-sum(take)==phase+1)
        #print([[adj[i][j] for i in range(n) if not take[i]] for j in range(n) if not take[j]])
        dst = list(adj[0])
        seen = list(take)
        best = 0
        for i in range(phase):
            #print(dst)
            last = best
            best = max((j for j in range(1, n) if not seen[j]),
                       key = lambda j: dst[j])
            assert (best != 0)
            #print(best,last,seen)
            #assert (all(dst[j] == adj[0][j] + sum(adj[j][k] for k in range(1,n) if seen[k] and not take[k]) for j in range(1,n) if not seen[j]))
            if i < phase - 1:
                for j in range(1, n):
                    dst[j] += adj[best][j]
                seen[best] = True
            else:
                #cut.append(best)
                if dst[best] < best_cut_weight:
                    best_cut_weight = dst[best]
                    #best_cut = list(cut)
                    best_cut = [j for j in range(n) if rep[j] == best]
                # Fusion of best and last
                #print("Merge", best, last)
                for j in range(n):
                    adj[last][j] = adj[j][last] = adj[last][j] + adj[best][j]
                    if rep[j] == best: rep[j] = last
                take[best] = True
    return best_cut_weight, best_cut

def stoer_wagner_nx(graph, weight = 'weight', heap = None):
    nodes = graph.nodes()
    d = {}
    for i in range(len(nodes)):
        d[nodes[i]] = i
    mat = [[0] * len(nodes) for i in range(len(nodes))]
    #d = {'b': 0, 'y': 1, 'x': 2, 'c': 3, 'e': 4, 'd': 5, 'a': 6}
    #nodes = 'byxceda'
    for u, v, r in graph.edges_iter(data = True):
        mat[d[u]][d[v]] = mat[d[v]][d[u]] = r.get(weight, 1)
    #print(d)
    w, c = stoer_wagner(mat)
    z = [False] * len(nodes)
    for u in c: z[u] = True
    return w, ([nodes[u] for u in c], [nodes[u] for u in range(len(nodes)) if not z[u]])

if __name__ == '__main__':
    import networkx as nx
    for _ in range(100):
        """G = nx.Graph()
        G.add_edge('x','a', weight=3)
        G.add_edge('x','b', weight=1)
        G.add_edge('a','c', weight=3)
        G.add_edge('b','c', weight=5)
        G.add_edge('b','d', weight=4)
        G.add_edge('d','e', weight=2)
        G.add_edge('c','y', weight=2)
        G.add_edge('e','y', weight=3)
        w, c = stoer_wagner_nx(G)
        print(w,c)
        assert (w == 4)"""
        G = nx.barabasi_albert_graph(100,5)
        w, _ = nx.stoer_wagner(G)
        w2, c = stoer_wagner_nx(G)
        k = 0
        for u in c[0]:
            for v in c[1]:
                if G.has_edge(u,v):
                    k += 1
        assert (k == w2)
        assert(w == w2)
        print("ok")
