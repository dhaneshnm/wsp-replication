# Asterix policy: column-locked row-dodger

## Strategy

The player starts at (row 5, column 5). The network never chooses left or right, and sticky actions only repeat its own previous action. So the player stays in column 5 for the whole episode. Each step it only chooses among staying (no-op), moving up, and moving down. It picks the target row (its own row, the one above, or the one below) with the lowest danger. Among safe rows it prefers one where treasure is about to reach column 5.

**Why one weighted sum per row is enough.** Each row (1 to 8) holds at most one entity. So a row's input contains at most one entity cell and one trail cell, and the trail shows which way that entity moves. A single linear sum over a row's enemy and trail cells can then grade the threat at column 5. In the table, "c4" means column 4, and "approaching" means moving toward column 5.

| Situation | Score S | Meaning |
|---|---|---|
| Enemy at c4 moving right, or c6 moving left | 4 | fatal next frame |
| Enemy at c5 | 4 | fatal to enter |
| Enemy at c3 or c7, approaching | 2 | medium |
| Enemy at c2 or c8 | 1 | mild |
| Enemy moving away from column 5 | 0 | safe |
| Treasure anywhere | ≤ 0 | never counts as danger |

The weights that produce these scores:
- Enemy weights by column, c2..c8: 1, 2, 4, 6, 4, 2, 1.
- Trail weights: column 4 = -2, column 5 = -4, column 6 = -2.
- The negative trail weights cancel enemies that are moving away from column 5.

## Hidden units

**Layer 1**
- **Units 0–7, D_r:** tanh(0.6·S_r − 1.2), the row danger. It gives about −0.83 for safe, −0.54 for mild, 0 for medium and 0.83 for fatal.
- **Units 8–15, P_r:** about ±1, telling whether the player is in row r. The weight is 6 on every player cell of the row, with bias −3.
- **Units 16–23, G_r:** treasure about to reach column 5 in row r. This covers treasure at c5, at c4 or c6 approaching, and more weakly at c3 or c7 approaching. Trail weights cancel treasure that is moving away.

**Layer 2** has 24 gated units, one per (player row r, action) for the actions stay, up and down. Each computes:

u = tanh(0.6·D_target − 0.3·G_target + 3·P_r − 3)

- The target row is r for stay, max(1, r−1) for up and min(8, r+1) for down.
- When the player is not in row r, the unit sits at −1, which adds the same constant to every action.
- When the player is in row r, the unit tracks the target row's danger minus its treasure attraction.
- Target rows 1 and 8 get a small extra penalty, because the edge rows leave only one escape direction.

**Output**
- Each action's logit is −25 times the sum of its 8 units. The result is 10 or more logits apart between fatal and medium, and between medium and safe. Treasure is preferred over an empty safe row by about 9.
- No-op gets a +4 tie-break so the player does not move needlessly.
- Left, right and fire are set far below the other actions.

```edits
# ---------- Layer 1: danger units D_r (cols 0..7), rows 1..8 ----------
W1[61:120:6, 0] = [0,0,0.6,1.2,2.4,3.6,2.4,1.2,0.6,0]
W1[64:120:6, 0] = [0,0,0,0,-1.2,-2.4,-1.2,0,0,0]
W1[121:180:6, 1] = [0,0,0.6,1.2,2.4,3.6,2.4,1.2,0.6,0]
W1[124:180:6, 1] = [0,0,0,0,-1.2,-2.4,-1.2,0,0,0]
W1[181:240:6, 2] = [0,0,0.6,1.2,2.4,3.6,2.4,1.2,0.6,0]
W1[184:240:6, 2] = [0,0,0,0,-1.2,-2.4,-1.2,0,0,0]
W1[241:300:6, 3] = [0,0,0.6,1.2,2.4,3.6,2.4,1.2,0.6,0]
W1[244:300:6, 3] = [0,0,0,0,-1.2,-2.4,-1.2,0,0,0]
W1[301:360:6, 4] = [0,0,0.6,1.2,2.4,3.6,2.4,1.2,0.6,0]
W1[304:360:6, 4] = [0,0,0,0,-1.2,-2.4,-1.2,0,0,0]
W1[361:420:6, 5] = [0,0,0.6,1.2,2.4,3.6,2.4,1.2,0.6,0]
W1[364:420:6, 5] = [0,0,0,0,-1.2,-2.4,-1.2,0,0,0]
W1[421:480:6, 6] = [0,0,0.6,1.2,2.4,3.6,2.4,1.2,0.6,0]
W1[424:480:6, 6] = [0,0,0,0,-1.2,-2.4,-1.2,0,0,0]
W1[481:540:6, 7] = [0,0,0.6,1.2,2.4,3.6,2.4,1.2,0.6,0]
W1[484:540:6, 7] = [0,0,0,0,-1.2,-2.4,-1.2,0,0,0]
b1[0:8] = -1.2
# ---------- Layer 1: player-row units P_r (cols 8..15) ----------
W1[60:120:6, 8] = 6
W1[120:180:6, 9] = 6
W1[180:240:6, 10] = 6
W1[240:300:6, 11] = 6
W1[300:360:6, 12] = 6
W1[360:420:6, 13] = 6
W1[420:480:6, 14] = 6
W1[480:540:6, 15] = 6
b1[8:16] = -3
# ---------- Layer 1: gold-arrival units G_r (cols 16..23) ----------
W1[62:120:6, 16] = [0,0,0,1,2,3,2,1,0,0]
W1[64:120:6, 16] = [0,0,0,0,-1,-2,-1,0,0,0]
W1[122:180:6, 17] = [0,0,0,1,2,3,2,1,0,0]
W1[124:180:6, 17] = [0,0,0,0,-1,-2,-1,0,0,0]
W1[182:240:6, 18] = [0,0,0,1,2,3,2,1,0,0]
W1[184:240:6, 18] = [0,0,0,0,-1,-2,-1,0,0,0]
W1[242:300:6, 19] = [0,0,0,1,2,3,2,1,0,0]
W1[244:300:6, 19] = [0,0,0,0,-1,-2,-1,0,0,0]
W1[302:360:6, 20] = [0,0,0,1,2,3,2,1,0,0]
W1[304:360:6, 20] = [0,0,0,0,-1,-2,-1,0,0,0]
W1[362:420:6, 21] = [0,0,0,1,2,3,2,1,0,0]
W1[364:420:6, 21] = [0,0,0,0,-1,-2,-1,0,0,0]
W1[422:480:6, 22] = [0,0,0,1,2,3,2,1,0,0]
W1[424:480:6, 22] = [0,0,0,0,-1,-2,-1,0,0,0]
W1[482:540:6, 23] = [0,0,0,1,2,3,2,1,0,0]
W1[484:540:6, 23] = [0,0,0,0,-1,-2,-1,0,0,0]
b1[16:24] = -1
# ---------- Layer 2: gated (player row, action) units ----------
# r=1: k0 stay t1, k1 up t1, k2 down t2
W2[8, 0:3] = 3
W2[0, 0] = 0.6
W2[16, 0] = -0.3
W2[0, 1] = 0.6
W2[16, 1] = -0.3
W2[1, 2] = 0.6
W2[17, 2] = -0.3
# r=2: k3 t2, k4 t1, k5 t3
W2[9, 3:6] = 3
W2[1, 3] = 0.6
W2[17, 3] = -0.3
W2[0, 4] = 0.6
W2[16, 4] = -0.3
W2[2, 5] = 0.6
W2[18, 5] = -0.3
# r=3: k6 t3, k7 t2, k8 t4
W2[10, 6:9] = 3
W2[2, 6] = 0.6
W2[18, 6] = -0.3
W2[1, 7] = 0.6
W2[17, 7] = -0.3
W2[3, 8] = 0.6
W2[19, 8] = -0.3
# r=4: k9 t4, k10 t3, k11 t5
W2[11, 9:12] = 3
W2[3, 9] = 0.6
W2[19, 9] = -0.3
W2[2, 10] = 0.6
W2[18, 10] = -0.3
W2[4, 11] = 0.6
W2[20, 11] = -0.3
# r=5: k12 t5, k13 t4, k14 t6
W2[12, 12:15] = 3
W2[4, 12] = 0.6
W2[20, 12] = -0.3
W2[3, 13] = 0.6
W2[19, 13] = -0.3
W2[5, 14] = 0.6
W2[21, 14] = -0.3
# r=6: k15 t6, k16 t5, k17 t7
W2[13, 15:18] = 3
W2[5, 15] = 0.6
W2[21, 15] = -0.3
W2[4, 16] = 0.6
W2[20, 16] = -0.3
W2[6, 17] = 0.6
W2[22, 17] = -0.3
# r=7: k18 t7, k19 t6, k20 t8
W2[14, 18:21] = 3
W2[6, 18] = 0.6
W2[22, 18] = -0.3
W2[5, 19] = 0.6
W2[21, 19] = -0.3
W2[7, 20] = 0.6
W2[23, 20] = -0.3
# r=8: k21 t8, k22 t7, k23 t8
W2[15, 21:24] = 3
W2[7, 21] = 0.6
W2[23, 21] = -0.3
W2[6, 22] = 0.6
W2[22, 22] = -0.3
W2[7, 23] = 0.6
W2[23, 23] = -0.3
b2[0:24] = -3
# small extra danger for edge target rows (1 and 8)
b2[0] = -2.92
b2[1] = -2.92
b2[4] = -2.92
b2[20] = -2.92
b2[21] = -2.92
b2[23] = -2.92
# ---------- Output ----------
W3[0:24:3, 0] = -25
W3[1:24:3, 2] = -25
W3[2:24:3, 4] = -25
b3[0] = -171
b3[2] = -175
b3[4] = -175
b3[1] = -60
b3[3] = -60
b3[5] = -60
```