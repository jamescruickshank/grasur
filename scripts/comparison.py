
from IPython import embed 

from rotation import OrientedRotationSystem

import json 
import os


#
fns = os.listdir('data/')

l = []
for fn in fns:
    print("loading data from %s"%fn)
    with open("data/%s"%fn) as datafile:
        data = json.load(datafile)
    l.append((OrientedRotationSystem(data[0][0],data[0][1]),fn))


sl = []
for o in l:
    for m in sl:
        if o[0].is_isomorphic(m[0]):
            print("%s is isomorphic to %s"%(o[1],m[1]))
            break
    else:
        sl.append(o)



fnsb = [x for x in os.listdir('../seven/') if x.startswith('ors')]

k = []
for fn in fnsb:
    print("loading data from %s"%fn)
    with open("../seven/%s"%fn) as datafile:
        data = json.load(datafile)
    for x in data:
        k.append((OrientedRotationSystem(x["sigma_perm"],x["tau_perm"]),(fn,data.index(x))))


sk = []
for o in k:
    for m in sk:
        if o[0].is_isomorphic(m[0]):
            break
    else:
        sk.append(o)




#embed()


sl_extras = []


for o in sl:
    for m in sk:
        if o[0].is_isomorphic(m[0]):
            print("%s = %s"%(str(o[1]),str(m[1])))
            #sl.remove(o)
            #sk.remove(m)
            break
    else:
        sl_extras.append(o)

print("%s in sl that are not in sk"%len(sl_extras))


sk_extras = []


for o in sk:
    for m in sl:
        if o[0].is_isomorphic(m[0]):
            print("%s = %s"%(str(o[1]),str(m[1])))
            #sl.remove(o)
            #sk.remove(m)
            break
    else:
        sk_extras.append(o)

print("%s in sk that are not in sl"%len(sk_extras))



#embed()

