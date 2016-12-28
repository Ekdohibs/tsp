from parser import parse_file
from separation import separation
from separation_dual import LinearDualTSP

#name = "burma14.tsp" #3001
#name = "gr17.tsp" #1684
#name = "gr21.tsp" #2707
#name = "eil51.tsp" #416.5, 7s
#name = "gr24.tsp" #1224.5
#name = "st70.tsp" #623.5, 31s
#name = "gr48.tsp" #4769
#name = "pr76.tsp" #98994.5
#name = "dantzig42.tsp"
name = "brazil58.tsp"
#name = "bayg29.tsp"
#name = "bays29.tsp"
#name = "berlin52.tsp"
#name = "ulysses22.tsp"

with open("TSPLIB/" + name, "r") as f:
    Adj = parse_file(f)
    #x, ival = separation(Adj)
    x, ival = LinearDualTSP(Adj).solve()
    #print(x)
    print(ival)
    #print(list(x))
    
    #for l in Adj:
    #    for c in l:
    #        print(c, end=' ')
    #    print(' ')
