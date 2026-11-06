# Hand-written policy network for MinAtar Asterix: stay in column 5, dodge vertically, chase gold vertically

## Strategy

The player never moves left or right. It stays in column 5, where it starts, and only moves up, down, or stays put. Every treasure crosses the whole board, so every treasure passes column 5; the agent only has to be in the right row when it arrives. Enemies only move horizontally, so dodging them is a purely vertical decision. Each row holds at most one entity, and its trail cell shows its direction. That makes "is this row dangerous / rewarding" a simple linear threshold test per row.

## Layer 1: 32 per-row detectors

Each unit is saturated to about ±1.

- **Units 0–7, P_y**: the player is in row y (y = 1..8).
- **Units 8–15, T_r**: an enemy in row r will reach column 5 within 2 moves. This means an enemy at column 3 or 4 moving right, or at column 6 or 7 moving left. Enemy and trail weights are chosen so a threat sums to 2 and anything else sums to at most 1.
- **Units 16–23, Bk_r**: row r is unsafe to enter. This means an enemy is at column 5, or one move away and approaching.
- **Units 24–31, G_r**: row r holds treasure that is approaching column 5 or is at column 5. The trail weights grow with distance from the centre, and the treasure weights shrink, so:
  - approaching treasure scores +1;
  - receding treasure scores −1 or 0;
  - any enemy in the row adds −6, which cancels its trail.

## Layer 2: 32 units gated by the player's row

Each unit gets +10·P_y from its own row's player unit. When the player is not in that row, the unit sits at exactly −1, a constant that the output biases cancel. When the player is in that row, the unit computes its own value.

- **S_y (units 0–7)**: about +1 if the player's row is threatened (T_y), about −1 if it holds approaching treasure (G_y), and 0 otherwise.
- **U_y (units 8–15)**: "up is blocked", meaning Bk of row y−1. At row 1 it is always on, because moving up there does nothing.
- **D_y (units 16–23)**: "down is blocked", meaning Bk of row y+1. At row 8 it is always on.
- **V_y (units 24–31)**: treasure direction, computed as tanh of a sum over rows with approaching treasure.
  - Each treasure above the player adds weight; each treasure below subtracts.
  - The weight shrinks with distance (2, 1.6, 1.3, 1.0, ...), so nearer treasure counts more.
  - A small bias pulls the player toward the middle rows, which keep two escape directions open.

## Outputs

- **Stay** = −16·s, where s is the S value for the player's row.
- **Up** = −24·[up blocked] + 8·v − 4, where v is the V value.
- **Down** = −24·[down blocked] − 8·v − 4.
- **Left, right and fire** are fixed at −30.

These weights give a clear order of priorities:

1. **Never enter a blocked row.** A blocked move costs 24, more than any treasure pull can offset.
2. **Leave a threatened row.** A threat costs staying 16, so moving to a free neighbour wins even against treasure pulling the other way. If both neighbours are blocked, staying put is the least bad option.
3. **Wait for treasure in your own row.** This gives staying a bonus of 16.
4. **Move toward the nearest treasure**, with a pull of up to 8.
5. **Otherwise stay put.** Any move starts 4 behind staying.

```edits
# ---------------- Layer 1 ----------------
# P_y units 0..7 : player in row y (any column)
W1[60:120:6, 0] = 10
W1[120:180:6, 1] = 10
W1[180:240:6, 2] = 10
W1[240:300:6, 3] = 10
W1[300:360:6, 4] = 10
W1[360:420:6, 5] = 10
W1[420:480:6, 6] = 10
W1[480:540:6, 7] = 10
b1[0:8] = -5
# T_r units 8..15 : enemy threat (d1/d2 approaching) in row r
W1[61:120:6, 8] = [0, 0, 0, 6, 6, 0, 6, 6, 0, 0]
W1[64:120:6, 8] = [0, 0, 6, 6, -6, -6, -6, 6, 6, 0]
W1[121:180:6, 9] = [0, 0, 0, 6, 6, 0, 6, 6, 0, 0]
W1[124:180:6, 9] = [0, 0, 6, 6, -6, -6, -6, 6, 6, 0]
W1[181:240:6, 10] = [0, 0, 0, 6, 6, 0, 6, 6, 0, 0]
W1[184:240:6, 10] = [0, 0, 6, 6, -6, -6, -6, 6, 6, 0]
W1[241:300:6, 11] = [0, 0, 0, 6, 6, 0, 6, 6, 0, 0]
W1[244:300:6, 11] = [0, 0, 6, 6, -6, -6, -6, 6, 6, 0]
W1[301:360:6, 12] = [0, 0, 0, 6, 6, 0, 6, 6, 0, 0]
W1[304:360:6, 12] = [0, 0, 6, 6, -6, -6, -6, 6, 6, 0]
W1[361:420:6, 13] = [0, 0, 0, 6, 6, 0, 6, 6, 0, 0]
W1[364:420:6, 13] = [0, 0, 6, 6, -6, -6, -6, 6, 6, 0]
W1[421:480:6, 14] = [0, 0, 0, 6, 6, 0, 6, 6, 0, 0]
W1[424:480:6, 14] = [0, 0, 6, 6, -6, -6, -6, 6, 6, 0]
W1[481:540:6, 15] = [0, 0, 0, 6, 6, 0, 6, 6, 0, 0]
W1[484:540:6, 15] = [0, 0, 6, 6, -6, -6, -6, 6, 6, 0]
b1[8:16] = -9
# Bk_r units 16..23 : row r unsafe to enter (enemy at col 5 or d1 approaching)
W1[61:120:6, 16] = [0, 0, 0, 0, 6, 12, 6, 0, 0, 0]
W1[64:120:6, 16] = [0, 0, 0, 6, 0, -6, 0, 6, 0, 0]
W1[121:180:6, 17] = [0, 0, 0, 0, 6, 12, 6, 0, 0, 0]
W1[124:180:6, 17] = [0, 0, 0, 6, 0, -6, 0, 6, 0, 0]
W1[181:240:6, 18] = [0, 0, 0, 0, 6, 12, 6, 0, 0, 0]
W1[184:240:6, 18] = [0, 0, 0, 6, 0, -6, 0, 6, 0, 0]
W1[241:300:6, 19] = [0, 0, 0, 0, 6, 12, 6, 0, 0, 0]
W1[244:300:6, 19] = [0, 0, 0, 6, 0, -6, 0, 6, 0, 0]
W1[301:360:6, 20] = [0, 0, 0, 0, 6, 12, 6, 0, 0, 0]
W1[304:360:6, 20] = [0, 0, 0, 6, 0, -6, 0, 6, 0, 0]
W1[361:420:6, 21] = [0, 0, 0, 0, 6, 12, 6, 0, 0, 0]
W1[364:420:6, 21] = [0, 0, 0, 6, 0, -6, 0, 6, 0, 0]
W1[421:480:6, 22] = [0, 0, 0, 0, 6, 12, 6, 0, 0, 0]
W1[424:480:6, 22] = [0, 0, 0, 6, 0, -6, 0, 6, 0, 0]
W1[481:540:6, 23] = [0, 0, 0, 0, 6, 12, 6, 0, 0, 0]
W1[484:540:6, 23] = [0, 0, 0, 6, 0, -6, 0, 6, 0, 0]
b1[16:24] = -9
# G_r units 24..31 : approaching treasure in row r
W1[62:120:6, 24] = [-24, -18, -12, -6, 0, 9, -6, -12, -18, -24]
W1[64:120:6, 24] = [24, 18, 12, 6, 0, 0, 6, 12, 18, 24]
W1[61:120:6, 24] = -36
W1[122:180:6, 25] = [-24, -18, -12, -6, 0, 9, -6, -12, -18, -24]
W1[124:180:6, 25] = [24, 18, 12, 6, 0, 0, 6, 12, 18, 24]
W1[121:180:6, 25] = -36
W1[182:240:6, 26] = [-24, -18, -12, -6, 0, 9, -6, -12, -18, -24]
W1[184:240:6, 26] = [24, 18, 12, 6, 0, 0, 6, 12, 18, 24]
W1[181:240:6, 26] = -36
W1[242:300:6, 27] = [-24, -18, -12, -6, 0, 9, -6, -12, -18, -24]
W1[244:300:6, 27] = [24, 18, 12, 6, 0, 0, 6, 12, 18, 24]
W1[241:300:6, 27] = -36
W1[302:360:6, 28] = [-24, -18, -12, -6, 0, 9, -6, -12, -18, -24]
W1[304:360:6, 28] = [24, 18, 12, 6, 0, 0, 6, 12, 18, 24]
W1[301:360:6, 28] = -36
W1[362:420:6, 29] = [-24, -18, -12, -6, 0, 9, -6, -12, -18, -24]
W1[364:420:6, 29] = [24, 18, 12, 6, 0, 0, 6, 12, 18, 24]
W1[361:420:6, 29] = -36
W1[422:480:6, 30] = [-24, -18, -12, -6, 0, 9, -6, -12, -18, -24]
W1[424:480:6, 30] = [24, 18, 12, 6, 0, 0, 6, 12, 18, 24]
W1[421:480:6, 30] = -36
W1[482:540:6, 31] = [-24, -18, -12, -6, 0, 9, -6, -12, -18, -24]
W1[484:540:6, 31] = [24, 18, 12, 6, 0, 0, 6, 12, 18, 24]
W1[481:540:6, 31] = -36
b1[24:32] = -3

# ---------------- Layer 2 ----------------
# S_y (cols 0..7): gate P_y, +T_y, -G_y
W2[0, 0] = 10
W2[1, 1] = 10
W2[2, 2] = 10
W2[3, 3] = 10
W2[4, 4] = 10
W2[5, 5] = 10
W2[6, 6] = 10
W2[7, 7] = 10
W2[8, 0] = 1.5
W2[9, 1] = 1.5
W2[10, 2] = 1.5
W2[11, 3] = 1.5
W2[12, 4] = 1.5
W2[13, 5] = 1.5
W2[14, 6] = 1.5
W2[15, 7] = 1.5
W2[24, 0] = -1.5
W2[25, 1] = -1.5
W2[26, 2] = -1.5
W2[27, 3] = -1.5
W2[28, 4] = -1.5
W2[29, 5] = -1.5
W2[30, 6] = -1.5
W2[31, 7] = -1.5
b2[0:8] = -10
# U_y (cols 8..15): up blocked
W2[0, 8] = 10
W2[1, 9] = 10
W2[16, 9] = 3
W2[2, 10] = 10
W2[17, 10] = 3
W2[3, 11] = 10
W2[18, 11] = 3
W2[4, 12] = 10
W2[19, 12] = 3
W2[5, 13] = 10
W2[20, 13] = 3
W2[6, 14] = 10
W2[21, 14] = 3
W2[7, 15] = 10
W2[22, 15] = 3
b2[8] = -7
b2[9:16] = -10
# D_y (cols 16..23): down blocked
W2[0, 16] = 10
W2[17, 16] = 3
W2[1, 17] = 10
W2[18, 17] = 3
W2[2, 18] = 10
W2[19, 18] = 3
W2[3, 19] = 10
W2[20, 19] = 3
W2[4, 20] = 10
W2[21, 20] = 3
W2[5, 21] = 10
W2[22, 21] = 3
W2[6, 22] = 10
W2[23, 22] = 3
W2[7, 23] = 10
b2[16:23] = -10
b2[23] = -7
# V_y (cols 24..31): treasure direction (+ = above)
W2[0, 24] = 10
W2[1, 25] = 10
W2[2, 26] = 10
W2[3, 27] = 10
W2[4, 28] = 10
W2[5, 29] = 10
W2[6, 30] = 10
W2[7, 31] = 10
W2[24:32, 24] = [0, -1, -0.8, -0.65, -0.5, -0.4, -0.3, -0.25]
W2[24:32, 25] = [1, 0, -1, -0.8, -0.65, -0.5, -0.4, -0.3]
W2[24:32, 26] = [0.8, 1, 0, -1, -0.8, -0.65, -0.5, -0.4]
W2[24:32, 27] = [0.65, 0.8, 1, 0, -1, -0.8, -0.65, -0.5]
W2[24:32, 28] = [0.5, 0.65, 0.8, 1, 0, -1, -0.8, -0.65]
W2[24:32, 29] = [0.4, 0.5, 0.65, 0.8, 1, 0, -1, -0.8]
W2[24:32, 30] = [0.3, 0.4, 0.5, 0.65, 0.8, 1, 0, -1]
W2[24:32, 31] = [0.25, 0.3, 0.4, 0.5, 0.65, 0.8, 1, 0]
b2[24:32] = [-14.5, -12.95, -11.55, -10.5, -9.5, -8.45, -7.05, -5.5]

# ---------------- Output ----------------
W3[0:8, 0] = -16
W3[8:16, 2] = -12
W3[24:32, 2] = 8
W3[16:24, 4] = -12
W3[24:32, 4] = -8
b3[0:6] = [-112, -30, -44, -30, -156, -30]
```