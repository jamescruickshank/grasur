import unittest 
import json

from RotationSystems import OrientedRotationSystem


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




if __name__=="__main__":
    unittest.main(verbosity=2)
