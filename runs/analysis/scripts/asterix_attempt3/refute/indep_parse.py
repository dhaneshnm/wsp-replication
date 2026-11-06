import sys,re; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
A="/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt3/"
txt=open(A+"answer.md").read()
blocks=re.findall(r"```edits\n(.*?)```", txt, re.S); print("edits blocks:",len(blocks))
ns={k:np.zeros(s,np.float32) for k,s in wsp.SHAPES.items()}
n=0
for line in blocks[-1].splitlines():
    line=line.split("#")[0].strip()
    if not line: continue
    exec(line,{},ns); n+=1
print("statements exec'd:",n)
net=wsp.load_npz(A+"net.npz")
for k in net: print(k, "max|diff| indep exec vs net.npz:", float(np.abs(net[k]-ns[k]).max()))
# spot-print a few entries
print("W1[64:120:6,24] =", net["W1"][64:120:6,24]); print("W1[61:120:6,24] =", net["W1"][61:120:6,24])
print("b2 =", net["b2"]); print("b3 =", net["b3"])
