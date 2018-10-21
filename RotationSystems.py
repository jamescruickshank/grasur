
from sage.all import *
import time
import json


from Sparsity import MyDiGraph,PebbleGame
from IPython import embed

class OrientedRotationSystem(object):
    """
sigma is a cycle decomposition of 
a permutation of darts and tau is a cycle decomposition of 
a fixed point free involution of darts. Note that the set of 
darts must be [1,2,...,2*e], so tau and sigma must be permutations of that set 
for example 
    r = OrientedRotationSystem([(1,2,3),(4,5,6),(7,8,9),(10,11,12)],[(1,4),(2,12),(3,8),(5,11),(6,7),(9,10)])
creates OrientedRotationSystem instance corresponding to a copy of K_4 embedded in the torus with a quadrilateral face and an octagonal face
"""
    def __init__(self,sigma,tau):
        if isinstance(tau,PermutationGroupElement):
            tau = tau.cycle_tuples()
            sigma = sigma.cycle_tuples()
        if isinstance(tau,list):
            if isinstance(tau[0],list):
                tau = [tuple(x) for x in tau]
                sigma = [tuple(x) for x in sigma]
        self.darts = []
        for e in tau:
            self.darts.append(list(e)[0])
            self.darts.append(list(e)[1])
        self.number_of_darts = len(self.darts)
        self.perm_group = PermutationGroup([sigma,tau],domain=self.darts)
        self.perm_group = PermutationGroup([sigma,tau],domain=self.darts)
        self.sigma_perm,self.tau_perm = self.perm_group(sigma),self.perm_group(tau)
        self.sigma_group = self.perm_group.subgroup([self.sigma_perm])
        self.tau_group = self.perm_group.subgroup([self.tau_perm])
        
        self.cache = {}


    @classmethod
    def dump(cls,rs_list,out_file):
        data_object = [
                [rs.sigma_perm.cycle_tuples(),rs.tau_perm.cycle_tuples()]
                for rs in rs_list
        ]
        with open(out_file,'w') as jsonfile:
            out = json.dump(data_object,jsonfile,indent=1)
        return out


    @classmethod
    def load(cls,in_file):
        with open(in_file,'r') as jsonfile:
            data = json.load(jsonfile)
        return [
                cls(
                    [tuple(c) for c in x[0]],
                    [tuple(c) for c in x[1]]
                ) for x in data
        ]



    @classmethod
    def from_graph(cls,graph,no_isomorphs=True):
        """returns a list a all possible OrientedRotationSystem instances with underlying graph equal to graph. graph should be an instance of sage.all.Graph"""
        edges = graph.edges()
        tau = [[2*i+1,2*i+2] for i in range(len(edges))]
        v_dict = { v:[] for v in graph.vertices() }
        for i in range(len(edges)):
            ed = edges[i]
            v_dict[ed[0]].append(2*i+1)
            v_dict[ed[1]].append(2*i+2)
        c_list = v_dict.values()
        rs_list = []
        for sigma in list_of_cycles(c_list):
            r = cls(sigma,tau)
            # now check for isomorphs
            for e in rs_list:
                if r.is_isomorphic(e):
                    break
            else:
                rs_list.append(r)
        return rs_list


    @classmethod
    def maps_from_graph(cls,graph,max_f_vector=(0,0,0),max_genus=None,min_genus=None):
        l = OrientedRotationSystem.from_graph(graph)
        o = []
        length = len(max_f_vector)
        for r in l:
            fd = r.f_vector(length)
            if min([max_f_vector[i]-fd[i] for i in range(length)]) >=0:
                o.append(r)
        if max_genus is not None:
            o = filter(lambda x: x.genus()<=max_genus,o)
        if min_genus is not None:
            o = filter(lambda x: x.genus()>=min_genus,o)
        print("found %s matching oriented rotation systems for %s"%(len(o),str(graph)))
        return o





    @classmethod
    def from_digraph_data(cls,in_file,out_file=None,*args,**kwargs):
        digraphs = MyDiGraph.load(in_file)
        graphs = [Graph(x.edges(),multiedges=True,loops=True) for x in digraphs]
        print("loaded %s graphs from %s"%(len(graphs),in_file))

        return {
                g.copy(immutable=True) : OrientedRotationSystem.maps_from_graph(g,*args,**kwargs)
            for g in graphs
        }


    def components(self):
        return self.perm_group.orbits()

    def vertices(self):
        return self.sigma_group.orbits()


    def edges(self):
        return self.tau_group.orbits()

    def faces(self):
        if self.cache.has_key('faces')==False:
            g = PermutationGroup([self.sigma_perm*self.tau_perm],domain=self.darts)
            self.cache['faces']=g.orbits()
        return self.cache['faces']

    def undirected_graph(self):
        """returns the underlying undirected graph object"""
        vertex_labels = [min(x) for x in self.sigma_group.orbits()]
        gr = Graph(multiedges=True,loops=True)
        gr.add_vertices(vertex_labels)
        for e in self.edges():
            s = self.sigma_group.orbit(e[0])
            t = self.sigma_group.orbit(e[1])
            gr.add_edge([min(s),min(t)])

        return gr

    def face_degrees(self):
        face_list = self.faces()
        return[len(i) for i in face_list]

    def f_vector(self,length=4):
        fds = self.face_degrees()
        return tuple([fds.count(i+1) for i in range(length)])


    def genus(self):
        return (2 - len(self.faces())+len(self.edges())-len(self.vertices()))/2

    def edge_contraction(self,dart):
        """edge should be a transposition of darts. NB There is no validation that 
        the input is actually an edge"""
        u,v = dart,self.tau_perm(dart)
        e_transp = PermutationGroupElement([(u,v)])
        x = PermutationGroupElement([(v,self.sigma_perm(u))])
        y = PermutationGroupElement([(u,self.sigma_perm(v))])

        con_sigma = self.sigma_perm*x*y*e_transp
        con_tau = self.tau_perm*e_transp
        return OrientedRotationSystem(con_sigma,con_tau)

    def edge_insertion(self,dart1,dart2,new_darts=None):
        """dart1 and dart2 should be on the same face"""
        if new_darts is not None:
            new1,new2 = new_darts
        else:
            new1 = max(self.darts)+1
            new2 = new1+1
        x = PermutationGroupElement([(self.sigma_perm(dart1),new1)])
        y = PermutationGroupElement([(self.sigma_perm(dart2),new2)])
        e_perm = PermutationGroupElement([(new1,new2)])

        in_sig = self.sigma_perm*x*y
        in_tau = self.tau_perm*e_perm
        return OrientedRotationSystem(in_sig,in_tau)


    def edge_deletion(self,dart):

        u,v = dart,self.tau_perm(dart)
        e_transp = PermutationGroupElement([(u,v)])
        x = PermutationGroupElement([(u,self.sigma_perm(u))])
        y = PermutationGroupElement([(v,self.sigma_perm(v))])

        del_sig = self.sigma_perm*x*y
        del_tau = self.tau_perm*e_transp

        return OrientedRotationSystem(del_sig,del_tau)
    

    def quad_contraction(self,dart):
        """The orbit of dart should be a quadrilateral. Returns the rot sys 
        obtained by contracting the quad face""" 
        rho = self.sigma_perm*self.tau_perm
        u,v,w,x = dart,rho(dart),(rho**2)(dart),(rho**3)(dart)
        d1 = max(self.darts)+1
        d2 = d1+1
        p = self.edge_insertion(u,w,new_darts=[d1,d2]).edge_deletion(v).edge_deletion(x).edge_contraction(d1)
        return p


    def is_isomorphic(self,other,mapping=False,orientation_preserving=False):

        # first check the underlying graph and then use the face structure???
        
        if self.number_of_darts != other.number_of_darts:
            return False
        for i in range(1,self.number_of_darts+1):
            val = self.based_isomorphism(other,1,i,mapping=mapping)
            if val !=False:
                return val

        if orientation_preserving==False:
            rev = OrientedRotationSystem(other.sigma_perm.inverse().cycle_tuples(),other.tau_perm.cycle_tuples())
            #other.sigma_perm = other.sigma_perm.inverse()
            return self.is_isomorphic(rev,mapping=mapping,orientation_preserving=True)
        
        return False

    def based_isomorphism(self,other,self_dart,other_dart,mapping=False):
        dart_mapping = {self_dart:other_dart}
        mapped_darts = [self_dart]

        # extend the mapping over an orbit of a dart, 
        # check for conflicts with existing mapping (return false)
        # and extend the mapping to the darts at the other end of the edge
        # while checking for conflicts
        # remove all the darts of the orbit from the mapped_darts list
        # but don't remove the other ends of the edges!
        while len(mapped_darts)>0:
            s = mapped_darts[0]
            t = dart_mapping[s]
            s_cycle = cycle_of(self.sigma_perm,s)
            t_cycle = cycle_of(other.sigma_perm,t)
            if len(s_cycle)!=len(t_cycle):
                return False
            for i in range(len(s_cycle)):
                if dart_mapping.has_key(s_cycle[i]):
                    if dart_mapping[s_cycle[i]] != t_cycle[i]:
                        return False
                dart_mapping[s_cycle[i]]=t_cycle[i]
                try:
                    mapped_darts.remove(s_cycle[i])
                except:
                    pass
                if dart_mapping.has_key(self.tau_perm(s_cycle[i])):
                    if dart_mapping[self.tau_perm(s_cycle[i])]!=other.tau_perm(t_cycle[i]):
                        return False
                else:
                    dart_mapping[self.tau_perm(s_cycle[i])]=other.tau_perm(t_cycle[i])
                    mapped_darts.append(self.tau_perm(s_cycle[i]))

        if mapping:
            return dart_mapping
        else:
            return True
        

def cycle_of(perm,n):
    cycles = perm.cycle_tuples()
    for a in cycles:
        if n in a:
            return a[a.index(n):]+a[:a.index(n)]
    return (n,)


def list_of_cycles(l,pattern=None):

    if len(l) == 1:
        e = l[0]
        return [[tuple(e[:1])+tuple(x)] for x in Permutations(e[1:]).list()]
    else:
        return [  i+j for j in list_of_cycles(l[1:]) for i in list_of_cycles(l[:1])] 


def is_irreducible(rot_sys):
    f = rot_sys.f_vector(4)
    if f[1]>0 or f[2]>0:
        return False
    if f[3]==0:
        return True
    quads = [q for q in rot_sys.faces() if len(q) == 4]
    for q in quads:
        s = rot_sys.quad_contraction(q[0]).undirected_graph()
        pg = PebbleGame(s.vertices(),2,2)
        if pg.run(s):
            return False
        t = rot_sys.quad_contraction(q[1]).undirected_graph()
        pg = PebbleGame(t.vertices(),2,2)
        if pg.run(t):
            return False
    return True



