import argparse
import math
import sys

import networkx as nx

from pycliques.coaffinations import coaffinations, CoaffinePair,\
    is_coaffine_map
from pycliques.clockwork import clockwork_graph
from pycliques.cliques import clique_graph as k
from pycliques.utilities import invert_dict


def read_adj_list(the_list):
    """Converts adjacency list given by GAP genreg to networkx graph."""
    n = len(the_list)
    the_graph = nx.Graph()
    for i in range(n):
        for j in the_list[i]:
            the_graph.add_edge(i, j-1)
    return the_graph


def graphs_from_file(f):
    """Reads a list of graphs created with PrintTo"""
    with open(f) as adj:
        v = adj.read()
    v = v.replace('\n', '')
    graphs = eval(v)
    graphs = [read_adj_list(g) for g in graphs]
    return graphs


allcovers = graphs_from_file("adjsall.txt")
cw = clockwork_graph([1]*6, [[0]]*6, 2, [0, 1])
cwp = CoaffinePair(cw, list(coaffinations(cw, 4))[0])
solved = []
uncertain = []
no_coaf_mono = []


def main():
    parser = argparse.ArgumentParser('coaffine-morphs')
    parser.add_argument('-i', '--i_index', help='Initial Index',
                        dest='initial', default=0, type=int)
    parser.add_argument('-e', '--e_index', help='Final Index',
                        dest='final', default=362, type=int)
    parser.add_argument('-t', '--iterated', help='Which iterated graph',
                        dest='iterated', default=0, type=int)
    parser.add_argument('-b', '--bound', help='How many monomorphisms to try',
                        dest='bound_monos', default=math.inf, type=int)
    parser.add_argument('-x', '--exclude', help='Indices to exclude',
                        dest='exclude', default='')
    args = parser.parse_args()
    if args.exclude:
        exclude = [int(item) for item in args.exclude.split(',')]
    else:
        exclude = []
    filelog = ''.join(st for st in sys.argv) + '.org'
    for j in range(args.initial, args.final):
        if j not in exclude:
            print(f"Trying graph {j}")
            g = allcovers[j]
            gp = CoaffinePair(g, list(coaffinations(g, 4))[0])
            for u in range(int(args.iterated)):
                gp = k(gp)
            GM = nx.isomorphism.GraphMatcher(gp.graph, cw)
            the_iter = GM.subgraph_monomorphisms_iter()
            for i, mono in enumerate(the_iter):
                if i > args.bound_monos:
                    print(f"Tried {args.bound_monos} monomorphisms, graph {j}")
                    uncertain.append(j)
                    with open(filelog, 'a') as f:
                        f.write(f"* graph {j}, after {args.bound_monos}")
                        f.write(" attempts\n\n")
                        f.write("No coaffine monomorphisms found!\n\n")
                    break
                print(f"graph {j}, mono {i}", end='\r', flush=True)
                mono = invert_dict(mono)
                if is_coaffine_map(cwp, gp, mono) is True:
                    solved.append(j)
                    print(mono)
                    with open(filelog, 'a') as f:
                        f.write(f"* graph {j}, after {i} tries\n\n")
                        f.write(f"{mono}\n\n")
                    break
            else:
                print(f"No monos for graph {j}")
                no_coaf_mono.append(j)
                with open(filelog, 'a') as f:
                    f.write("No coaffine monomorphisms!\n\n")
    print(f"Graphs in {solved} are solved!")
    print(f"Graphs in {no_coaf_mono} have no coaffine monomorphisms!")
    print(f"Graphs in {uncertain} have no definite answer after checking")
    print(f"{args.bound_monos} monomorphisms for each.")


if __name__ == '__main__':
    main()
