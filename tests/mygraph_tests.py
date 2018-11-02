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
        self.mygraphs = {
                x : MyGraph(**self.data[x]) for x in self.data
        }

class MyGraphConstructorFromGraphTestCase(MyGraphBaseTestCase):
    def runTest(self):
        mg = self.mygraphs["from graph"]
        self.assertItemsEqual(mg.vertices(),[1,2,3])
        self.assertItemsEqual(mg.edges(),[(1,2,"e"),(2,3,"f"),(3,1,"g")])
        self.assertItemsEqual(mg.darts,[1,2,3,4,5,6])
        self.assertEqual(mg.vertex_partition,{1:[1,6],2:[2,3],3:[4,5]})


class MyGraphConstructorPartialLabellingTestCase(MyGraphBaseTestCase):
    def runTest(self):
        mg = self.mygraphs["partially labelled graph"]
        self.assertItemsEqual(mg.edges(),[(1,2,10),(2,1,11)])


class MyGraphConstructorFromDartsTestCase(MyGraphBaseTestCase):
    def runTest(self):
        mg = self.mygraphs["digon"]
        self.assertItemsEqual(mg.vertices(),['u','v'])
        self.assertItemsEqual(mg.edges(),[('u','v','e'),('v','u','f')])
        self.assertItemsEqual(mg.darts,[1,2,3,4])


class MyGraphAutoLabelTestCase(MyGraphBaseTestCase):
    def runTest(self):
        mg = self.mygraphs["no labels"]
        self.assertItemsEqual(mg.vertices(),[0,1])
        self.assertItemsEqual(mg.edges(),[(0,1,0),(1,0,1)])



class MyGraphIsolatedVertexTestCase(MyGraphBaseTestCase):
    def runTest(self):
        mg = self.mygraphs["isolated vertex"]
        self.assertItemsEqual(mg.vertices(),[0,1])
        self.assertItemsEqual(mg.edges(),[(0,0,0)])


class MyGraphDigonSpitTestCase(MyGraphBaseTestCase):
    def runTest(self):
        mg = self.mygraphs["digon"]
        split = mg.digon_split("u",[])
        self.assertItemsEqual(split.vertex_partition,{"u_1":[5,7],"u_2":[1,2,6,8],"v":[3,4]})





if __name__=="__main__":
    unittest.main(verbosity=2)
