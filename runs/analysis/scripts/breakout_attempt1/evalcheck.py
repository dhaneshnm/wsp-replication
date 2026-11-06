import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
if __name__ == "__main__":
    print(wsp.evaluate(nets()["claude"], "breakout", episodes=200, workers=4))
