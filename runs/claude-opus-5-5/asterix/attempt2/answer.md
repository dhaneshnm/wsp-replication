## Design

**Strategy.** The player never moves sideways. It stays in column 5, where it starts, and only moves up, down, or stays put. Entities move only horizontally, so everything that matters is whether an entity in a given row is approaching column 5 or has already passed it. Each row holds at most one entity, and a row with gold therefore contains no enemy.

At each step the policy scores three target rows: the current row (no-op), the row above (up) and the row below (down). Each target is scored as follows:
- **Immediate danger** gives a huge penalty. This means an enemy at column 5, or an enemy one step away and moving toward column 5. Staying, or entering, that row can kill the player on this frame.
- **Near danger** gives a big penalty. This is an approaching enemy 2–3 cells away.
- **Far danger** gives a small penalty. This is an approaching enemy 4–5 cells away.
- **Approaching gold** gives a bonus, because sitting in that row collects it.
- **Edge rows** (1 and 8) get a small penalty, because they leave only one escape route.
- **Small extra terms:** no-op gets a small bonus to reduce dithering. A weak bias pushes the player toward the side (above or below) that has more approaching gold.
- Left, right and fire are never chosen.

**Layer 1 (32 units).**
- **Units 0–7, P_y:** the player is in row y.
- **Units 8–15, H1_r:** immediate enemy danger at column 5 in row r. Direction is read from where the trail sits: a trail at column 3 behind an enemy at column 4 means it is moving right; a trail at column 7 behind an enemy at column 6 means it is moving left. Weights on the enemy and trail channels are tuned so that passed enemies and gold trails stay negative.
- **Units 16–23, H2_r:** an approaching enemy in row r, in three levels. An enemy 2–3 cells away gives about +1. One 4–5 cells away gives about −0.46. A passed enemy, or no enemy, gives −1. The trail weights are V-shaped so that the enemy-plus-trail sum separates approaching enemies from passed ones.
- **Units 24–31, G_r:** gold in row r approaching column 5 (or already at column 5).

**Layer 2 (32 units).**
- **Units 0–23, one per (player row y, action):** each is an AND gate. It sees P_y plus the danger and gold features of the target row (y, y−1 or y+1, clamped to rows 1–8). If the player is not in row y it saturates at −1, which adds the same constant to every action and so cancels out. If the player is in row y it reads about +1 for immediate danger, +0.44 for near danger, −0.46 for a neutral row and −0.99 for a gold row.
- **Units 24–31, per row y:** the sign of (approaching gold above − approaching gold below), gated the same way.

**Output.** Each of the three action logits is −6 × its gated badness unit. The gold-direction units add ±1 to up/down. Left, right and fire sit about 60 logits below.

```edits
# ---------- Layer 1 ----------
# P_y units 0..7 (player in row y)
W1[60:120:6, 0] = 6
W1[120:180:6, 1] = 6
W1[180:240:6, 2] = 6
W1[240:300:6, 3] = 6
W1[300:360:6, 4] = 6
W1[360:420:6, 5] = 6
W1[420:480:6, 6] = 6
W1[480:540:6, 7] = 6
b1[0:8] = -3
# H1_r units 8..15 (immediate danger at column 5)
W1[61:120:6, 8] = [-12,-12,-12,-12,6,18,6,-12,-12,-12]
W1[64:120:6, 8] = [0,0,0,6,0,-12,0,6,0,0]
W1[121:180:6, 9] = [-12,-12,-12,-12,6,18,6,-12,-12,-12]
W1[124:180:6, 9] = [0,0,0,6,0,-12,0,6,0,0]
W1[181:240:6, 10] = [-12,-12,-12,-12,6,18,6,-12,-12,-12]
W1[184:240:6, 10] = [0,0,0,6,0,-12,0,6,0,0]
W1[241:300:6, 11] = [-12,-12,-12,-12,6,18,6,-12,-12,-12]
W1[244:300:6, 11] = [0,0,0,6,0,-12,0,6,0,0]
W1[301:360:6, 12] = [-12,-12,-12,-12,6,18,6,-12,-12,-12]
W1[304:360:6, 12] = [0,0,0,6,0,-12,0,6,0,0]
W1[361:420:6, 13] = [-12,-12,-12,-12,6,18,6,-12,-12,-12]
W1[364:420:6, 13] = [0,0,0,6,0,-12,0,6,0,0]
W1[421:480:6, 14] = [-12,-12,-12,-12,6,18,6,-12,-12,-12]
W1[424:480:6, 14] = [0,0,0,6,0,-12,0,6,0,0]
W1[481:540:6, 15] = [-12,-12,-12,-12,6,18,6,-12,-12,-12]
W1[484:540:6, 15] = [0,0,0,6,0,-12,0,6,0,0]
b1[8:16] = -9
# H2_r units 16..23 (approaching enemy: near / far / none)
W1[61:120:6, 16] = [3.5,3.5,11,15,17,23,17,11,7,3.5]
W1[64:120:6, 16] = [0,-4,-8,-12,-16,-16,-12,-8,-4,0]
W1[121:180:6, 17] = [3.5,3.5,11,15,17,23,17,11,7,3.5]
W1[124:180:6, 17] = [0,-4,-8,-12,-16,-16,-12,-8,-4,0]
W1[181:240:6, 18] = [3.5,3.5,11,15,17,23,17,11,7,3.5]
W1[184:240:6, 18] = [0,-4,-8,-12,-16,-16,-12,-8,-4,0]
W1[241:300:6, 19] = [3.5,3.5,11,15,17,23,17,11,7,3.5]
W1[244:300:6, 19] = [0,-4,-8,-12,-16,-16,-12,-8,-4,0]
W1[301:360:6, 20] = [3.5,3.5,11,15,17,23,17,11,7,3.5]
W1[304:360:6, 20] = [0,-4,-8,-12,-16,-16,-12,-8,-4,0]
W1[361:420:6, 21] = [3.5,3.5,11,15,17,23,17,11,7,3.5]
W1[364:420:6, 21] = [0,-4,-8,-12,-16,-16,-12,-8,-4,0]
W1[421:480:6, 22] = [3.5,3.5,11,15,17,23,17,11,7,3.5]
W1[424:480:6, 22] = [0,-4,-8,-12,-16,-16,-12,-8,-4,0]
W1[481:540:6, 23] = [3.5,3.5,11,15,17,23,17,11,7,3.5]
W1[484:540:6, 23] = [0,-4,-8,-12,-16,-16,-12,-8,-4,0]
b1[16:24] = -4
# G_r units 24..31 (gold approaching column 5)
W1[62:120:6, 24] = [7,7,13,19,25,31,19,13,7,7]
W1[64:120:6, 24] = [0,-6,-12,-18,-24,-24,-18,-12,-6,0]
W1[122:180:6, 25] = [7,7,13,19,25,31,19,13,7,7]
W1[124:180:6, 25] = [0,-6,-12,-18,-24,-24,-18,-12,-6,0]
W1[182:240:6, 26] = [7,7,13,19,25,31,19,13,7,7]
W1[184:240:6, 26] = [0,-6,-12,-18,-24,-24,-18,-12,-6,0]
W1[242:300:6, 27] = [7,7,13,19,25,31,19,13,7,7]
W1[244:300:6, 27] = [0,-6,-12,-18,-24,-24,-18,-12,-6,0]
W1[302:360:6, 28] = [7,7,13,19,25,31,19,13,7,7]
W1[304:360:6, 28] = [0,-6,-12,-18,-24,-24,-18,-12,-6,0]
W1[362:420:6, 29] = [7,7,13,19,25,31,19,13,7,7]
W1[364:420:6, 29] = [0,-6,-12,-18,-24,-24,-18,-12,-6,0]
W1[422:480:6, 30] = [7,7,13,19,25,31,19,13,7,7]
W1[424:480:6, 30] = [0,-6,-12,-18,-24,-24,-18,-12,-6,0]
W1[482:540:6, 31] = [7,7,13,19,25,31,19,13,7,7]
W1[484:540:6, 31] = [0,-6,-12,-18,-24,-24,-18,-12,-6,0]
b1[24:32] = -4

# ---------- Layer 2 ----------
# player-row gates: stay_y=y-1, up_y=7+y, down_y=15+y, goldDir_y=23+y
W2[0, 0:24:8] = 6
W2[1, 1:24:8] = 6
W2[2, 2:24:8] = 6
W2[3, 3:24:8] = 6
W2[4, 4:24:8] = 6
W2[5, 5:24:8] = 6
W2[6, 6:24:8] = 6
W2[7, 7:24:8] = 6
W2[0, 24] = 10
W2[1, 25] = 10
W2[2, 26] = 10
W2[3, 27] = 10
W2[4, 28] = 10
W2[5, 29] = 10
W2[6, 30] = 10
W2[7, 31] = 10
# H1_r -> units whose target row is r  (weight 2)
W2[8, 0] = 2
W2[8, 8] = 2
W2[8, 9] = 2
W2[9, 1] = 2
W2[9, 10] = 2
W2[9, 16] = 2
W2[10, 2] = 2
W2[10, 11] = 2
W2[10, 17] = 2
W2[11, 3] = 2
W2[11, 12] = 2
W2[11, 18] = 2
W2[12, 4] = 2
W2[12, 13] = 2
W2[12, 19] = 2
W2[13, 5] = 2
W2[13, 14] = 2
W2[13, 20] = 2
W2[14, 6] = 2
W2[14, 15] = 2
W2[14, 21] = 2
W2[15, 7] = 2
W2[15, 22] = 2
W2[15, 23] = 2
# H2_r -> same targets (weight 0.5)
W2[16, 0] = 0.5
W2[16, 8] = 0.5
W2[16, 9] = 0.5
W2[17, 1] = 0.5
W2[17, 10] = 0.5
W2[17, 16] = 0.5
W2[18, 2] = 0.5
W2[18, 11] = 0.5
W2[18, 17] = 0.5
W2[19, 3] = 0.5
W2[19, 12] = 0.5
W2[19, 18] = 0.5
W2[20, 4] = 0.5
W2[20, 13] = 0.5
W2[20, 19] = 0.5
W2[21, 5] = 0.5
W2[21, 14] = 0.5
W2[21, 20] = 0.5
W2[22, 6] = 0.5
W2[22, 15] = 0.5
W2[22, 21] = 0.5
W2[23, 7] = 0.5
W2[23, 22] = 0.5
W2[23, 23] = 0.5
# G_r -> same targets (weight -1)
W2[24, 0] = -1
W2[24, 8] = -1
W2[24, 9] = -1
W2[25, 1] = -1
W2[25, 10] = -1
W2[25, 16] = -1
W2[26, 2] = -1
W2[26, 11] = -1
W2[26, 17] = -1
W2[27, 3] = -1
W2[27, 12] = -1
W2[27, 18] = -1
W2[28, 4] = -1
W2[28, 13] = -1
W2[28, 19] = -1
W2[29, 5] = -1
W2[29, 14] = -1
W2[29, 20] = -1
W2[30, 6] = -1
W2[30, 15] = -1
W2[30, 21] = -1
W2[31, 7] = -1
W2[31, 22] = -1
W2[31, 23] = -1
# gold-direction units: gold above (+) minus gold below
W2[24:32, 24:32] = [[0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5], [-0.5, 0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5], [-0.5, -0.5, 0, 0.5, 0.5, 0.5, 0.5, 0.5], [-0.5, -0.5, -0.5, 0, 0.5, 0.5, 0.5, 0.5], [-0.5, -0.5, -0.5, -0.5, 0, 0.5, 0.5, 0.5], [-0.5, -0.5, -0.5, -0.5, -0.5, 0, 0.5, 0.5], [-0.5, -0.5, -0.5, -0.5, -0.5, -0.5, 0, 0.5], [-0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, 0]]
b2[0:24] = -5
b2[0] = -4.75
b2[8] = -4.75
b2[9] = -4.75
b2[7] = -4.75
b2[22] = -4.75
b2[23] = -4.75
b2[24:32] = [-13.5, -12.5, -11.5, -10.5, -9.5, -8.5, -7.5, -6.5]

# ---------- Output ----------
W3[0:8, 0] = -6
W3[8:16, 2] = -6
W3[16:24, 4] = -6
W3[24:32, 2] = 1
W3[24:32, 4] = -1
b3[0:6] = [1.5, -20, 7, -20, -7, -20]
```