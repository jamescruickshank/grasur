import unittest 
import json

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from rotation import OrientedRotationSystem
from sparsity import PebbleGame, MyDiGraph
from sage.all import graphs, Graph
from IPython import embed

class MyDiGraphTestCase(unittest.TestCase):
    def setUp(self):
        with open('fixtures/dg.json','r') as jsonfile:
            data = json.load(jsonfile)
        self.digraphs = {
                key: MyDiGraph(edges=data[key],multiedges=True)
                for key in data
        }



class MultiedgesTestCase(MyDiGraphTestCase):
    def runTest(self):
        dg = self.digraphs['one']
        self.assertEqual(len(dg.edges()),2)



class FindingParallelsTestCase(MyDiGraphTestCase):
    
    def runTest(self):
        dg = self.digraphs['two']
        paras = dg.parallels()
        self.assertItemsEqual(paras,[[0,1],[2,3]])


class FindingBoupuetAndDigonSubGraphTestCase(MyDiGraphTestCase):
    def __runTest(self):
        dg1 = self.digraphs['four']
        dg2 = self.digraphs['five']
        self.assertFalse(dg1.has_2_bouquet_plus_digon())
        self.assertTrue(dg2.has_2_bouquet_plus_digon())


class FindBouquetAndTriangleTestCase(MyDiGraphTestCase):
    def __runTest(self):
        dg1=self.digraphs["six"]
        self.assertTrue(dg1.has_2_bouquet_plus_triangle())


class SubgraphSearchMyDiGraph(MyDiGraphTestCase):
    def runTest(self):
        necklace = self.digraphs['necklace']
        bouquet = self.digraphs['bouquet']
        dg1 = self.digraphs["seven"]
        self.assertEqual(len(dg1.multisubgraph_find(necklace)),4)
        self.assertEqual(len(dg1.multisubgraph_find(bouquet)),2)




if __name__=="__main__":
    unittest.main(verbosity=2)
