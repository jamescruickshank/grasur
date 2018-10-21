import unittest 
import json
import copy

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from RotationSystems import OrientedRotationSystem
from Sparsity import PebbleGame 


from sage.all import graphs, Graph



def get_rotation_systems(jsonfile):
    with open(jsonfile,'r') as jsonfile:
        data = json.load(jsonfile)
        return {
                key : OrientedRotationSystem(
                    data[key]['sigma_data'],
                    data[key]['tau_data']
                ) for key in data.keys()
        }




class OrientedRotationSystemTestCase(unittest.TestCase):

    def setUp(self):
        with open('fixtures/ors.json','r') as orsfile:
            data = json.load(orsfile)
        self.or_rot_sys_dict = {
                key : OrientedRotationSystem(
                    data[key]['sigma_data'],
                    data[key]['tau_data']
                ) for key in data.keys()
        }



class GenusTestCase(OrientedRotationSystemTestCase):
    def runTest(self):
        ros = self.or_rot_sys_dict['example 1']
        self.assertEqual(ros.genus(),1)

class DartsTestCase(OrientedRotationSystemTestCase):
    def runTest(self):
        ros = self.or_rot_sys_dict['example 2']
        darts = ros.darts
        darts.sort()
        self.assertEqual(darts,[1,2,3,5,6,7])


class EdgeCountTestCase(OrientedRotationSystemTestCase):
    def runTest(self):
        ros = self.or_rot_sys_dict['example 2']
        self.assertEqual(len(ros.edges()),3)

class VertexCountTestCase(OrientedRotationSystemTestCase):
    def runTest(self):
        ros = self.or_rot_sys_dict['example 2']
        self.assertEqual(len(ros.vertices()),2)

class FaceCountTestCase(OrientedRotationSystemTestCase):
    def runTest(self):
        ros = self.or_rot_sys_dict['example 2']
        #print(ros.faces())
        self.assertEqual(len(ros.faces()),3)

class FromGraphTestCase(unittest.TestCase):
    def runTest(self):
        g = graphs.CompleteGraph(4)
        l = OrientedRotationSystem.from_graph(g)
        for r in l:
            self.assertTrue(g.is_isomorphic(r.undirected_graph()))


class OrientationPreservingIsoTestCase(OrientedRotationSystemTestCase):
    def runTest(self):
        ros = self.or_rot_sys_dict['no-inv1']
        self.assertTrue(ros.is_isomorphic(ros))
        #rev = OrientedRotationSystem(ros.sigma_perm.inverse().cycle_tuples(),ros.tau_perm.cycle_tuples())
        #rev.sigma_perm = rev.sigma_perm.inverse()
        rev = self.or_rot_sys_dict['no-inv2']
        self.assertTrue(ros.is_isomorphic(rev))
        self.assertFalse(ros.is_isomorphic(rev,orientation_preserving=True))


class PebbleGameLoopedGraphTestCase(unittest.TestCase):
    def runTest(self):
        g = Graph(multiedges=True,loops=True)
        g.add_edge(1,1)
        p = PebbleGame(g.vertices(),2,2)
        self.assertFalse(p.run(g))



if __name__=="__main__":
    unittest.main(verbosity=2)
