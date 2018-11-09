import unittest 
import json
import copy

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from rotation import OrientedRotationSystem
from sparsity import PebbleGame 


from sage.all import graphs, Graph

from IPython import embed


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
            self.data = json.load(orsfile)
        self.or_rot_sys_dict = {
                key : OrientedRotationSystem(
                    self.data[key]['sigma_data'],
                    self.data[key]['tau_data']
                ) for key in self.data.keys()
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
    def XXXrunTest(self):
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

class FacialVertexAdditionsHexagonTestCase(OrientedRotationSystemTestCase):
    def runTest(self):
        r = self.or_rot_sys_dict['hexagon']
        l = r.facial_vertex_additions(1,7,min_new_face_degree=5)
        self.assertEqual(len(l),2)

class FacialVertexAdditionsPentagonTestCase(OrientedRotationSystemTestCase):
    def runTest(self):
        s = self.or_rot_sys_dict["pentagon"]
        result = False
        for j in [1,3,5,7,9]:
            result = result or len(s.facial_vertex_additions(1,j,min_new_face_degree=5))>0
        self.assertFalse(result)

class FacialVertexAdditionsIrredK4TestCase(OrientedRotationSystemTestCase):
    def runTest(self):
        s = self.or_rot_sys_dict["example 1"]
        vert1,vert2 = 1,1
        l = s.facial_vertex_additions(vert1,vert2,min_new_face_degree=5)
        self.assertEqual(len(l),2)


class VertexAdditonK4TestCase1(OrientedRotationSystemTestCase):
    def runTest(self):
        s = self.or_rot_sys_dict["example 1"]
        r = s.vertex_addition(2,5)
        self.assertEqual(r.f_vector(7),(0,0,0,1,1,0,1))
        r = s.vertex_addition(2,7)
        self.assertEqual(r.f_vector(7),(0,0,0,1,0,2,0))

class EdgeInsertionTestCase(OrientedRotationSystemTestCase):
    def runTest(self):
        s = self.or_rot_sys_dict["hexagon"]
        r = s.edge_insertion(3,11)
        self.assertEqual(len(r.face_of(1)),3)


class EdgeAdditonK4TestCase(OrientedRotationSystemTestCase):
    def runTest(self):
        s = self.or_rot_sys_dict["example 1"]
        r = s.edge_insertion(2,3)
        self.assertEqual(r.f_vector(6),(0,0,0,2,0,1))


class FaceOfTestCase(OrientedRotationSystemTestCase):
    def runTest(self):
        r = self.or_rot_sys_dict['hexagon']
        self.assertEqual(r.face_of(3),[3,1,11,9,7,5])


class VertexLabelsTestCase(OrientedRotationSystemTestCase):
    def runTest(self):
        sigma = [tuple(i) for i in self.data['example 1']['sigma_data']]
        tau = [tuple(i) for i in self.data['example 1']['tau_data']]
        labels = [2,4,8,9]
        r = OrientedRotationSystem(sigma,tau,vertex_labels = labels)
        self.assertItemsEqual(labels,r.vertices())



class VertexLabelsUndirectedGraphTestCase(OrientedRotationSystemTestCase):
    def runTest(self):
        sigma = [tuple(i) for i in self.data['example 1']['sigma_data']]
        tau = [tuple(i) for i in self.data['example 1']['tau_data']]
        labels = [2,4,8,9]
        r = OrientedRotationSystem(sigma,tau,vertex_labels = labels)
        self.assertItemsEqual(labels,r.undirected_graph().vertices())


class FromGraphTestCase(OrientedRotationSystemTestCase):
    def XXXrunTest(self):
        g = graphs.CompleteGraph(4)
        l = OrientedRotationSystem.from_graph(g)
        self.assertEqual(len(l),3)



class FromGraphLabelsTestCase(OrientedRotationSystemTestCase):
    def XXXrunTest(self):
        g = Graph()
        g.add_edges([(1,3),(5,6),(3,5),(1,6),(1,5),(3,6)])
        l = OrientedRotationSystem.from_graph(g)
        self.assertItemsEqual(l[0].vertices(),[1,3,5,6])




class PebbleGameLoopedGraphTestCase(unittest.TestCase):
    def runTest(self):
        g = Graph(multiedges=True,loops=True)
        g.add_edge(1,1)
        p = PebbleGame(g.vertices(),2,2)
        self.assertFalse(p.run(g))


class FromMyGraphTestCase(OrientedRotationSystemTestCase):
    def runTest(self):
        pass



if __name__=="__main__":
    unittest.main(verbosity=2)
