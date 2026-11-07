import cairo, profiles as P
from hand import *
S=2.5
fs=[f for f,*_ in P.CITIES+P.CASTLES+P.HOLY]
cols=8; rows=(len(fs)+cols-1)//cols
W=int(330*S*cols); H=int(230*S*rows)
s,c=new_surface(W,H)
for i,f in enumerate(fs):
    c.save(); c.translate((i%cols)*330*S,(i//cols)*230*S); c.scale(S,S)
    try: f(Pen(c,seed=i+3))
    except Exception as e: print(f.__name__,e)
    c.restore()
s.write_to_png('out/test1.png')
