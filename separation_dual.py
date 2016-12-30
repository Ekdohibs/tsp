import networkx as nx
from scipy.optimize import linprog
import numpy as np
from min_cut import stoer_wagner_nx

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

def subG(G, x, extToEdge):
    nbN = len(G.nodes())
    subG = nx.Graph()
    for (d, a) in G.edges():
        if (d,a) in extToEdge:
            if(x[ extToEdge[(d, a)] ] != 0):
                subG.add_edge(d, a, weight = x[ extToEdge[(d, a)] ])
    
    return subG

class LinearDualTSP(object):
    def __init__(self, Adj):
        self.G = nx.Graph()
        for l in range(len(Adj)):
            for c in range(l):
                self.G.add_edge(l, c, weight = Adj[l][c])

        self.n = len(Adj)
        self.edge_mapping = {}
        self.cuts = []
        self.primal_obj = []
        self.primal_eqs = [[] for _ in range(self.n)]
        self.primal_ineqs = []
        self.dual_obj = [-2] * self.n
        self.dual_ineqs = []
        self.dual_ineqs_b = []

        # TODO: init with good heuristic
        for i in range(self.n):
            self.add_edge((i, (i + 1) % self.n))

    def solve_primal(self):
        #print(len(self.primal_eqs), self.n, [len(x) for x in self.primal_eqs])
        #print(len(self.primal_ineqs), [len(x) for x in self.primal_ineqs])
        #print(len(self.primal_obj))
        res = linprog(self.primal_obj,
                      A_eq = self.primal_eqs,
                      b_eq = [2] * self.n,
                      A_ub = self.primal_ineqs if len(self.primal_ineqs) > 0 else None,
                      b_ub = [-2] * len(self.primal_ineqs) if len(self.primal_ineqs) > 0 else None,
                      bounds=((0, 1)))
        if res.status != 0:
            print(res)
        return res.x, res.fun

    def solve_dual(self):
        e = len(self.primal_obj)
        #print(self.dual_obj)
        #print(self.dual_ineqs)
        #print(self.dual_ineqs_b)
        #print(len(self.dual_obj))
        #print([len(x) for x in self.dual_ineqs])
        #print(self.n + len(self.cuts))
        res = linprog(self.dual_obj + [1] * e,
                      A_ub = [self.dual_ineqs[i] + [-1 if i == j else 0 for j in range(e)] for i in range(e)],
                      b_ub = self.dual_ineqs_b,
                      bounds = ((None,None),) * self.n + ((0,None),) * (e + len(self.cuts)))
        return res.x[:self.n], res.x[self.n:self.n+len(self.cuts)], res.x[self.n+len(self.cuts):], -res.fun

    def add_edge(self, edge):
        assert (edge not in self.edge_mapping)
        k = len(self.primal_obj)
        self.edge_mapping[edge] = self.edge_mapping[(edge[1],edge[0])] = k
        self.primal_obj.append(self.G[edge[0]][edge[1]]['weight'])
        for i in range(self.n):
            self.primal_eqs[i].append(1 if i in edge else 0)
        for i in range(len(self.cuts)):
            if (edge[0] in self.cuts[i][0]) != (edge[1] in self.cuts[i][0]):
                self.primal_ineqs[i].append(-1)
            else:
                self.primal_ineqs[i].append(0)
        self.dual_ineqs_b.append(self.G[edge[0]][edge[1]]['weight'])
        ll = [0] * (self.n + len(self.cuts))
        ll[edge[0]] = 1
        ll[edge[1]] = 1
        for i in range(len(self.cuts)):
            if (edge[0] in self.cuts[i][0]) != (edge[1] in self.cuts[i][0]):
                ll[i + self.n] = 1
        self.dual_ineqs.append(ll)

    def add_cut(self, cut):
        cut = (set(cut[0]), set(cut[1]))
        self.cuts.append(cut)
        self.dual_obj.append(-2)
        for e, i in self.edge_mapping.items():
            if e[1] > e[0]: continue
            if (e[0] in cut[0]) != (e[1] in cut[0]):
                self.dual_ineqs[i].append(1)
            else:
                self.dual_ineqs[i].append(0)
        ll = [0] * len(self.primal_obj)
        for e, i in self.edge_mapping.items():
            if (e[0] in cut[0]) != (e[1] in cut[0]):
                ll[i] = -1
        self.primal_ineqs.append(ll)

    def solve_old(self):
        x, fun = self.solve_primal()
        while True:
            while True:
                #print(x, self.edge_mapping)
                sG = subG(self.G, x, self.edge_mapping)
                ccs = connected_components(sG)
                print(ccs)
                if len(ccs) > 1:
                    if len(ccs) == 2:
                        self.add_cut((ccs[0], ccs[1]))
                    else:
                        for i in range(len(ccs)):
                            self.add_cut((ccs[i], sum([ccs[j] for j in range(len(ccs)) if i != j], [])))
                else:
                    cutV, cut = stoer_wagner_nx(sG)
                    print(cutV, cut)
                    if(cutV >= 2):
                        break
                    self.add_cut(cut)
                
                x, fun = self.solve_primal()

            eqs, cts, beta, dual_fun = self.solve_dual()
            print(fun, dual_fun)
            #print(eqs, cts, beta)
            l = []
            for i in range(self.n):
                for j in range(i):
                    if (i, j) in self.edge_mapping: continue
                    s = eqs[i] + eqs[j]
                    for r in range(len(self.cuts)):
                        if (i in self.cuts[r][0]) != (j in self.cuts[r][0]):
                            s += cts[r]
                    if s > self.G[i][j]['weight']:
                        l.append((i, j))
            print(len(l))
            if len(l) == 0:
                break
            for e in l:
                self.add_edge(e)
            x, fun = self.solve_primal()

        return x, fun

    def solve(self):
        n = 0
        while n < 10:
            while True:
                eqs, cts, beta, dual_fun = self.solve_dual()
                print(dual_fun)
                #print(eqs, cts, beta)
                l = []
                for i in range(self.n):
                    for j in range(i):
                        if (i, j) in self.edge_mapping: continue
                        s = eqs[i] + eqs[j]
                        for r in range(len(self.cuts)):
                            if (i in self.cuts[r][0]) != (j in self.cuts[r][0]):
                                s += cts[r]
                        if s > self.G[i][j]['weight']:
                            l.append((i, j))
                print(len(l), len(self.primal_obj))
                if len(l) == 0:
                    break
                for e in l:
                    self.add_edge(e)
            
            x, fun = self.solve_primal()
            sG = subG(self.G, x, self.edge_mapping)
            ccs = connected_components(sG)
            print(ccs)
            if len(ccs) > 1:
                if len(ccs) == 2:
                    self.add_cut((ccs[0], ccs[1]))
                else:
                    for i in range(len(ccs)):
                        self.add_cut((ccs[i], sum([ccs[j] for j in range(len(ccs)) if i != j], [])))
            else:
                cutV, cut = stoer_wagner_nx(sG)
                print(cutV, cut)
                if(cutV >= 2-eps):
                    break
                self.add_cut(cut)
            n += 1

        return x, fun

