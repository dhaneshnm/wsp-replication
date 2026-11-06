## Strategy

The policy predicts the column where the ball will be when it reaches row 8, the last row before the bottom. It moves the paddle toward that column and then waits there. Because the paddle usually arrives early, it has spare steps, so it is robust to sticky actions.

The model behind the prediction:
- **Wall bounces.** The ball's column with its wall "stalls" behaves like a coordinate that repeats every 20 steps. Fold the position with fold(u) = u mod 20, then use 19 − m if m ≥ 10.
- **Ball moving down** at (x, y) with horizontal direction dx. The ball is caught if the paddle is under the ball's column at row 8. That column is exactly fold(x + dx·(8−y)).
- **Ball moving up.** The paddle heads for fold(x + dx·T(y)), where T is an estimated return time. For rows 4 and below, T assumes the ball turns at a brick in row 2 (T = y+3). For rows 0–3 it uses fixed values (9, 10, 9, 8). For y ≥ 4 this target stays fixed while the ball climbs. When the ball turns, the exact downward target is always reachable with at least 3 steps to spare.

## Hidden layer 1 (10 units used)

- **Units 0–7: direction-specific comparisons.** For each of the 4 ball directions there is a lookup table L_d(ball cell), stored in the ball-channel weights. A pair of units computes:
  - R_d = tanh(5(L_d − p − 0.5)): the target is right of the paddle.
  - Lf_d = tanh(5(p − L_d − 0.5)): the target is left of the paddle.
  - The paddle column p enters through the paddle-channel weights.
  - The directions are down-right (units 0,1), down-left (2,3), up-right (4,5) and up-left (6,7).
- **Unit 8 (H): is the ball moving right?** It computes 8·(ball_x − trail_x ± 0.5 at the walls). The wall correction gives the right answer when the ball stalls at a side wall (ball and trail in the same column).
- **Unit 9 (V): is the ball moving down?** It computes 8·(ball_y − trail_y + 0.5 for rows ≤ 7, − 0.5 at row 8). This classifies the one-frame horizontal trails correctly in most cases:
  - a bounce off the top wall or a brick counts as down;
  - a bounce off the paddle counts as up.

## Hidden layer 2 (8 units used)

Each unit is an AND of three signals: one comparison unit, plus the matching H and V signs. The unit fires only for the ball's actual direction. Even-numbered units mean "move right"; odd-numbered units mean "move left".

## Output

- Right logit: 15 × (sum of the "right" units) + 45, which is +15 if any fires and −15 otherwise.
- Left logit: built the same way from the "left" units.
- No-op, up, down and fire stay at 0, so the paddle waits when it is already at the target.

```edits
# ---------- Layer 1: lookup tables (ball channel), unscaled first ----------
# Unit 0 and 1: down-right table L_DR
W1[3:60:6, 0] = [8,9,9,8,7,6,5,4,3,2]
W1[63:120:6, 0] = [7,8,9,9,8,7,6,5,4,3]
W1[123:180:6, 0] = [6,7,8,9,9,8,7,6,5,4]
W1[183:240:6, 0] = [5,6,7,8,9,9,8,7,6,5]
W1[243:300:6, 0] = [4,5,6,7,8,9,9,8,7,6]
W1[303:360:6, 0] = [3,4,5,6,7,8,9,9,8,7]
W1[363:420:6, 0] = [2,3,4,5,6,7,8,9,9,8]
W1[423:480:6, 0] = [1,2,3,4,5,6,7,8,9,9]
W1[483:540:6, 0] = [0,1,2,3,4,5,6,7,8,9]
W1[3:60:6, 1] = [8,9,9,8,7,6,5,4,3,2]
W1[63:120:6, 1] = [7,8,9,9,8,7,6,5,4,3]
W1[123:180:6, 1] = [6,7,8,9,9,8,7,6,5,4]
W1[183:240:6, 1] = [5,6,7,8,9,9,8,7,6,5]
W1[243:300:6, 1] = [4,5,6,7,8,9,9,8,7,6]
W1[303:360:6, 1] = [3,4,5,6,7,8,9,9,8,7]
W1[363:420:6, 1] = [2,3,4,5,6,7,8,9,9,8]
W1[423:480:6, 1] = [1,2,3,4,5,6,7,8,9,9]
W1[483:540:6, 1] = [0,1,2,3,4,5,6,7,8,9]
# Unit 2 and 3: down-left table L_DL
W1[3:60:6, 2] = [7,6,5,4,3,2,1,0,0,1]
W1[63:120:6, 2] = [6,5,4,3,2,1,0,0,1,2]
W1[123:180:6, 2] = [5,4,3,2,1,0,0,1,2,3]
W1[183:240:6, 2] = [4,3,2,1,0,0,1,2,3,4]
W1[243:300:6, 2] = [3,2,1,0,0,1,2,3,4,5]
W1[303:360:6, 2] = [2,1,0,0,1,2,3,4,5,6]
W1[363:420:6, 2] = [1,0,0,1,2,3,4,5,6,7]
W1[423:480:6, 2] = [0,0,1,2,3,4,5,6,7,8]
W1[483:540:6, 2] = [0,1,2,3,4,5,6,7,8,9]
W1[3:60:6, 3] = [7,6,5,4,3,2,1,0,0,1]
W1[63:120:6, 3] = [6,5,4,3,2,1,0,0,1,2]
W1[123:180:6, 3] = [5,4,3,2,1,0,0,1,2,3]
W1[183:240:6, 3] = [4,3,2,1,0,0,1,2,3,4]
W1[243:300:6, 3] = [3,2,1,0,0,1,2,3,4,5]
W1[303:360:6, 3] = [2,1,0,0,1,2,3,4,5,6]
W1[363:420:6, 3] = [1,0,0,1,2,3,4,5,6,7]
W1[423:480:6, 3] = [0,0,1,2,3,4,5,6,7,8]
W1[483:540:6, 3] = [0,1,2,3,4,5,6,7,8,9]
# Unit 4 and 5: up-right table L_UR (T = 9,10,9,8,7,8,9,10,11 for rows 0..8)
W1[3:60:6, 4] = [9,9,8,7,6,5,4,3,2,1]
W1[63:120:6, 4] = [9,8,7,6,5,4,3,2,1,0]
W1[123:180:6, 4] = [9,9,8,7,6,5,4,3,2,1]
W1[183:240:6, 4] = [8,9,9,8,7,6,5,4,3,2]
W1[243:300:6, 4] = [7,8,9,9,8,7,6,5,4,3]
W1[303:360:6, 4] = [8,9,9,8,7,6,5,4,3,2]
W1[363:420:6, 4] = [9,9,8,7,6,5,4,3,2,1]
W1[423:480:6, 4] = [9,8,7,6,5,4,3,2,1,0]
W1[483:540:6, 4] = [8,7,6,5,4,3,2,1,0,0]
W1[3:60:6, 5] = [9,9,8,7,6,5,4,3,2,1]
W1[63:120:6, 5] = [9,8,7,6,5,4,3,2,1,0]
W1[123:180:6, 5] = [9,9,8,7,6,5,4,3,2,1]
W1[183:240:6, 5] = [8,9,9,8,7,6,5,4,3,2]
W1[243:300:6, 5] = [7,8,9,9,8,7,6,5,4,3]
W1[303:360:6, 5] = [8,9,9,8,7,6,5,4,3,2]
W1[363:420:6, 5] = [9,9,8,7,6,5,4,3,2,1]
W1[423:480:6, 5] = [9,8,7,6,5,4,3,2,1,0]
W1[483:540:6, 5] = [8,7,6,5,4,3,2,1,0,0]
# Unit 6 and 7: up-left table L_UL
W1[3:60:6, 6] = [8,7,6,5,4,3,2,1,0,0]
W1[63:120:6, 6] = [9,8,7,6,5,4,3,2,1,0]
W1[123:180:6, 6] = [8,7,6,5,4,3,2,1,0,0]
W1[183:240:6, 6] = [7,6,5,4,3,2,1,0,0,1]
W1[243:300:6, 6] = [6,5,4,3,2,1,0,0,1,2]
W1[303:360:6, 6] = [7,6,5,4,3,2,1,0,0,1]
W1[363:420:6, 6] = [8,7,6,5,4,3,2,1,0,0]
W1[423:480:6, 6] = [9,8,7,6,5,4,3,2,1,0]
W1[483:540:6, 6] = [9,9,8,7,6,5,4,3,2,1]
W1[3:60:6, 7] = [8,7,6,5,4,3,2,1,0,0]
W1[63:120:6, 7] = [9,8,7,6,5,4,3,2,1,0]
W1[123:180:6, 7] = [8,7,6,5,4,3,2,1,0,0]
W1[183:240:6, 7] = [7,6,5,4,3,2,1,0,0,1]
W1[243:300:6, 7] = [6,5,4,3,2,1,0,0,1,2]
W1[303:360:6, 7] = [7,6,5,4,3,2,1,0,0,1]
W1[363:420:6, 7] = [8,7,6,5,4,3,2,1,0,0]
W1[423:480:6, 7] = [9,8,7,6,5,4,3,2,1,0]
W1[483:540:6, 7] = [9,9,8,7,6,5,4,3,2,1]
# scale: R units (+5*L), Lf units (-5*L)
W1[3:600:6, 0] *= 5
W1[3:600:6, 1] *= -5
W1[3:600:6, 2] *= 5
W1[3:600:6, 3] *= -5
W1[3:600:6, 4] *= 5
W1[3:600:6, 5] *= -5
W1[3:600:6, 6] *= 5
W1[3:600:6, 7] *= -5
# paddle position terms
W1[540:600:6, 0] = [0,-5,-10,-15,-20,-25,-30,-35,-40,-45]
W1[540:600:6, 1] = [0,5,10,15,20,25,30,35,40,45]
W1[540:600:6, 2] = [0,-5,-10,-15,-20,-25,-30,-35,-40,-45]
W1[540:600:6, 3] = [0,5,10,15,20,25,30,35,40,45]
W1[540:600:6, 4] = [0,-5,-10,-15,-20,-25,-30,-35,-40,-45]
W1[540:600:6, 5] = [0,5,10,15,20,25,30,35,40,45]
W1[540:600:6, 6] = [0,-5,-10,-15,-20,-25,-30,-35,-40,-45]
W1[540:600:6, 7] = [0,5,10,15,20,25,30,35,40,45]
b1[0:8] = -2.5
# ---------- Unit 8: H (ball moving right) ----------
W1[3:600:60, 8] = 4
W1[9:600:60, 8] = 8
W1[15:600:60, 8] = 16
W1[21:600:60, 8] = 24
W1[27:600:60, 8] = 32
W1[33:600:60, 8] = 40
W1[39:600:60, 8] = 48
W1[45:600:60, 8] = 56
W1[51:600:60, 8] = 64
W1[57:600:60, 8] = 68
W1[10:600:60, 8] = -8
W1[16:600:60, 8] = -16
W1[22:600:60, 8] = -24
W1[28:600:60, 8] = -32
W1[34:600:60, 8] = -40
W1[40:600:60, 8] = -48
W1[46:600:60, 8] = -56
W1[52:600:60, 8] = -64
W1[58:600:60, 8] = -72
# ---------- Unit 9: V (ball moving down) ----------
W1[3:60:6, 9] = 4
W1[63:120:6, 9] = 12
W1[123:180:6, 9] = 20
W1[183:240:6, 9] = 28
W1[243:300:6, 9] = 36
W1[303:360:6, 9] = 44
W1[363:420:6, 9] = 52
W1[423:480:6, 9] = 60
W1[483:540:6, 9] = 60
W1[64:120:6, 9] = -8
W1[124:180:6, 9] = -16
W1[184:240:6, 9] = -24
W1[244:300:6, 9] = -32
W1[304:360:6, 9] = -40
W1[364:420:6, 9] = -48
W1[424:480:6, 9] = -56
W1[484:540:6, 9] = -64
# ---------- Layer 2: AND(comparison, H sign, V sign) ----------
W2[0,0] = 5
W2[8,0] = 5
W2[9,0] = 5
W2[1,1] = 5
W2[8,1] = 5
W2[9,1] = 5
W2[2,2] = 5
W2[8,2] = -5
W2[9,2] = 5
W2[3,3] = 5
W2[8,3] = -5
W2[9,3] = 5
W2[4,4] = 5
W2[8,4] = 5
W2[9,4] = -5
W2[5,5] = 5
W2[8,5] = 5
W2[9,5] = -5
W2[6,6] = 5
W2[8,6] = -5
W2[9,6] = -5
W2[7,7] = 5
W2[8,7] = -5
W2[9,7] = -5
b2[0:8] = -10
# ---------- Output ----------
W3[0,3] = 15
W3[2,3] = 15
W3[4,3] = 15
W3[6,3] = 15
W3[1,1] = 15
W3[3,1] = 15
W3[5,1] = 15
W3[7,1] = 15
b3[3] = 45
b3[1] = 45
```