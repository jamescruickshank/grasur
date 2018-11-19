
from rotation import *
from sparsity import *
from graphcollections import *

from IPython import embed
import os

fns = os.listdir('seven/')

#with open('seven/filenames.txt') as fns:
filenames = [x.strip('\n') for x in fns if x.startswith('ors')]


stop = True
embed()
if stop:
    raise ValueError


count=0

for f in filenames:
    r = ORSCollection('seven/%s'%f)
    count += len(r.data)

print(count)






