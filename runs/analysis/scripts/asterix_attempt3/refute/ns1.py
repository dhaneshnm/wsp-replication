import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nosticky import ep, np, wsp
from concurrent.futures import ProcessPoolExecutor
if __name__=="__main__":
    which=sys.argv[1]; sticky=float(sys.argv[2])
    with ProcessPoolExecutor(4) as ex:
        r=list(ex.map(ep,[(which,s,sticky,False) for s in range(200)],chunksize=5))
    sc=np.array([x[0] for x in r]); L=np.array([x[1] for x in r])
    print(f"{which} sticky={sticky} sampled: mean {sc.mean():.2f} se {sc.std(ddof=1)/np.sqrt(len(sc)):.2f} len {L.mean():.0f} capped {(L==wsp.MAX_STEPS).sum()}")
