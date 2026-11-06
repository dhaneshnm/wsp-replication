import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
E=lambda r,c,right: (r,c,right,False); G=lambda r,c,right: (r,c,right,True)
print("Astra L2 hazard aggregators h2[0]=up, h2[1]=down, h2[2]=wait ; logits n/u/d")
for name,pr,ents in [("empty",5,[]),("enemy c5 1 above",5,[E(4,5,True)]),("enemy c4-> 1 above",5,[E(4,4,True)]),
    ("enemy c3-> 1 above",5,[E(4,3,True)]),("enemy c5 2 above",5,[E(3,5,True)]),("enemy c4-> 2 above",5,[E(3,4,True)]),
    ("enemy c3-> 2 above",5,[E(3,3,True)]),("enemy c5 3 above",5,[E(2,5,True)]),
    ("own row c4->",5,[E(5,4,True)]),("own row c3->",5,[E(5,3,True)]),("own row c2->",5,[E(5,2,True)]),("own row c4<- (receding)",5,[E(5,4,False)]),
    ("own row c4-> AND 1-above c5",5,[E(5,4,True),E(4,5,True)]),
    ("row1: own c3->, row2 c5",1,[E(1,3,True),E(2,5,False)]),
    ("row1: own c4->, row2 c5",1,[E(1,4,True),E(2,5,False)])]:
    h1,h2,z,p=fwd(AST,obs(pr,ents))
    print(f"  {name:32s} up={h2[0]:+.2f} down={h2[1]:+.2f} wait={h2[2]:+.2f} | logits n/u/d {z[0]:+7.2f} {z[2]:+7.2f} {z[4]:+7.2f} | {fmtp(p)}")
print("Astra L1 treasure units h1[24:32] (row r unit = 23+r), player row 5, gold at c3->:")
for r in range(1,9):
    h1,h2,z,p=fwd(AST,obs(5,[G(r,3,True)]))
    print(f"  gold row {r}: unit {23+r} = {h1[23+r]:+.3f}; others max {np.max(np.delete(h1[24:32],r-1)):+.3f} | {fmtp(p)}")
for c,right in [(1,True),(4,True),(5,True),(6,True),(5,False),(4,False),(8,False)]:
    h1,_,_,_=fwd(AST,obs(5,[G(3,c,right)]))
    print(f"  gold row 3 at c{c} {'->' if right else '<-'}: unit 26 = {h1[26]:+.3f}")
