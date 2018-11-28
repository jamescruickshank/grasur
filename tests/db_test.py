import unittest 
import json
import copy

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from sparsity import MyGraph

from models import MyGraphDB

from sage.all import graphs, Graph

from IPython import embed


class BaseDBTestCase(unittest.TestCase):
    def setUp(self):
        self.db = MyGraphDB('../irred.db')


class CreateAndRetrieveTestCase(BaseDBTestCase):
    def runTest(self):
        g = MyGraph(dart_partitions=[[[1,2]],[[1,2]]])
        self.db.create(g)

        d = self.db.get_graph_data(degree_sequence=[2])
        self.assertEqual(len(d),1)

if __name__=="__main__":
    unittest.main(verbosity=2)

