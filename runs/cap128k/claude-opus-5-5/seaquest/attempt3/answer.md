## Design

**Strategy.** The submarine parks at column 8, facing left, and fires along its row. It moves only up and down. The reasons:

- Divers cross whole rows, so a diver walks into a stationary sub. The sub only has to be in the right row in time.
- Every threat to a sub at column 8 shows up in columns 6–9 of its row. That makes danger checks fixed cell lookups.
- Enemies coming from the left walk into our bullets. Enemies that have already passed (moving left, away from us) are chased down by bullets, which are 6× faster.

**Layer 1 (29 units).**

- **S_r, rows 0–8 (units 0–8):** "the sub is in row r", from the sum of player cells in that row.
- **R_r, rows 1–8 (units 9–16):** "row r has something worth going to."
  - It is a column-weighted score of the reward channel, minus the same column weights on the trail channel.
  - An object's trail sits on its left if it is approaching and on its right if it is receding. So the weights give approaching objects +1.5 and receding ones −1.5.
  - The danger channel adds a small bonus, so enemies (danger + reward) beat divers, and receding enemies stay attractive.
  - Effect: approaching divers or enemies, receding enemies, and divers just spawned at column 9 are attractive. Receding divers and lone bullets are not.
  - Danger at column 8 or 9 cancels the score. Row 1's score is suppressed unless the column-8 gauge cell is lit (a rough "has diver" test).
- **U_r, rows 1–8 (units 17–24):** any danger in columns 6–9 of row r. This means "can't enter this row" for a neighbouring row, and "must leave" for the sub's own row.
- **HD (unit 25): "certainly has a diver".** The gauge channel mixes the oxygen and diver bars, so this is gauge column 8 lit **and** some column 0–7 dark.
- **SURF (unit 26): time to surface.**
  - Diver present and oxygen below 40 (gauge columns 1–2 are oxygen-only, so this is readable).
  - Or 6 divers, detectable only once oxygen is below 60.
- **HR / HL (units 27–28):** horizontal positioning toward column 8 facing left.
  - HR: "a player cell lies in columns 0–7", so go right.
  - HL: "sub at column 9 facing right", so press left once.

**Layer 2.** Each unit is the active-row AND of a linear rule.

- **Up_r (units 0–7):** gate S_r, then add:
  - +50 if the current row is in danger, and +50 if SURF;
  - attraction from rows above minus rows below, weighted 8, 5, 3.5, 2.5, 2 by distance;
  - −10 if the current row is itself attractive (stay and shoot);
  - −150 if the row above is unsafe (a veto).
  - Moving from row 1 into row 0 needs HD (surfacing with no diver ends the game). From row 2, moving up without a diver is heavily penalised because of the 10% sticky-up risk.
- **Down_r (units 8–15):** the mirror image. Downward attraction is weighted ×1.25 to break ties. Row 0 dives whenever row 1 is safe and the sub is in position.
- **Other units:** relays for HR/HL, and a BLOCK unit (sub in row 1 with no confirmed diver) that pushes the "up" logit to −20.

**Output.** Fire is the default (logit 10). A chosen move gets logit about 20, and horizontal correction gets 22.

```edits
# ---------- Layer 1 ----------
# S_r : sub in row r (units 0..8)
W1[0:60:6, 0] = 6
W1[60:120:6, 1] = 6
W1[120:180:6, 2] = 6
W1[180:240:6, 3] = 6
W1[240:300:6, 4] = 6
W1[300:360:6, 5] = 6
W1[360:420:6, 6] = 6
W1[420:480:6, 7] = 6
W1[480:540:6, 8] = 6
b1[0:9] = -6
# R_r : row attractiveness (units 9..16 for rows 1..8)
W1[62:120:6, 9] = [7.5, 12, 16.5, 21, 25.5, 30, 34.5, 39, 43.5, 30]
W1[64:120:6, 9] = [0, -4.5, -9, -13.5, -18, -22.5, -27, -31.5, -36, 0]
W1[61:120:6, 9] = [3, 3, 3, 3, 3, 3, -9, -9, -60, -90]
W1[122:180:6, 10] = [7.5, 12, 16.5, 21, 25.5, 30, 34.5, 39, 43.5, 30]
W1[124:180:6, 10] = [0, -4.5, -9, -13.5, -18, -22.5, -27, -31.5, -36, 0]
W1[121:180:6, 10] = [3, 3, 3, 3, 3, 3, -9, -9, -60, -90]
W1[182:240:6, 11] = [7.5, 12, 16.5, 21, 25.5, 30, 34.5, 39, 43.5, 30]
W1[184:240:6, 11] = [0, -4.5, -9, -13.5, -18, -22.5, -27, -31.5, -36, 0]
W1[181:240:6, 11] = [3, 3, 3, 3, 3, 3, -9, -9, -60, -90]
W1[242:300:6, 12] = [7.5, 12, 16.5, 21, 25.5, 30, 34.5, 39, 43.5, 30]
W1[244:300:6, 12] = [0, -4.5, -9, -13.5, -18, -22.5, -27, -31.5, -36, 0]
W1[241:300:6, 12] = [3, 3, 3, 3, 3, 3, -9, -9, -60, -90]
W1[302:360:6, 13] = [7.5, 12, 16.5, 21, 25.5, 30, 34.5, 39, 43.5, 30]
W1[304:360:6, 13] = [0, -4.5, -9, -13.5, -18, -22.5, -27, -31.5, -36, 0]
W1[301:360:6, 13] = [3, 3, 3, 3, 3, 3, -9, -9, -60, -90]
W1[362:420:6, 14] = [7.5, 12, 16.5, 21, 25.5, 30, 34.5, 39, 43.5, 30]
W1[364:420:6, 14] = [0, -4.5, -9, -13.5, -18, -22.5, -27, -31.5, -36, 0]
W1[361:420:6, 14] = [3, 3, 3, 3, 3, 3, -9, -9, -60, -90]
W1[422:480:6, 15] = [7.5, 12, 16.5, 21, 25.5, 30, 34.5, 39, 43.5, 30]
W1[424:480:6, 15] = [0, -4.5, -9, -13.5, -18, -22.5, -27, -31.5, -36, 0]
W1[421:480:6, 15] = [3, 3, 3, 3, 3, 3, -9, -9, -60, -90]
W1[482:540:6, 16] = [7.5, 12, 16.5, 21, 25.5, 30, 34.5, 39, 43.5, 30]
W1[484:540:6, 16] = [0, -4.5, -9, -13.5, -18, -22.5, -27, -31.5, -36, 0]
W1[481:540:6, 16] = [3, 3, 3, 3, 3, 3, -9, -9, -60, -90]
b1[9:17] = -4.5
W1[593, 9] = 40
b1[9] = -44.5
# U_r : danger in cols 6..9 of row r (units 17..24)
W1[97:120:6, 17] = 10
W1[157:180:6, 18] = 10
W1[217:240:6, 19] = 10
W1[277:300:6, 20] = 10
W1[337:360:6, 21] = 10
W1[397:420:6, 22] = 10
W1[457:480:6, 23] = 10
W1[517:540:6, 24] = 10
b1[17:25] = -5
# HD : surely has a diver (unit 25)
W1[593, 25] = 120
W1[545:593:6, 25] = -12
b1[25] = -30
# SURF (unit 26)
W1[593, 26] = 12
W1[551, 26] = -12
W1[563, 26] = 24
W1[557, 26] = -24
b1[26] = -6
# HR : player cell in cols 0..7 (unit 27)
W1[0:48:6, 27] = 8
W1[60:108:6, 27] = 8
W1[120:168:6, 27] = 8
W1[180:228:6, 27] = 8
W1[240:288:6, 27] = 8
W1[300:348:6, 27] = 8
W1[360:408:6, 27] = 8
W1[420:468:6, 27] = 8
W1[480:528:6, 27] = 8
b1[27] = -4
# HL : at col 9 facing right (unit 28)
W1[0:48:6, 28] = -16
W1[60:108:6, 28] = -16
W1[120:168:6, 28] = -16
W1[180:228:6, 28] = -16
W1[240:288:6, 28] = -16
W1[300:348:6, 28] = -16
W1[360:408:6, 28] = -16
W1[420:468:6, 28] = -16
W1[480:528:6, 28] = -16
W1[54:600:60, 28] = 8
W1[58:600:60, 28] = -8
b1[28] = -4

# ---------- Layer 2 ----------
W2[26, 0:8] = 25
W2[26, 8:16] = -15
# Up_1 .. Up_8 (units 0..7)
W2[1, 0] = 100
W2[17, 0] = 25
W2[25, 0] = 100
W2[9:17, 0] = [-5, -5, -3.125, -2.1875, -1.5625, -1.25, -1.25, -1.25]
b2[0] = -171.625
W2[2, 1] = 100
W2[18, 1] = 25
W2[17, 1] = -75
W2[25, 1] = 22.5
W2[9:17, 1] = [4, -5, -5, -3.125, -2.1875, -1.5625, -1.25, -1.25]
b2[1] = -163.875
W2[3, 2] = 100
W2[19, 2] = 25
W2[18, 2] = -75
W2[9:17, 2] = [2.5, 4, -5, -5, -3.125, -2.1875, -1.5625, -1.25]
b2[2] = -137.625
W2[4, 3] = 100
W2[20, 3] = 25
W2[19, 3] = -75
W2[9:17, 3] = [1.75, 2.5, 4, -5, -5, -3.125, -2.1875, -1.5625]
b2[3] = -134.625
W2[5, 4] = 100
W2[21, 4] = 25
W2[20, 4] = -75
W2[9:17, 4] = [1.25, 1.75, 2.5, 4, -5, -5, -3.125, -2.1875]
b2[4] = -131.8125
W2[6, 5] = 100
W2[22, 5] = 25
W2[21, 5] = -75
W2[9:17, 5] = [1, 1.25, 1.75, 2.5, 4, -5, -5, -3.125]
b2[5] = -128.625
W2[7, 6] = 100
W2[23, 6] = 25
W2[22, 6] = -75
W2[9:17, 6] = [1, 1, 1.25, 1.75, 2.5, 4, -5, -5]
b2[6] = -124.5
W2[8, 7] = 100
W2[24, 7] = 25
W2[23, 7] = -75
W2[9:17, 7] = [1, 1, 1, 1.25, 1.75, 2.5, 4, -5]
b2[7] = -118.5
# Down_0 (unit 8)
W2[0, 8] = 100
W2[17, 8] = -75
W2[27, 8] = -20
W2[28, 8] = -20
b2[8] = -227
# Down_1 .. Down_7 (units 9..15)
W2[1, 9] = 100
W2[17, 9] = 25
W2[18, 9] = -75
W2[9:17, 9] = [-5, 5, 3.125, 2.1875, 1.5625, 1.25, 1.25, 1.25]
b2[9] = -155.375
W2[2, 10] = 100
W2[18, 10] = 25
W2[19, 10] = -75
W2[9:17, 10] = [-4, -5, 5, 3.125, 2.1875, 1.5625, 1.25, 1.25]
b2[10] = -160.625
W2[3, 11] = 100
W2[19, 11] = 25
W2[20, 11] = -75
W2[9:17, 11] = [-2.5, -4, -5, 5, 3.125, 2.1875, 1.5625, 1.25]
b2[11] = -164.375
W2[4, 12] = 100
W2[20, 12] = 25
W2[21, 12] = -75
W2[9:17, 12] = [-1.75, -2.5, -4, -5, 5, 3.125, 2.1875, 1.5625]
b2[12] = -167.375
W2[5, 13] = 100
W2[21, 13] = 25
W2[22, 13] = -75
W2[9:17, 13] = [-1.25, -1.75, -2.5, -4, -5, 5, 3.125, 2.1875]
b2[13] = -170.1875
W2[6, 14] = 100
W2[22, 14] = 25
W2[23, 14] = -75
W2[9:17, 14] = [-1, -1.25, -1.75, -2.5, -4, -5, 5, 3.125]
b2[14] = -173.375
W2[7, 15] = 100
W2[23, 15] = 25
W2[24, 15] = -75
W2[9:17, 15] = [-1, -1, -1.25, -1.75, -2.5, -4, -5, 5]
b2[15] = -177.5
# relays and block
W2[27, 16] = 5
W2[28, 17] = 5
W2[1, 18] = 10
W2[25, 18] = -10
b2[18] = -10

# ---------- Output ----------
W3[0:8, 2] = 10
W3[1, 2] = 7
W3[18, 2] = -10
b3[2] = 67
W3[8:16, 4] = 10
b3[4] = 80
W3[16, 3] = 11
b3[3] = 11
W3[17, 1] = 11
b3[1] = 11
b3[5] = 10
```