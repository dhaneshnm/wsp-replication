## Design

**Strategy: predict where the ball will land and wait there.**

A few facts from the source code shape the design:

- **Catch rule.** When the ball is on row 8 moving down at column `bc`, the paddle moves first. The ball is caught if the paddle ends at `bc` (a "straight" bounce that keeps the horizontal direction) or at the ball's next column (a "reversal" bounce).
- **Horizontal motion is a fold.** The ball moves one column per step. At a wall it is clamped for one step and then reverses. So its future column after k steps is `F(c + dx·k)`, where `F(u)`: take `u mod 20`, and if the result is 10 or more, use `19 − (u mod 20)`.
- **Timing.**
  - A ball that will move down next, at row r, reaches row 8 after `8 − r` steps. "Moving down next" means it is moving down, or it is flat on a row other than 8 (after a brick or top bounce, or at reset).
  - A ball that will move up next means it is moving up, or it is flat on row 8 just after a paddle catch. Its return time is guessed by assuming it bounces at row 4, the lowest brick row. That gives `S(r) = r + 1` for r ≥ 4, and `S(r) = 9 − r` for r ≤ 3 (immediate bounce).
  - If the guess is wrong, the error is at most `2·(4 − h)` columns, where h is the actual bounce row. The descent phase then has `9 − h` moves to fix it, which is always enough.
- **Where to aim.** The paddle aims at the exact landing column `x8`. Standing there and doing a no-op gives a straight catch, so the horizontal direction is preserved and the predictions stay consistent.

**Layer 1 (10 units).** Each unit is a single linear threshold over the one-hot inputs (ball cell, trail cell, paddle column).

- **Units 0–7: comparators.** For each target table T in {D+, D−, U+, U−} there are two units:
  - `tanh(10·(T(ball cell) − paddle − 0.5))` fires when the paddle should move right.
  - the mirrored unit fires when it should move left.
  - D± are the descent tables and U± the ascent tables (± is the horizontal direction).
- **Unit 8: X, horizontal direction.** It computes `a(bc) − lc ≥ 1`, with `a(0) = 1`, which means "next horizontal direction is +1". Wall cases are absorbed by the fold, so no extra unit is needed.
- **Unit 9: V, vertical class.** It computes `lr − a'(br) ≥ 1`, with `a'(8) = 7`, which means "the ball moves up next". This also classifies the row-8 post-catch state as up.

**Layer 2 (8 units).** Each unit is an AND of one comparator with its class condition (X sign and V sign): `tanh(5·(C ± X ± V − 2))`.

**Outputs.**
- The "right" logit is ±20, depending on whether any right-AND unit is active; "left" works the same way.
- No-op and the three no-op-equivalent actions have logit 0.
- So the policy is near-deterministic. When the paddle is already on target it no-ops, which also makes sticky repeats harmless while waiting.

```edits
# ---------- Layer 1 ----------
# unit 0: R_D+ (descent, dx=+1), unit 1: L_D+
W1[3:600:6, 0] = [8,9,9,8,7,6,5,4,3,2,
 7,8,9,9,8,7,6,5,4,3,
 6,7,8,9,9,8,7,6,5,4,
 5,6,7,8,9,9,8,7,6,5,
 4,5,6,7,8,9,9,8,7,6,
 3,4,5,6,7,8,9,9,8,7,
 2,3,4,5,6,7,8,9,9,8,
 1,2,3,4,5,6,7,8,9,9,
 0,1,2,3,4,5,6,7,8,9,
 0,1,2,3,4,5,6,7,8,9]
W1[540:600:6, 0] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[:, 0] *= 10
W1[3:600:6, 1] = [8,9,9,8,7,6,5,4,3,2,
 7,8,9,9,8,7,6,5,4,3,
 6,7,8,9,9,8,7,6,5,4,
 5,6,7,8,9,9,8,7,6,5,
 4,5,6,7,8,9,9,8,7,6,
 3,4,5,6,7,8,9,9,8,7,
 2,3,4,5,6,7,8,9,9,8,
 1,2,3,4,5,6,7,8,9,9,
 0,1,2,3,4,5,6,7,8,9,
 0,1,2,3,4,5,6,7,8,9]
W1[540:600:6, 1] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[:, 1] *= -10
# unit 2: R_D- (descent, dx=-1), unit 3: L_D-
W1[3:600:6, 2] = [7,6,5,4,3,2,1,0,0,1,
 6,5,4,3,2,1,0,0,1,2,
 5,4,3,2,1,0,0,1,2,3,
 4,3,2,1,0,0,1,2,3,4,
 3,2,1,0,0,1,2,3,4,5,
 2,1,0,0,1,2,3,4,5,6,
 1,0,0,1,2,3,4,5,6,7,
 0,0,1,2,3,4,5,6,7,8,
 0,1,2,3,4,5,6,7,8,9,
 0,1,2,3,4,5,6,7,8,9]
W1[540:600:6, 2] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[:, 2] *= 10
W1[3:600:6, 3] = [7,6,5,4,3,2,1,0,0,1,
 6,5,4,3,2,1,0,0,1,2,
 5,4,3,2,1,0,0,1,2,3,
 4,3,2,1,0,0,1,2,3,4,
 3,2,1,0,0,1,2,3,4,5,
 2,1,0,0,1,2,3,4,5,6,
 1,0,0,1,2,3,4,5,6,7,
 0,0,1,2,3,4,5,6,7,8,
 0,1,2,3,4,5,6,7,8,9,
 0,1,2,3,4,5,6,7,8,9]
W1[540:600:6, 3] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[:, 3] *= -10
# unit 4: R_U+ (ascent guess, dx=+1), unit 5: L_U+
W1[3:600:6, 4] = [9,9,8,7,6,5,4,3,2,1,
 8,9,9,8,7,6,5,4,3,2,
 7,8,9,9,8,7,6,5,4,3,
 6,7,8,9,9,8,7,6,5,4,
 5,6,7,8,9,9,8,7,6,5,
 6,7,8,9,9,8,7,6,5,4,
 7,8,9,9,8,7,6,5,4,3,
 8,9,9,8,7,6,5,4,3,2,
 9,9,8,7,6,5,4,3,2,1,
 9,9,8,7,6,5,4,3,2,1]
W1[540:600:6, 4] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[:, 4] *= 10
W1[3:600:6, 5] = [9,9,8,7,6,5,4,3,2,1,
 8,9,9,8,7,6,5,4,3,2,
 7,8,9,9,8,7,6,5,4,3,
 6,7,8,9,9,8,7,6,5,4,
 5,6,7,8,9,9,8,7,6,5,
 6,7,8,9,9,8,7,6,5,4,
 7,8,9,9,8,7,6,5,4,3,
 8,9,9,8,7,6,5,4,3,2,
 9,9,8,7,6,5,4,3,2,1,
 9,9,8,7,6,5,4,3,2,1]
W1[540:600:6, 5] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[:, 5] *= -10
# unit 6: R_U- (ascent guess, dx=-1), unit 7: L_U-
W1[3:600:6, 6] = [8,7,6,5,4,3,2,1,0,0,
 7,6,5,4,3,2,1,0,0,1,
 6,5,4,3,2,1,0,0,1,2,
 5,4,3,2,1,0,0,1,2,3,
 4,3,2,1,0,0,1,2,3,4,
 5,4,3,2,1,0,0,1,2,3,
 6,5,4,3,2,1,0,0,1,2,
 7,6,5,4,3,2,1,0,0,1,
 8,7,6,5,4,3,2,1,0,0,
 8,7,6,5,4,3,2,1,0,0]
W1[540:600:6, 6] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[:, 6] *= 10
W1[3:600:6, 7] = [8,7,6,5,4,3,2,1,0,0,
 7,6,5,4,3,2,1,0,0,1,
 6,5,4,3,2,1,0,0,1,2,
 5,4,3,2,1,0,0,1,2,3,
 4,3,2,1,0,0,1,2,3,4,
 5,4,3,2,1,0,0,1,2,3,
 6,5,4,3,2,1,0,0,1,2,
 7,6,5,4,3,2,1,0,0,1,
 8,7,6,5,4,3,2,1,0,0,
 8,7,6,5,4,3,2,1,0,0]
W1[540:600:6, 7] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[:, 7] *= -10
b1[0:8] = -5
# unit 8: X = next horizontal direction is +1  (ball col weight 10*a(c), a(0)=1; trail col weight -10c)
W1[3:600:60, 8] = 10
W1[9:600:60, 8] = 10
W1[15:600:60, 8] = 20
W1[21:600:60, 8] = 30
W1[27:600:60, 8] = 40
W1[33:600:60, 8] = 50
W1[39:600:60, 8] = 60
W1[45:600:60, 8] = 70
W1[51:600:60, 8] = 80
W1[57:600:60, 8] = 90
W1[4:600:60, 8] = 0
W1[10:600:60, 8] = -10
W1[16:600:60, 8] = -20
W1[22:600:60, 8] = -30
W1[28:600:60, 8] = -40
W1[34:600:60, 8] = -50
W1[40:600:60, 8] = -60
W1[46:600:60, 8] = -70
W1[52:600:60, 8] = -80
W1[58:600:60, 8] = -90
b1[8] = -5
# unit 9: V = ball moves up next (trail row weight 10r; ball row weight -10*a'(r), a'(8)=7)
W1[3:60:6, 9] = 0
W1[63:120:6, 9] = -10
W1[123:180:6, 9] = -20
W1[183:240:6, 9] = -30
W1[243:300:6, 9] = -40
W1[303:360:6, 9] = -50
W1[363:420:6, 9] = -60
W1[423:480:6, 9] = -70
W1[483:540:6, 9] = -70
W1[543:600:6, 9] = -90
W1[4:60:6, 9] = 0
W1[64:120:6, 9] = 10
W1[124:180:6, 9] = 20
W1[184:240:6, 9] = 30
W1[244:300:6, 9] = 40
W1[304:360:6, 9] = 50
W1[364:420:6, 9] = 60
W1[424:480:6, 9] = 70
W1[484:540:6, 9] = 80
W1[544:600:6, 9] = 90
b1[9] = -5
# ---------- Layer 2: AND(comparator, X sign, V sign) ----------
W2[0, 0] = 5
W2[8, 0] = 5
W2[9, 0] = -5
W2[1, 1] = 5
W2[8, 1] = 5
W2[9, 1] = -5
W2[2, 2] = 5
W2[8, 2] = -5
W2[9, 2] = -5
W2[3, 3] = 5
W2[8, 3] = -5
W2[9, 3] = -5
W2[4, 4] = 5
W2[8, 4] = 5
W2[9, 4] = 5
W2[5, 5] = 5
W2[8, 5] = 5
W2[9, 5] = 5
W2[6, 6] = 5
W2[8, 6] = -5
W2[9, 6] = 5
W2[7, 7] = 5
W2[8, 7] = -5
W2[9, 7] = 5
b2[0:8] = -10
# ---------- Output ----------
W3[0:8:2, 3] = 20
W3[1:8:2, 1] = 20
b3[3] = 60
b3[1] = 60
```