import sys
import random
import matplotlib.pyplot as plt

# define a class to represent the nodes
class Node :
    # each node contains a list of other nodes it has edges to
    def __init__ (self):
        self.edges = []
        self.degree = 0
        self.id = -1
        # these are the numerators for calculating death/birth probabilities
        #self.birthNum = 0.0
        #self.deathNum = 0.0
    
    # this prints the ids of the edges of the node
    def __str__(self):
        mystr = "Node " + str(self.id) + " has edges to:"
        for i in range(self.degree):
            mystr += "\n\tNode " + str(self.edges[i].id)
        return mystr
    __repr__ = __str__

# define a class to use for the adjacency list
class AdjList :
    # the AdjList contains a list (alist) of nodes 

    # NOTE if we organize this by decreasing order of degree, then
    # it will be quicker to calc the probabilities

    def __init__(self):
        # first up, we want to set up the default graph
        # with one node and a self loop
        self.nNodes = 1
        self.nEdges = 0
        self.alist = []
        n = Node()
        n.id = 0
        n.degree = 0
        self.maxDegree = 0
        self.nodesAtMaxDegree = 1
        # do not add the self loop, as this causes math errors
        #n.edges.append(n)
        self.birthDen = 1.0
        self.deathDen = 1.0
        self.alist.append(n)

    # add a node n to the list with an edge to the node at index m
    def addNode(self,m,t):
        n = Node()
        n.edges.append(self.alist[m])
        n.degree = 1
        n.id = t
        self.nNodes += 1
        self.nEdges += 1
        #n.birthNum = 1.0
        #n.deathNum = float(self.nNodes) - 1.0
        self.alist.append(n)

        # now update degree of m, and add n to its list of edges
        self.alist[m].degree += 1
        self.alist[m].edges.append(n)

        # this block will be used to look at degrees later
        if self.alist[m].degree > self.maxDegree :
            self.maxDegree = self.alist[m].degree
            self.nodesAtMaxDegree = 1
        elif self.alist[m].degree == self.maxDegree :
            self.nodesAtMaxDegree += 1

        # update the global probability denominators
        self.birthDen = float(2*self.nEdges)
        # if self.birthDen == 0:
        #     print "Warning: Adding a new node set birthDen to 0."
        self.deathDen = float((self.nNodes*self.nNodes) - (2*self.nEdges))
        # if self.deathDen == 0:
        #     print "Warning: Adding a new node set deathDen to 0."

    # this removes a node at index m and updates the list
    def remNode(self,m):
        # first update the degrees and remove the edges
        rnode = self.alist[m]
        self.nNodes -= 1        
        for i in range(rnode.degree):
            #print "DEBUG I=" + str(i)
            # j is set to each node with an edge to m
            if rnode.edges[i].degree == self.maxDegree :
                self.nodesAtMaxDegree -= 1

            # just make sure we dont remove itself first
            if rnode.id != rnode.edges[i].id:
                rnode.edges[i].degree -= 1
                rnode.edges[i].edges.remove(rnode)
                self.nEdges -= 1

        # then remove the node
        self.alist.remove(self.alist[m])
        self.birthDen = float(2*self.nEdges)
        # if self.birthDen == 0:
        #     print "\tWarning: birthDen set to 0."
        #     print "\tNodes: " + str(self.nNodes) + " Edges: " + str(self.nEdges)
        self.deathDen = float((self.nNodes*self.nNodes) - (2*self.nEdges))
        # if self.deathDen == 0:
        #     print "\tWarning: deathDen set to 0."
        #     print "\t# Nodes: " + str(self.nNodes) + ", # edges: " + str(self.nEdges)


    def printLength(self):
        print "graph is length: " + str(self.nNodes)

    def printList(self):
        print "Graph contains these nodes: "
        for i in range(self.nNodes):
            j = self.alist[i]
            print str(j)
    
# this definition will do a random number to decide if the next event
# will be a birth or death. It needs to know the probabilities of each
def RollForEvent(g,t,bp):
    event = random.random()
    nChoice = random.random()
    if event <= bp:
        #print str(t) + ": Birth chosen!"
        # choose a node to connect to
        found = 0
        i = 0
        p = 0.0

        # this is called if theres only one node
        if g.nNodes == 1:
            found = 1
            g.addNode(0,t)
            #print "\tAdded a node with an edge to node " + str(g.alist[0].id)
        # this is called if there are multiple nodes
        while found == 0:
            # Calc the probability for this node and add it to the sum
            # check for special case of no edges (island nodes)
            if g.nEdges == 0: # this avoids divide by zero
                incr = 1 / g.nNodes
                p += incr
            else: # default case
                p += float(g.alist[i].degree) / float(g.birthDen)
            #print "p=" + str(p)
            if nChoice <= p:
                # we found the right node to connect to, add the new one in
                found = 1
                g.addNode(i,t)
                #print "\tAdded a node with an edge to node " + str(g.alist[i].id)
                break
            #print "i=" + str(i)
            if i < g.nNodes - 1:
                i += 1
            else:
                #print "\tERROR: Unable to choose birth node connection"
                #print "Final p value: " + str(p)
                #print "final rand value: " + str(nChoice)
                found = -1

    else: # if event > bp, we chose death
        #print str(t) + ": Death chosen!"
        # choose a node to remove
        found = 0
        i = 0
        p = 0.0

        # this is called if there's one node
        if g.nNodes == 1:
            # we are removing the only node, kill the sim
            found = -1
            #print "\tRemoved node " + str(g.alist[0].id)
            g.remNode(0)
        # this is called if there's multiple nodes
        while found == 0:
            # Calc the probability for this node and add it to the sum
            if g.nEdges == 0: # this avoids divide by zero
                incr = 1 / g.nNodes
                p += incr
            else: # default case
                p = p + float(g.nNodes - g.alist[i].degree) / float(g.deathDen)
            #print "p at " + str(i) + " is " + str(p)
            if nChoice <= p:
                # we found the right node to remove
                found = 1
                #print "\tRemoved node " + str(g.alist[i].id)
                g.remNode(i)
                break

            #print "i=" + str(i)
            if i < g.nNodes - 1:
                i += 1
            else:
                # this is all debug stuff
                #print "\tERROR: Unable to choose death node"
                found = -1
    return found


# this will perform one runthrough of the simulation.
def performSim(mygraph, simLength, birthP):
    # here is the main loop of the simulation
    i = 0
    badRun = 1
    fig1data = []
    fig2data = []
    # loop until we get a run that finishes...
    while badRun == 1:
        badRun = 0
        # main sim loop
        for i in range(simLength):
            if RollForEvent(mygraph, i + 1, birthP) == -1:
                # we didnt find a node, or removed the only node
                # hence this is a bad run
                #print "Exiting simulation early..."
                badRun = 1
                # reset the graph
                mygraph = AdjList()
                break
            # check if we reached a 5th of the input size
            if i == simLength/5 :
                # record first data point
                fig1data.append(mygraph.nNodes)
                fig2data.append(mygraph.nEdges)
            elif i == 2*simLength / 5 :
                fig1data.append(mygraph.nNodes)
                fig2data.append(mygraph.nEdges)
            elif i == 3*simLength / 5 :
                fig1data.append(mygraph.nNodes)
                fig2data.append(mygraph.nEdges)
            elif i == 4*simLength / 5 :
                fig1data.append(mygraph.nNodes)
                fig2data.append(mygraph.nEdges)

    # print the statistics
    fig1data.append(mygraph.nNodes)
    fig2data.append(mygraph.nEdges)
    print "Simulation Completed at turn " + str(i + 1)
    print "\tTotal nodes at completion: " + str(mygraph.nNodes)
    print "\tTotal edges at completion: " + str(mygraph.nEdges) + "\n"
    return mygraph, fig1data, fig2data


def CountWithDegree(g):
    # count the number of nodes with a given degree i
    degrees = []
    probs = []
    totalNodes = g.nNodes

    # initialize our arrays
    for i in range((g.maxDegree+1)):
        degrees.append(0)
        p = (float(totalNodes) - float(i)) / (float(totalNodes * totalNodes) - float(2 * g.nEdges))
        probs.append(p)

    print "Max degree is: " + str(g.maxDegree)
    # now count all the degrees
    for j in range(g.nNodes):
        # here we count the number of nodes at each degree
        itr = g.alist[j].degree
        degrees[itr] += 1

    # note that this creates a index at zero for degrees and probs that should be ignored later
    return degrees, probs


def main():
    # handle the cmdline args
    if len(sys.argv) < 1 :
        print "ERROR: Invalid command line arguments"
        print "USAGE: python a2.py numberOfTurns"
        exit(0)
    simLength = int(sys.argv[1])

    # initialize the random function and the graph
    random.seed()
    mygraph = AdjList()
    mygraph2 = AdjList()
    mygraph3 = AdjList()

    mygraph, vec1, edges1 = performSim(mygraph,simLength,0.6)
    mygraph2, vec2, edges2 = performSim(mygraph2,simLength,0.75)
    mygraph3, vec3, edges3 = performSim(mygraph3,simLength,0.9)

    # plot the graphs using pyplot
    # plt.plot(vec1)
    # plt.plot(vec2)
    # plt.plot(vec3)
    # plt.show()
    #
    # plt.plot(edges1)
    # plt.plot(edges2)
    # plt.plot(edges3)
    # plt.show()

    # fig 5:
    # we know that we need a for loop from 1 to k
    #   k is the max degree
    # set sum = 0
    # at each step we take the probability of the node being chosen for deletion
    #   sum this to prior results, if any, and plot the sum
    #   i++
    print "Finished calculating graphs!"
    fig3 = []
    degreeList, plist = CountWithDegree(mygraph2)
    sum = 0.0
    #print "DL: " + str(len(degreeList)) + " PL: " + str(len(plist))
    for i in range(len(degreeList)-1, 1, -1):
        #print str(i)
        # get the base probability of deleting this node
        # multiply this probability by the number of nodes with that degree...
        p = plist[i] * degreeList[i]
        sum += p
        fig3.append(sum)

    # reverse the list
    fig3.reverse()
    plt.plot(fig3, 'ro')
    plt.xscale('log')
    plt.yscale('log')
    plt.axis([0, 100, 0.00001, 1])
    plt.show()
    exit(0)


if __name__ == "__main__":
    main()
