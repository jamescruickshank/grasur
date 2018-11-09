import unittest 
import json
import copy

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from sparsity import MyGraph


from sage.all import graphs, Graph

from IPython import embed



class MyGraphBaseTestCase(unittest.TestCase):

    def setUp(self):
        with open('fixtures/mygraphs.json','r') as jsonfile:
            self.data = json.load(jsonfile)


class FromTuplesTestCase(MyGraphBaseTestCase):
    def runTest(self):
        g = MyGraph(dart_partitions=[[(1,2,3),(4,)],[(1,2),(3,4)]])
        self.assertDictEqual(g.vertex_partition(),{0:[1,2,3],1:[4]})

class MyGraphConstructorFromGraphTestCase(MyGraphBaseTestCase):
    def runTest(self):
        mg = MyGraph(**self.data["from graph"])
        self.assertItemsEqual(mg.vertices(),[1,2,3])
        self.assertItemsEqual(mg.edges(),[(1,2,"e"),(2,3,"f"),(3,1,"g")])
        self.assertItemsEqual(mg.darts,[1,2,3,4,5,6])
        self.assertEqual(mg.vertex_partition(),{1:[1,6],2:[2,3],3:[4,5]})


class MyGraphConstructorPartialLabellingTestCase(MyGraphBaseTestCase):
    def runTest(self):
        mg = MyGraph(**self.data["partially labelled graph"])
        self.assertItemsEqual(mg.edges(),[(1,2,10),(2,1,11)])


class MyGraphConstructorFromDartsTestCase(MyGraphBaseTestCase):
    def runTest(self):
        mg = MyGraph(**self.data["digon"])
        self.assertItemsEqual(mg.vertices(),['u','v'])
        self.assertItemsEqual(mg.edges(),[('u','v','e'),('v','u','f')])
        self.assertItemsEqual(mg.darts,[1,2,3,4])


class MyGraphAutoLabelTestCase(MyGraphBaseTestCase):
    def runTest(self):
        mg = MyGraph(**self.data["no labels"])
        self.assertItemsEqual(mg.vertices(),[0,1])
        self.assertItemsEqual(mg.edges(),[(0,1,0),(1,0,1)])



class MyGraphIsolatedVertexTestCase(MyGraphBaseTestCase):
    def runTest(self):
        mg = MyGraph(**self.data["isolated vertex"])
        self.assertItemsEqual(mg.vertices(),[0,1])
        self.assertItemsEqual(mg.edges(),[(0,0,0)])


class MyGraphDigonSplitTestCase(MyGraphBaseTestCase):
    def runTest(self):
        mg = MyGraph(**self.data["digon"])
        split = mg.digon_split("u",[],vertex_labels=("u_1","u_2"))
        self.assertItemsEqual(split.vertex_partition(),{"u_1":[5,7],"u_2":[1,2,6,8],"v":[3,4]})


class MyGraphDigonSplitSelfTestCase(MyGraphBaseTestCase):
    def runTest(self):
        mg = MyGraph(**self.data["no labels"])
        split = mg.digon_split(0,[2])
        t = split.digon_split(3,[1])

        self.assertEqual(len(t.edges()),6)
        self.assertItemsEqual(mg.vertex_partition(),{0:[1,2],1:[3,4]})


class MyGraphOneExtensionTestCase(MyGraphBaseTestCase):
    def runTest(self):
        mg = MyGraph(**self.data["3-gon"])
        sp = mg.one_extension(0,2)
        self.assertItemsEqual(sp.vertex_partition().values(),[[1,2],[3,4],[5,6,7],[8,9,10]])
        self.assertItemsEqual(sp.edge_partition().values(),[[2,8],[9,3],[10,7],[4,5],[6,1]])

class MyGraphAdjacencyCountTestCase(MyGraphBaseTestCase):
    def runTest(self):
        bqt = MyGraph(**self.data["bouquet"])
        self.assertEqual(bqt.adjacencies(0,1),2)
        self.assertEqual(bqt.adjacencies(0,2),0)



class MyGraphSubGraphSearchTestCase(MyGraphBaseTestCase):
    def runTest(self):
        bqt = MyGraph(**self.data["bouquet"])
        digon = MyGraph(**self.data["2-gon"])
        tri = MyGraph(**self.data["3-gon"])
        self.assertEqual(len(bqt.subgraph_find(digon)),1)
        self.assertEqual(len(bqt.subgraph_find(tri)),0)
        self.assertEqual(len(tri.subgraph_find(tri,first_match_only=False)),6)


class MyGraphSubGraphSearchK4TestCase(MyGraphBaseTestCase):
    def runTest(self):
        tri = MyGraph(**self.data["3-gon"])
        k4 = MyGraph(graphs.CompleteGraph(4))
        self.assertEqual(len(k4.subgraph_find(tri,first_match_only=False)),24)


class MyGraphExtensionsOfTestCase(MyGraphBaseTestCase):
    def runTest(self):
        t1 = MyGraph(dart_partitions=[[[]],[]])
        t2 = MyGraph.extensions_of(t1)
        t3 = MyGraph.extensions_of(t2)
        self.assertEqual(len(t3),2)
        t4 = MyGraph.extensions_of(t3)
        self.assertEqual(len(t4),9)



class EdgeDeletionTestCase(MyGraphBaseTestCase):
    def runTest(self):
        g = MyGraph(**self.data["digon"])
        h = g.edge_deletion("f")
        self.assertDictEqual(h.edge_partition(),{"e":[1,3]})


class EdgeDeletionTestCase2(MyGraphBaseTestCase):
    def runTest(self):
        g = MyGraph([[0,1,0],[0,2,1],[0,3,2],[1,2,3],[1,3,4],[2,3,5]])
        h = g.edge_deletion(0).edge_deletion(5)
        k = MyGraph(**self.data["4-gon"])
        self.assertEqual(len(h.isomorphisms(k)),1)


class VertexDeletionTestCase(MyGraphBaseTestCase):
    def runTest(self):
        g = MyGraph([[0,1,0],[0,2,1],[0,3,2],[1,2,3],[1,3,4],[2,3,5]])
        h = g.vertex_deletion(0)
        k = MyGraph(**self.data["3-gon"])
        self.assertEqual(len(h.isomorphisms(k)),1)

class DiValentVertexTestCase(MyGraphBaseTestCase):
    def runTest(self):
        k = MyGraph(**self.data["3-gon"])
        self.assertItemsEqual(k.find_divalent_vertex(),(0,1,2))
        self.assertEqual(k.find_divalent_vertex()[0],0)



class DiValentVertexTestCase2(MyGraphBaseTestCase):
    def runTest(self):
        k = MyGraph([[0,1,0],[0,2,1],[0,3,2],[1,2,3],[1,3,4],[2,3,5]])
        self.assertEqual(k.find_divalent_vertex(),None)
        l = k.edge_deletion(0)
        self.assertItemsEqual(l.find_divalent_vertex()[1:],(2,3))



if __name__=="__main__":
    unittest.main(verbosity=2)
