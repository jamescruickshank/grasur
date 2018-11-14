import unittest 
import json
import copy

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from sparsity import MyGraph
from rotation import OrientedRotationSystem
from graphcollections import GraphCollection,ORSCollection

from sage.all import graphs, Graph

from IPython import embed


class MyEncoder(json.JSONEncoder):
    def default(self,o):
        if isinstance(o,Integer):
            return int(o)
        else:
            return json.JSONEncoder.default(self,o)



class GraphCollectionsBaseTestCase(unittest.TestCase):

    def setUp(self):
        with open('fixtures/mygraphs.json','r') as jsonfile:
            self.data = json.load(jsonfile)

        self.fp = 'test_db.json'
        with open(self.fp,'w+') as dbfile:
            json.dump([],dbfile)
        dbfile.close()
        self.collection = GraphCollection(self.fp)

class ORSCollectionBaseTestCase(unittest.TestCase):
    def setUp(self):
        with open('fixtures/ors.json','r') as orsfile:
            self.data = json.load(orsfile)
        
        self.fp = 'ors_test_db.json'
        with open(self.fp,'w+') as dbfile:
            json.dump([],dbfile)
        dbfile.close()
        self.collection = ORSCollection(self.fp)

class AddGraphTest(GraphCollectionsBaseTestCase):
    def runTest(self):
        g = MyGraph(**self.data["3-gon"])
        h = MyGraph(**self.data["bouquet"])
        self.collection.insert(g)
        self.collection.insert(h)
        self.collection.commit()


        coll = GraphCollection(self.fp)
        self.assertEqual(len(coll.data),2)


class SelectTest(GraphCollectionsBaseTestCase):
    def runTest(self):
        g = MyGraph(**self.data["3-gon"])
        h = MyGraph(**self.data["bouquet"])
        k = MyGraph(**self.data["digon"])
        self.collection.insert(g)
        self.collection.insert(h)
        self.collection.insert(k)
        self.collection.insert(h)
        self.collection.insert(k)

        results1 = self.collection.select(degree_sequence=[4,2,2])
        self.assertEqual(len(results1),2)

        results2 = self.collection.select(v=3)
        #embed()
        self.assertEqual(len(results2),3)



class PrimaryKeyTest(GraphCollectionsBaseTestCase):
    def runTest(self):
        g = MyGraph(**self.data["3-gon"])
        h = MyGraph(**self.data["bouquet"])
        k = MyGraph(**self.data["digon"])
        self.collection.insert(g)
        self.collection.insert(h)
        self.collection.insert(k)
        self.collection.insert(h)
        self.collection.insert(k)

        self.assertEqual(self.collection.pk,6)


class IsomorphsTestCase(GraphCollectionsBaseTestCase):
    def runTest(self):
        g = MyGraph(**self.data["3-gon"])
        h = MyGraph(**self.data["no labels"])
        k = MyGraph(**self.data["digon"])
        self.collection.insert(g)
        self.collection.insert(h)
        self.collection.insert(k)

        t = MyGraph(dart_partitions=[[[1,2],[3,4]],[[1,3],[2,4]]])

        results = self.collection.get_isomorphs(t)

        self.assertEqual(len(results),2)
        #embed()
        self.assertItemsEqual([r[0] for r in results],[2,3])

class ORSCollectionInsertTest(ORSCollectionBaseTestCase):
    def runTest(self):
        k = OrientedRotationSystem(self.data['example 1']['sigma_data'],self.data['example 1']['tau_data'])
        self.collection.insert(k,graph_collection_fp='fixtures/test4.json')
        self.collection.commit()
        #embed()
        res = self.collection.select(id=1)
        self.assertEqual(len(res),1)
        self.assertItemsEqual(res[0]['sigma_perm'],[list(t) for t in k.sigma_perm.cycle_tuples()])




if __name__=="__main__":
    unittest.main(verbosity=2)

