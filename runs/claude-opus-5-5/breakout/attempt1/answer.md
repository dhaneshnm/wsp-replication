## Design

**Strategy.** The policy predicts the column where the ball will reach the bottom row. It then moves the paddle toward that column and waits there (no-op) once it arrives. Waiting is robust to sticky actions, because a repeated no-op does no harm.

- **Ball descending.** The landing column is exact. Unfold the path as u = x + vx·(9 − y), then fold it at the walls with f(u):
  - u for 0..9
  - 19 − u for 10..19
  - −1 − u for negative u
  
  This matches the game's wall clipping, which gives the folding a period of 20. A catch only needs the paddle at the landing column after the last move.
- **Ball ascending.** The policy uses a guess. It assumes the ball turns just under the brick rows (row 4) and moves 1 column sideways on the turn step. From row 8 the guess is 9 − c whatever the direction, which conveniently ignores the unknown direction right after a paddle hit.

**Layer 1 (6 units used).**
- **Units 0–3 (Δ units).** One per mode: down-right, down-left, up-right, up-left. Each computes tanh(L_mode(ball cell) − paddle column). The ball input is one-hot, so any lookup table of the ball cell is linear. Ball weights are the landing table and paddle weights are −c.
- **Unit 4 (gH, "moving right").** It is the sign of 2·dx + [ball in column 0] − [ball in column 9], with dx = ball column − trail column. Ball weights carry +column and trail weights carry −column. This handles wall bounces and the start state.
- **Unit 5 (gV, "descending").** It is the sign of dy + 0.5 − [ball in row 8], with dy = ball row − trail row. This handles brick and ceiling bounces (dy = 0 means now moving down). It also handles paddle hits (dy = 0 at row 8 means now moving up).

**Layer 2 (8 units).** For each mode there is a "go right" unit, tanh(6·Δ − 2.28 ± 10·gV ± 10·gH − 20). There is a matching "go left" unit with −6·Δ. A unit can only fire when both gates match its mode. It then fires if the paddle is at least one column off the target in its direction.

**Output.**
- The right logit is 8 × (sum of the right units) + 32, and the left logit is built the same way. This gives about 16 when moving is wanted and about 0 otherwise.
- No-op has a bias of 6, so it wins when the paddle is on target.
- Up, down and fire are suppressed with a bias of −10.

```edits
# ---------- Layer 1: Delta units (ball landing table minus paddle column) ----------
# unit 0: descending, vx=+1
W1[3:60:6, 0]    = [9,9,8,7,6,5,4,3,2,1]
W1[63:120:6, 0]  = [8,9,9,8,7,6,5,4,3,2]
W1[123:180:6, 0] = [7,8,9,9,8,7,6,5,4,3]
W1[183:240:6, 0] = [6,7,8,9,9,8,7,6,5,4]
W1[243:300:6, 0] = [5,6,7,8,9,9,8,7,6,5]
W1[303:360:6, 0] = [4,5,6,7,8,9,9,8,7,6]
W1[363:420:6, 0] = [3,4,5,6,7,8,9,9,8,7]
W1[423:480:6, 0] = [2,3,4,5,6,7,8,9,9,8]
W1[483:540:6, 0] = [1,2,3,4,5,6,7,8,9,9]
# unit 1: descending, vx=-1
W1[3:60:6, 1]    = [8,7,6,5,4,3,2,1,0,0]
W1[63:120:6, 1]  = [7,6,5,4,3,2,1,0,0,1]
W1[123:180:6, 1] = [6,5,4,3,2,1,0,0,1,2]
W1[183:240:6, 1] = [5,4,3,2,1,0,0,1,2,3]
W1[243:300:6, 1] = [4,3,2,1,0,0,1,2,3,4]
W1[303:360:6, 1] = [3,2,1,0,0,1,2,3,4,5]
W1[363:420:6, 1] = [2,1,0,0,1,2,3,4,5,6]
W1[423:480:6, 1] = [1,0,0,1,2,3,4,5,6,7]
W1[483:540:6, 1] = [0,0,1,2,3,4,5,6,7,8]
# unit 2: ascending, vx=+1 (guess: turn at row 4)
W1[3:60:6, 2]    = [9,8,7,6,5,4,3,2,1,0]
W1[63:120:6, 2]  = [8,7,6,5,4,3,2,1,0,0]
W1[123:180:6, 2] = [9,8,7,6,5,4,3,2,1,0]
W1[183:240:6, 2] = [9,9,8,7,6,5,4,3,2,1]
W1[243:300:6, 2] = [6,7,8,9,9,8,7,6,5,4]
W1[303:360:6, 2] = [7,8,9,9,8,7,6,5,4,3]
W1[363:420:6, 2] = [8,9,9,8,7,6,5,4,3,2]
W1[423:480:6, 2] = [9,9,8,7,6,5,4,3,2,1]
W1[483:540:6, 2] = [9,8,7,6,5,4,3,2,1,0]
# unit 3: ascending, vx=-1
W1[3:60:6, 3]    = [9,8,7,6,5,4,3,2,1,0]
W1[63:120:6, 3]  = [9,9,8,7,6,5,4,3,2,1]
W1[123:180:6, 3] = [9,8,7,6,5,4,3,2,1,0]
W1[183:240:6, 3] = [8,7,6,5,4,3,2,1,0,0]
W1[243:300:6, 3] = [5,4,3,2,1,0,0,1,2,3]
W1[303:360:6, 3] = [6,5,4,3,2,1,0,0,1,2]
W1[363:420:6, 3] = [7,6,5,4,3,2,1,0,0,1]
W1[423:480:6, 3] = [8,7,6,5,4,3,2,1,0,0]
W1[483:540:6, 3] = [9,8,7,6,5,4,3,2,1,0]
# paddle column (row 9, channel 0), subtracted
W1[540:600:6, 0] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[540:600:6, 1] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[540:600:6, 2] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[540:600:6, 3] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]

# ---------- unit 4: gH (moving right) = sign(2dx + [c=0] - [c=9]), scale 4 ----------
W1[3:600:60, 4] = 4
W1[9:600:60, 4] = 8
W1[15:600:60, 4] = 16
W1[21:600:60, 4] = 24
W1[27:600:60, 4] = 32
W1[33:600:60, 4] = 40
W1[39:600:60, 4] = 48
W1[45:600:60, 4] = 56
W1[51:600:60, 4] = 64
W1[57:600:60, 4] = 68
W1[10:600:60, 4] = -8
W1[16:600:60, 4] = -16
W1[22:600:60, 4] = -24
W1[28:600:60, 4] = -32
W1[34:600:60, 4] = -40
W1[40:600:60, 4] = -48
W1[46:600:60, 4] = -56
W1[52:600:60, 4] = -64
W1[58:600:60, 4] = -72

# ---------- unit 5: gV (descending) = sign(dy + 0.5 - [r=8]), scale 8 ----------
W1[63:120:6, 5] = 8
W1[123:180:6, 5] = 16
W1[183:240:6, 5] = 24
W1[243:300:6, 5] = 32
W1[303:360:6, 5] = 40
W1[363:420:6, 5] = 48
W1[423:480:6, 5] = 56
W1[483:540:6, 5] = 56
W1[64:120:6, 5] = -8
W1[124:180:6, 5] = -16
W1[184:240:6, 5] = -24
W1[244:300:6, 5] = -32
W1[304:360:6, 5] = -40
W1[364:420:6, 5] = -48
W1[424:480:6, 5] = -56
W1[484:540:6, 5] = -64
W1[544:600:6, 5] = -72
b1[5] = 4

# ---------- Layer 2: gated move-right (0-3) and move-left (4-7) units ----------
W2[0, 0] = 6
W2[4, 0] = 10
W2[5, 0] = 10
W2[1, 1] = 6
W2[4, 1] = -10
W2[5, 1] = 10
W2[2, 2] = 6
W2[4, 2] = 10
W2[5, 2] = -10
W2[3, 3] = 6
W2[4, 3] = -10
W2[5, 3] = -10
W2[0, 4] = -6
W2[4, 4] = 10
W2[5, 4] = 10
W2[1, 5] = -6
W2[4, 5] = -10
W2[5, 5] = 10
W2[2, 6] = -6
W2[4, 6] = 10
W2[5, 6] = -10
W2[3, 7] = -6
W2[4, 7] = -10
W2[5, 7] = -10
b2[0:8] = -22.28

# ---------- Output ----------
W3[0:4, 3] = 8
W3[4:8, 1] = 8
b3[0:6] = [6, 32, -10, 32, -10, -10]
```