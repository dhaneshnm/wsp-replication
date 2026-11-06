# Hand-built Seaquest policy: design and weights

## Strategy

The sub keeps near the centre columns (4–5). It moves vertically to rows that contain targets (enemies or divers), turns to face an enemy in its own row, and fires. It refuses vertical moves into cells that are about to be dangerous. It dodges vertically when an enemy bullet is in its row. It surfaces when oxygen is low and it carries at least one diver. It never goes up from row 1 otherwise, because surfacing without a diver ends the game.

## Layer 1: per-row gated units

Each per-row unit is gated by the player being in row k. Every player cell of row k gets weight 10 and the bias is −20. When the player is in another row, the unit outputs exactly −1. Each group has 7 units (rows 2..8), so its sum plus 6 equals the value of the active row's unit.

- **V_k (units 0–6), vertical drive.**
  - Rewards in other rows pull with weights 0.5, 0.4, 0.3, … by distance: positive for rows above, negative for rows below.
  - Danger in columns 2–7 of the row above adds about −4, which vetoes up. Danger in the row below adds about +4, which vetoes down.
  - Row 1 targets are ignored, and V_2 has an extra −0.5 bias toward going down.
  - The value encodes three levels: |V| < 0.9 means "go up/down"; |V| > 0.9 means a veto with no push.
- **O_k (units 7–13), facing direction.** It equals 2·(front − back), read from the player and trail channels in columns 3–6.
- **D_k (units 14–20), side of the target.** Danger plus reward cells weigh ±0.6, so an enemy (in both channels) counts ±1.2 and a diver ±0.6. A small term on the player's position re-centres the sub. After tanh, |D| > 0.716 means "enemy on that side"; a smaller |D| means re-centre or step toward a diver.
- **Y_k (units 21–27), bullet in my row.** Danger minus reward detects enemy bullets.

## Layer 1: global units

- **S (unit 28), surface now.** True when gauge cell (9,2) is off (oxygen below 60) and gauge cell (9,8) is on (at least one diver).
- **R01 (unit 29).** True when the player is in row 0 or 1.

## Layer 2: step and AND detectors

The second layer turns these signals into on/off conditions:
- **Vertical:** up-desire, down-veto, down-desire, up-veto.
- **Horizontal:** fire-right, fire-left, turn-right, turn-left, re-centre right or left.
- **Dodging:** dodge up or down, chosen by the sign of V.
- **Surfacing and top rows:** a copy of S, a copy of R01, surface-from-row-1, and go-down-from-rows-0/1.

## Output logits, by priority

| Action / condition | Logit |
|---|---|
| Dodge | 10 |
| Leave rows 0/1 / surface from row 1 | ~10 |
| Surface (rows 2..8) | 9 |
| Fire or turn at an enemy in my row | 7 |
| Vertical chase | 3 |
| Re-centre | 1.5 |
| Default fire | 1 |
| Default no-op | 0 |
| Vetoed move | −20 |

```edits
# ---------- Layer 1: V_k (units 0..6, rows 2..8) ----------
W1[120:180:6, 0] = 10
W1[182:240:6, 0] = -0.5
W1[242:300:6, 0] = -0.4
W1[302:360:6, 0] = -0.3
W1[362:420:6, 0] = -0.22
W1[422:480:6, 0] = -0.16
W1[482:540:6, 0] = -0.12
W1[73:104:6, 0] = [-3.5, -4, -4, -4, -4, -3.5]
W1[193:224:6, 0] = [3.5, 4, 4, 4, 4, 3.5]
b1[0] = -20.5

W1[180:240:6, 1] = 10
W1[122:180:6, 1] = 0.5
W1[242:300:6, 1] = -0.5
W1[302:360:6, 1] = -0.4
W1[362:420:6, 1] = -0.3
W1[422:480:6, 1] = -0.22
W1[482:540:6, 1] = -0.16
W1[133:164:6, 1] = [-3.5, -4, -4, -4, -4, -3.5]
W1[253:284:6, 1] = [3.5, 4, 4, 4, 4, 3.5]
b1[1] = -20

W1[240:300:6, 2] = 10
W1[122:180:6, 2] = 0.4
W1[182:240:6, 2] = 0.5
W1[302:360:6, 2] = -0.5
W1[362:420:6, 2] = -0.4
W1[422:480:6, 2] = -0.3
W1[482:540:6, 2] = -0.22
W1[193:224:6, 2] = [-3.5, -4, -4, -4, -4, -3.5]
W1[313:344:6, 2] = [3.5, 4, 4, 4, 4, 3.5]
b1[2] = -20

W1[300:360:6, 3] = 10
W1[122:180:6, 3] = 0.3
W1[182:240:6, 3] = 0.4
W1[242:300:6, 3] = 0.5
W1[362:420:6, 3] = -0.5
W1[422:480:6, 3] = -0.4
W1[482:540:6, 3] = -0.3
W1[253:284:6, 3] = [-3.5, -4, -4, -4, -4, -3.5]
W1[373:404:6, 3] = [3.5, 4, 4, 4, 4, 3.5]
b1[3] = -20

W1[360:420:6, 4] = 10
W1[122:180:6, 4] = 0.22
W1[182:240:6, 4] = 0.3
W1[242:300:6, 4] = 0.4
W1[302:360:6, 4] = 0.5
W1[422:480:6, 4] = -0.5
W1[482:540:6, 4] = -0.4
W1[313:344:6, 4] = [-3.5, -4, -4, -4, -4, -3.5]
W1[433:464:6, 4] = [3.5, 4, 4, 4, 4, 3.5]
b1[4] = -20

W1[420:480:6, 5] = 10
W1[122:180:6, 5] = 0.16
W1[182:240:6, 5] = 0.22
W1[242:300:6, 5] = 0.3
W1[302:360:6, 5] = 0.4
W1[362:420:6, 5] = 0.5
W1[482:540:6, 5] = -0.5
W1[373:404:6, 5] = [-3.5, -4, -4, -4, -4, -3.5]
W1[493:524:6, 5] = [3.5, 4, 4, 4, 4, 3.5]
b1[5] = -20

W1[480:540:6, 6] = 10
W1[122:180:6, 6] = 0.12
W1[182:240:6, 6] = 0.16
W1[242:300:6, 6] = 0.22
W1[302:360:6, 6] = 0.3
W1[362:420:6, 6] = 0.4
W1[422:480:6, 6] = 0.5
W1[433:464:6, 6] = [-3.5, -4, -4, -4, -4, -3.5]
b1[6] = -20

# ---------- Layer 1: O_k orientation (units 7..13) ----------
W1[120:180:6, 7] = 10
W1[138:162:6, 7] = [7, 9, 11, 13]
W1[142:166:6, 7] = [6, 2, -2, -6]
W1[180:240:6, 8] = 10
W1[198:222:6, 8] = [7, 9, 11, 13]
W1[202:226:6, 8] = [6, 2, -2, -6]
W1[240:300:6, 9] = 10
W1[258:282:6, 9] = [7, 9, 11, 13]
W1[262:286:6, 9] = [6, 2, -2, -6]
W1[300:360:6, 10] = 10
W1[318:342:6, 10] = [7, 9, 11, 13]
W1[322:346:6, 10] = [6, 2, -2, -6]
W1[360:420:6, 11] = 10
W1[378:402:6, 11] = [7, 9, 11, 13]
W1[382:406:6, 11] = [6, 2, -2, -6]
W1[420:480:6, 12] = 10
W1[438:462:6, 12] = [7, 9, 11, 13]
W1[442:466:6, 12] = [6, 2, -2, -6]
W1[480:540:6, 13] = 10
W1[498:522:6, 13] = [7, 9, 11, 13]
W1[502:526:6, 13] = [6, 2, -2, -6]
b1[7:14] = -20

# ---------- Layer 1: D_k target side + recentre (units 14..20) ----------
W1[120:180:6, 14] = [10.27, 10.21, 10.15, 10.09, 10.03, 9.97, 9.91, 9.85, 9.79, 9.73]
W1[121:180:6, 14] = [-0.6, -0.6, -0.6, -0.6, 0, 0, 0.6, 0.6, 0.6, 0.6]
W1[122:180:6, 14] = [-0.6, -0.6, -0.6, -0.6, 0, 0, 0.6, 0.6, 0.6, 0.6]
W1[180:240:6, 15] = [10.27, 10.21, 10.15, 10.09, 10.03, 9.97, 9.91, 9.85, 9.79, 9.73]
W1[181:240:6, 15] = [-0.6, -0.6, -0.6, -0.6, 0, 0, 0.6, 0.6, 0.6, 0.6]
W1[182:240:6, 15] = [-0.6, -0.6, -0.6, -0.6, 0, 0, 0.6, 0.6, 0.6, 0.6]
W1[240:300:6, 16] = [10.27, 10.21, 10.15, 10.09, 10.03, 9.97, 9.91, 9.85, 9.79, 9.73]
W1[241:300:6, 16] = [-0.6, -0.6, -0.6, -0.6, 0, 0, 0.6, 0.6, 0.6, 0.6]
W1[242:300:6, 16] = [-0.6, -0.6, -0.6, -0.6, 0, 0, 0.6, 0.6, 0.6, 0.6]
W1[300:360:6, 17] = [10.27, 10.21, 10.15, 10.09, 10.03, 9.97, 9.91, 9.85, 9.79, 9.73]
W1[301:360:6, 17] = [-0.6, -0.6, -0.6, -0.6, 0, 0, 0.6, 0.6, 0.6, 0.6]
W1[302:360:6, 17] = [-0.6, -0.6, -0.6, -0.6, 0, 0, 0.6, 0.6, 0.6, 0.6]
W1[360:420:6, 18] = [10.27, 10.21, 10.15, 10.09, 10.03, 9.97, 9.91, 9.85, 9.79, 9.73]
W1[361:420:6, 18] = [-0.6, -0.6, -0.6, -0.6, 0, 0, 0.6, 0.6, 0.6, 0.6]
W1[362:420:6, 18] = [-0.6, -0.6, -0.6, -0.6, 0, 0, 0.6, 0.6, 0.6, 0.6]
W1[420:480:6, 19] = [10.27, 10.21, 10.15, 10.09, 10.03, 9.97, 9.91, 9.85, 9.79, 9.73]
W1[421:480:6, 19] = [-0.6, -0.6, -0.6, -0.6, 0, 0, 0.6, 0.6, 0.6, 0.6]
W1[422:480:6, 19] = [-0.6, -0.6, -0.6, -0.6, 0, 0, 0.6, 0.6, 0.6, 0.6]
W1[480:540:6, 20] = [10.27, 10.21, 10.15, 10.09, 10.03, 9.97, 9.91, 9.85, 9.79, 9.73]
W1[481:540:6, 20] = [-0.6, -0.6, -0.6, -0.6, 0, 0, 0.6, 0.6, 0.6, 0.6]
W1[482:540:6, 20] = [-0.6, -0.6, -0.6, -0.6, 0, 0, 0.6, 0.6, 0.6, 0.6]
b1[14:21] = -20

# ---------- Layer 1: Y_k bullet in my row (units 21..27) ----------
W1[120:180:6, 21] = 10
W1[121:180:6, 21] = 3
W1[122:180:6, 21] = -3
W1[180:240:6, 22] = 10
W1[181:240:6, 22] = 3
W1[182:240:6, 22] = -3
W1[240:300:6, 23] = 10
W1[241:300:6, 23] = 3
W1[242:300:6, 23] = -3
W1[300:360:6, 24] = 10
W1[301:360:6, 24] = 3
W1[302:360:6, 24] = -3
W1[360:420:6, 25] = 10
W1[361:420:6, 25] = 3
W1[362:420:6, 25] = -3
W1[420:480:6, 26] = 10
W1[421:480:6, 26] = 3
W1[422:480:6, 26] = -3
W1[480:540:6, 27] = 10
W1[481:540:6, 27] = 3
W1[482:540:6, 27] = -3
b1[21:28] = -21.5

# ---------- Layer 1: S (surface) and R01 ----------
W1[593, 28] = 5
W1[557, 28] = -5
b1[28] = -2.5
W1[0:60:6, 29] = 5
W1[60:120:6, 29] = 5
b1[29] = -5

# ---------- Layer 2 ----------
W2[0:7, 0] = 80
b2[0] = 475.2
W2[0:7, 1] = 40
b2[1] = 204
W2[0:7, 2] = -80
b2[2] = -484.8
W2[0:7, 3] = -40
b2[3] = -276
W2[14:21, 4] = 100
W2[7:14, 4] = 40
b2[4] = 730
W2[14:21, 5] = -100
W2[7:14, 5] = -40
b2[5] = -950
W2[14:21, 6] = 100
W2[7:14, 6] = -40
b2[6] = 250
W2[14:21, 7] = -100
W2[7:14, 7] = 40
b2[7] = -470
W2[14:21, 8] = 60
b2[8] = 356.4
W2[14:21, 9] = -60
b2[9] = -363.6
W2[0:7, 10] = 80
W2[21:28, 10] = 100
b2[10] = 1004.8
W2[0:7, 11] = -80
W2[21:28, 11] = 100
b2[11] = 35.2
W2[28, 12] = 5
W2[29, 13] = 5
W2[28, 14] = 5
W2[29, 14] = 5
b2[14] = -5
W2[29, 15] = 5
W2[28, 15] = -5
b2[15] = -5

# ---------- Layer 3 (logits: 0 noop,1 left,2 up,3 right,4 down,5 fire) ----------
W3[4, 5] = 3
W3[5, 5] = 3
W3[13, 5] = -3
b3[5] = 4
W3[7, 1] = 2.75
W3[9, 1] = 3.75
W3[5, 1] = -3.75
b3[1] = -3.25
W3[6, 3] = 2.75
W3[8, 3] = 3.75
W3[4, 3] = -3.75
b3[3] = -3.25
W3[0, 2] = 4.5
W3[1, 2] = -4.5
W3[10, 2] = 8
W3[12, 2] = 7.5
W3[3, 2] = -10
W3[14, 2] = 11
b3[2] = 10.5
W3[2, 4] = 4.5
W3[3, 4] = -4.5
W3[11, 4] = 8
W3[1, 4] = -10
W3[15, 4] = 8
b3[4] = 0
```