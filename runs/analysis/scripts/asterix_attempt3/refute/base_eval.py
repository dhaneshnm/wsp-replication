import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
if __name__=="__main__":
    print("original", wsp.evaluate(NET,"asterix",episodes=200,workers=4))
