from parser import parse_file
from separation import separation

name = "burma14.tsp" #3001
#name = "gr17.tsp" #1684
#name = "gr21.tsp" #2707
#name = "eil51.tsp" #416.5
#name = "gr24.tsp" #1224.5
#name = "st70.tsp" #623.5
#name = "gr48.tsp" #4769
#name = "pr76.tsp" #98994.5

with open("TSPLIB/" + name, "r") as f:
    Adj = parse_file(f)
    x, ival = separation(Adj)
    #print(x)
    print(ival)
    
    #for l in Adj:
    #    for c in l:
    #        print(c, end=' ')
    #    print(' ')
