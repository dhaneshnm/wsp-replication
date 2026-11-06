import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from envprobe import *
show("row 7 empty (wants up)", state(7, 5, False))
show("row 7, fish row6 col5 moving L", state(7, 5, False, fish=[(6, 5, False)]))
show("row 7, fish row6 col7 moving L", state(7, 5, False, fish=[(6, 7, False)]))
show("row 7, fish row6 col1 moving R", state(7, 5, False, fish=[(6, 1, True)]))
show("row 3 empty (wants down)", state(3, 5, False))
show("row 3, fish row4 col6 moving L", state(3, 5, False, fish=[(4, 6, False)]))
show("row 4, diver row7 col2 (target below)", state(4, 5, False, divers=[(7, 2, True)]))
show("row 4, diver row7 col2 + fish row5 col5", state(4, 5, False, divers=[(7, 2, True)], fish=[(5, 5, False)]))
show("SURF row 5 oxy50 dc1, fish row4 col5", state(5, 5, False, oxy=50, ndiv=1, fish=[(4, 5, False)]))
show("SURF row 5 oxy50 dc1, fish row4 col6 moving L", state(5, 5, False, oxy=50, ndiv=1, fish=[(4, 6, False)]))
