import sys, profiles as P
from hand import *
S=4
names=sys.argv[1].split(',')
fs=[getattr(P,n) for n in names]
cols=4; rows=(len(fs)+cols-1)//cols
s,c=new_surface(330*S*cols,230*S*rows)
for i,f in enumerate(fs):
    c.save(); c.translate((i%cols)*330*S,(i//cols)*230*S); c.scale(S,S); f(Pen(c,seed=i+3)); c.restore()
s.write_to_png('out/test2.png')
from PIL import Image; Image.open('out/test2.png').convert('RGB').save('out/test2.jpg',quality=80)
