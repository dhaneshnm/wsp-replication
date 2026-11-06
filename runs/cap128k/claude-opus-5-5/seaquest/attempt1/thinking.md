I need a workable policy without running anything, so I'll aim for something simple and reasonable. The MinAtar Seaquest baselines land somewhere around 5 to 20 points, which gives me a target. The oxygen timer drains after about 200 steps underwater, so the sub has to surface to pick up divers. My rough plan is to hold a row, fire at enemies to the left and right, and surface at the right moment.

I'm sketching out the enemy behavior: they spawn on the edges of the middle rows and slide sideways, and their bullets travel in the direction they face. The plan is to sit in a row and keep firing at whatever comes across it. Anything approaching from behind is the real danger, while enemies in other rows don't matter unless I move vertically.

I'm settling on a fixed row, turning toward enemies there, and firing, since each shot should clear an enemy in roughly five steps while spawns come only every twenty. The main risk I see is an enemy sub in my own row firing back, but if I shoot as soon as it appears, my bullet should reach it before its first shot.

I'm weighing whether to dodge by switching rows, but that adds complexity, and the other option is to keep tracking enemies vertically in the row they're in.

I'm weighing a shot-and-dodge approach against just tracking enemies vertically, but moving into a row next to an enemy is risky. I also need to plan for oxygen, since surfacing refills it. Each surfacing makes the game harder, and I'm keeping track of how many divers I'm carrying.

I'm recalling typical DQN results on MinAtar Seaquest, which are somewhere in the tens, so that's a rough benchmark. Next I'm going to combine three rules: move vertically toward enemies or divers, face and fire when a target shares my row, and only surface for oxygen when I'm carrying a diver.

I'm working out how to read the sub's position from the state grid: the row it's in should show up as two filled cells on the first channel, with the back cell possibly running off the edge at the borders.

I'm checking the facing rules at the grid edges, and working out that the sub can never face right at x=0. Then I'm telling the front cell from the back by the trail channel, so I can read orientation off the state. Next I'm weighing a simpler design that uses fewer units.

I'm sketching out how to encode vertical tracking and shooting in the network, and I'm not sure a plain feature layout will capture the oxygen logic cleanly yet.

I'm thinking about how to encode the target-row logic: for each possible sub row, a unit that switches on only when the sub sits there, so that "target above" and "target below" can be expressed without needing product terms.

I'm building a per-row unit that fires only when the sub sits in row k, so it can weigh targets above against targets below. Outside that row the unit stays saturated at a constant, so it adds nothing to the output.

I'm gating a per-row unit so it only responds when the sub sits in row k: outside that row it stays saturated at -1, and inside it reflects the difference between targets below and above. Summing across the nine rows should leave a constant plus a single tanh term for the active row, which keeps the vertical signal clean.

I'm turning to the horizontal side now, where I need to know whether targets in the sub's row lie to the left or right of it. That's another product of two conditions, row and column, so I'm considering gating per row and then weighing the column position within it.

Simplifying by keeping the sub near a central column would make the left-versus-right split fixed, though divers crossing its row complicate that.

I'm settling on a policy where the sub only needs vertical alignment with divers, since they drift toward it, and any enemy in its row is fair game because a shot travels faster than enemies move. For the horizontal side, I'll look at which side of the sub the threats sit on and face that way, treating the sub as roughly central.

I'm working out how to handle the horizontal side: the sub bounces between columns 5 and 6, and enemies close to it are dangerous no matter what. I'm thinking of gating a per-row unit for the left-versus-right difference in threats, weighted by that row.

I'm working out how to tell which way the sub faces by summing the column positions of its cells on the first channel. Then I'll compare enemy counts on the far left against the far right within each row, so the sub can turn toward threats or fire when already facing them.

I'm now weighing how to tell which way the sub faces, since the front and back cells can't be separated with a single linear feature. Trying to isolate the back cell runs into the same product problem, and gating by row adds more complexity. I'm considering skipping orientation altogether and just steering toward enemies, though that leaves out firing.

I'm stuck on telling which way the sub faces. Front and back cells both light up on channel 0, and channel 4 also picks up enemy trails, so a single linear feature can't separate them cleanly. I'm considering whether a per-row gate that reads channel 4 could isolate the back cell.

I'm trying to tell the sub's front cell from its back, since each channel alone mixes in enemy trails. A per-cell difference doesn't separate them cleanly, and a per-cell AND would take too many units. I'm considering per-column gates or a sum over rows that combines both channels.

I'm trying to get the sub's facing direction from the state, and I'm considering a row-gated orientation unit. The trouble is that it would still need a product of the trail channel and the front-cell positions. An alternative is to pin the sub to fixed columns for each facing, so its occupied cells reveal orientation directly.

I'm checking whether the sub's front cell can be told apart from its back using the channel 0 and channel 4 readings in its row, since enemy trails on channel 4 muddy a simple column sum. A per-column count won't cleanly separate them, so I'm looking at whether the cells at columns 5 and 6 in the sub's row can settle which end is the front.

I'm trying to get the facing direction from the back cell, since it's the one that sits on the trail channel too. Shifting the sub's own orientation into a weighted sum over trail positions across the row might separate it without assuming the sub stays at columns 5 and 6.

I'm weighing whether the sub's facing can be read from the sum of column positions across both channels in its row. The back cell also shows up on the trail channel, which makes a clean product hard without gating. Enemy trails in that row would throw the sum off, though it only matters when an enemy is actually present.

I'm trying to tell which way the sub faces by using a column-weighted sum over both channels in its row, since the back cell also lights up on the trail channel. Enemy trails in that row would skew the sum, though, so I'm checking whether a short phrase is enough for this stretch.

I'm weighing whether orientation can be computed per row, which would cost about nine more units on top of the vertical and horizontal ones. The trouble is that enemy trails on channel 4 pollute the back-cell signal whenever an enemy shares that row, so I'm looking for a way around that.

I'm writing the per-row orientation term as a weighted sum of column positions over the trail channel minus the front-and-back channel, so the back cell's offset shows up as a sign. The enemy trails will skew that sum, and I can subtract them out by locating each reward object's trail one cell to either side.

I'm checking the orientation signal for edge cases: an object at column 9 moving left would have its trail cut off the grid, which skews the sum by about nine units. That error would make the orientation term unreliable near the edges.

I'm trying to isolate the sub's back cell with a per-column unit that sums both channels over the column, since the back is the only cell lit on both. Enemy trails in the same column could still pollute that sum, so I'm checking whether the column count alone is enough to separate them.

I'm trying to pin down the back cell with a layer-two unit that combines per-column gates, using a linear ch0 sum to recover the front-minus-back difference.

I'm now considering whether to drop orientation tracking altogether and let the sub's position imply which way it faces, or to dodge vertically out of an enemy's row instead of trying to turn toward it.

I'm looking at whether the row-gated orientation unit can tell front from back by comparing the trail channel at columns 4 and 5 in each row, weighted by the sub's position in that row. That only holds if the sub sits exactly at columns 4 and 5, so I'm checking how to generalize it.

I'm checking whether the sub's facing can be read from a column-weighted difference of the trail and front-and-back channels in its own row. Enemy and diver trails in that row would still throw the sum off, so I'm looking at whether restricting the sub to a narrow band of columns would keep that pollution small.

I'm restricting the orientation check to columns 3 through 6, weighting ch4 against ch0 so that each row's offset comes out as roughly plus or minus a half. The catch is that any enemy or diver trail inside that band would shift the sum, so the signal only holds when nothing else is in those cells.

I'm working out how the sub can keep its horizontal position within columns 3 through 6, which I can read from the channel 0 total without any gating. Once that holds, the facing signal in its own row stays readable, though I'd still have to turn toward an enemy and that turn shifts the sub's position.

I'm noticing that if I only ever turn back and forth, the sub keeps the same two cells, so the orientation check stays stable. Any drift would come from repeated same-direction presses, so I'm thinking about whether a little centering would keep it steady.

I'm weighing a window of columns 2 through 7 instead of 3 through 6, to tolerate a bit more offset in the sub's position. The catch is that any enemy trail landing in that wider band could pollute the orientation sum, so I'm checking whether an enemy coming from the left, one column back of its trail, would fall inside the window.

I'm settling on a per-row orientation unit that sums the trail channel against the front-and-back channel across columns 3 to 6, so the back cell's offset appears as a sign. Enemy or diver trails inside that window would pollute the sum, but that only happens when something is already very close to the sub.

I'm tallying the per-row budget now: vertical units for rows 0 through 8, horizontal enemy-side units for rows 1 through 8, and orientation units for rows 1 through 8, which comes to about 25 units. That leaves roughly 7 for oxygen, diver count, and the rest. I'm also wondering whether the horizontal and orientation units could be merged into one per-row unit.

I'm checking whether a merged per-row unit can encode "turn right" as enemy-on-the-right AND facing-left, using a threshold combination of the two signals instead of separate layer-two units.

I'm turning to the vertical side of the policy now, weighing how to move toward rows with enemies or divers without stepping into a row where an enemy sits right beside the sub's column. Enemy bullets are a risk too, so I'm also thinking about how the sub should handle them while it's changing rows.

Checking how the bullet moves against the fish in the same step: a bullet can't pass through a fish, since both the bullet's move and the fish's move trigger a collision check. Now I'm turning to enemy bullets, which the sub's own firing logic doesn't cover.

I'm weighing how close enemy subs are to shooting at me: one already in flight toward my row means I have to dodge vertically, and subs facing me need to be shot quickly. I also want to avoid stepping into a row right next to an enemy. My priority is kills first, then staying alive long enough to use the oxygen limit, with divers extending that.

I'm working out the diver priorities next: when there are no divers on board, the sub goes after them vertically ahead of enemies, and it only heads up for air once it has at least one diver.

Checking the front-cell hitbox: the sub can only be hit at its front cell, not its back cell, so moving vertically into a row where an enemy is one or two columns away is the real risk.

I'm checking how enemies approaching from behind can still hit the sub at its front cell. For the vertical choice, I'm thinking about adding danger from enemies in the rows just above and below, near the sub's columns, so it avoids moving into a row where something is about to reach it.

I'm treating a soft danger term as a sum that pushes the sub down when something threatens from above and up when something threatens from below, which only works if the two effects cancel cleanly. I'll add a separate "stay" region for when the vertical value is small, and layer two turns it into separate want-down and want-up signals. I'm also starting to think about enemy bullets in the sub's own row, especially ones coming from behind it.

I'm checking how bullets behave in the sub's own row: an enemy sub facing me can fire toward my position, and since bullets carry no trail, I can't tell their direction from the board alone.

I'm sorting out how bullets in the sub's own row should count toward the vertical push, since bullets carry no trail and I can't tell their direction. My plan is to treat them as a dodge signal in V_k, nudging the sub toward the middle rows, and I'm checking how that interacts with danger above and below.

I'm working out how an enemy bullet in my row would reach the sub, and I'm settling on dodging once a bullet gets within about four cells, since the player's move resolves before the bullets move.

I'm checking how a bullet in the sub's own row would threaten it, since enemy bullets have no trail and I can't read their direction from the board. My plan is to count danger in adjacent rows within the window of columns 3 to 7 when choosing whether to move vertically, so a bullet approaching from another row is a reason to hold off.

Bullets in my own row would also need dodging, so when I enter a row with a bullet on its way I'll have to move again, even if the vertical pull keeps drawing me back. Firing costs nothing except the move that step, so I'll default to shooting, since bullets don't interact with divers.

I'm now decoding the status bar in row 9, where the oxygen gauge and the diver gauge share the same channel and can overlap. Oxygen fills from the left and divers from the right, so a filled column 9 can only mean oxygen is at or above about 190.

I'm reading the oxygen gauge off row 9: when column 2 is off, oxygen is under about 60, and at that level the diver bar can't reach that far left, so the reading is clean. Column 8 can only mean a diver is aboard when oxygen is low, since a high oxygen reading would fill that column too. So at low oxygen I can trust that signal, and it's a cue to head up for air.

I'm settling on surfacing only when oxygen drops below about 60 steps and I'm carrying at least one diver, since eight rows is well within that window. Once I reach the surface, oxygen refills and the urge fades, but I need to block moving up from row 1 when I have no divers, or I'd drown on the next surface attempt.

I'm thinking about the diver versus enemy distinction: a diver shows up as a reward cell without a sub-cell on top, an enemy as both, and a bullet as only the sub-cell. Since I want the vertical pull to go toward divers, especially when I have none, I need to weigh those signals differently.

I'm weighing the target values so that enemies pull the sub toward them, divers pull it harder, and bullets push it away. The open question is how to weight rows by distance when deciding the vertical move, since targets on opposite sides could cancel out and leave the sub stuck in the middle.

I'm looking at how to fold the own-row targets into the vertical choice, since a scalar sum can't express "hold position." I'm considering a separate hold signal from the enemies in my row, but they can cancel out on either side, so I'm working out how to keep that from being misleading.

I'm working out the layer-2 units now: a DOWN signal that fires when the summed vertical value is clearly positive, and an UP signal for the opposite, both squashed through tanh with a small offset. I'll fill in the exact constants once I see how the sums behave.

I'm now working out how to make the vertical choice respect enemies in my own row, since a scalar sum can't express holding position. My current idea is to suppress the up and down signals when there's a strong horizontal target, though I haven't settled how to express that cleanly.

I'm trying to make the horizontal side work without exceeding my unit budget, so I'm weighing whether to fold the own-row hold signal into the horizontal units or drop it. I'm looking at a per-row unit that combines the turn decision for each row instead of keeping separate horizontal and orientation units.

I'm working out the turn signal for each row: the sum of an enemy's presence and its facing direction, with trail pollution from nearby enemies shifting the facing reading.

I'm checking how an enemy's trail could leak into the facing window: an enemy moving away from the sub in its row, or a diver, can put a trail cell inside columns 3 to 6, which would skew the turn reading.

I'm checking whether the orientation signal can be pinned to columns 5 and 6 only, since the sub's cells are fixed there, and comparing the trail at column 6 against column 5 to read facing direction.

I'm working out the turn logic for the sub's facing: with it at columns 5 and 6, a left-facing sub has its cells at (x, x+1), so pressing left from a right-facing position just shifts it one cell further left, which I need to account for when re-centering.

I'm checking whether centering conflicts with turning: a turn doesn't move the cells, but a repeated press in the same direction after a turn would shift the sub one cell. I'll give centering low priority, only when no enemy is in my row, since drift should be rare.

I'm checking the orientation signal across a wider window of columns, 3 to 7, weighting each column by its position. That way a pair of sub cells anywhere in that range still reads as facing left or right, and the signal is a half-step difference between back and front. The open concern is whether enemies or trails from objects in the same row, within roughly columns 2 to 8, could leak into that window and skew the reading.

I'm checking how an enemy coming in from the far side, or a diver near the window, would leave a trail that lands inside columns 3 to 7, and whether that trail would make the facing reading unreliable for a step or two.

Now I'm checking whether the sum of the column-weighted trail values can still tell which way the sub faces when a stray trail sits inside the window. Subtracting the mean column (5) from each weight should cancel the constant offsets, so the facing reading stays at plus or minus one half, with pollution limited to about two in magnitude. That leaves the reading unreliable for a step or two when an object is close, which I'll accept.

Now I'm weighing whether to merge the per-row signals into one scalar turn decision, since that would save units. I'm testing a single signed value that combines the enemy-right and enemy-left presence with the facing signal, and checking whether its sign comes out right for each of the four cases.

I'm settling on a per-row turn signal: the enemy-right and enemy-left presence plus the facing reading, scaled so the four cases separate with a threshold. Working out the tanh scaling so the layer-2 turn units stay linear enough.

I'm checking whether two enemies stacked on the right, both moving toward the sub while it faces right, would push the combined turn signal past threshold and wrongly trigger a turn. The per-row sum counts enemies rather than just their presence, so multiple enemies on one side could overwhelm the balance. I'm considering whether to saturate the enemy term or weight only the nearest cells, since same-direction enemies are spaced far apart anyway.

I'm checking whether enemies in a window to the right, around columns 7 to 9, would be enough to trigger a turn in time, since they spawn far off and move slowly toward the sub.

I'm checking whether an enemy in the far-left columns could be missed by the left window, and I'm settling on a left window at columns 0 to 3 and a right window at columns 7 to 9. Enemies in those windows should trigger a turn before they reach the sub's cells, and an enemy that has already slipped to column 4 would be too late to turn for, so I'm relying on the earlier detection. I'm also weighing whether to count divers in the same windows, since I want them to pull the sub without being shot at.

I'm weighing how to count the enemy and diver presence in the row without them canceling out, and I'm leaning toward giving enemies a full weight while divers and bullets get a smaller one. Facing toward a bullet or diver doesn't help much, so I'll accept some wasted turns rather than complicate the unit.

I'm weighing a combined turn value that counts enemies twice as heavily as divers or bullets, with a threshold that should fire only when two enemies sit on the right and the sub faces left.

I'm settling on a turn signal where enemies count double against single diver or bullet hits, with the facing term weighted to split the cases. I'm testing a couple of weight pairs to see which threshold leaves the most margin before deciding on the scale.

I'm checking whether a single shared turn unit with a tanh-scaled sum can separate the four enemy-and-facing cases, but the layer-1 output range is tight, so I'd need a high gain in layer 2 to separate them cleanly.

I'm checking whether a single row-wise turn unit still works when the rows with no enemies sum to a constant offset, since an empty row 0 would look like a strong left-turn signal.

I'm turning to the layer-2 turn units now, gating each row's signal on whether the sub is actually in that row. I'll fold that gate into the input weights on the sub's own cells, so inactive rows sit at a flat negative value and the row-zero sum stays neutral.

I'm checking whether the vertical units and a row-zero turn unit are needed, since at row zero the summed turn units would otherwise read as a full left-turn signal. Gating each turn unit on the sub's presence in its row should keep the inactive rows flat, so I'm weighing whether a bias shift on the layer-2 turn units can handle row zero without an extra unit.

I'm budgeting the remaining units: 18 used so far, with room left for an own-row enemy hold signal and an oxygen-low check at the sub's cell.

I'm adding a surface signal that turns on when the diver bar at column 8 is lit and oxygen is low, and turns off when the low-oxygen bar at column 2 is lit, using a steep tanh so it snaps cleanly to plus or minus one.

I'm checking whether the oxygen-based surface signal can tell a diver is present, since the diver bar at column 8 stays lit at high oxygen too and would look like a diver. That ambiguity only lasts for the first twenty steps below the surface, and I won't surface then anyway, so I can accept it.

I'm working out the upward pull next, since targets only sit in rows 1 through 8 and the sub should not drift to row 0 without a reason. The risk is an upward dodge from row 1, so I'm adding a surface term to the vertical units that pushes up only when the oxygen-based surface signal is on.

I'm noticing the upward pull would also fire whenever there are no divers and oxygen is fine, which isn't what I want, so I'll move the surfacing push into a separate layer-2 unit driven by the surface signal. To keep the sub from rising out of row 1 without reason, I'll give the row-1 vertical unit a strong downward bias.

I'm working out how the vertical units should behave in row 1: nothing targets row 0, so the only upward push would come from danger below, and that would surface the sub without a diver, so I'll remove it. I'm also noting that surfacing with a diver aboard is acceptable since it refills oxygen, even if it wasn't planned.

I'm settling the row-0 case: the vertical unit there should always push down, since the sub has to dive back after surfacing and oxygen is refilled so the surface signal is off. The open question is whether a sub at row 0 moving down could walk straight into an enemy in row 1 right next to it.

I'm weighing whether the vertical units need a separate hold term for enemies in the sub's own row, since otherwise the pull from targets in other rows would drag the sub out of a row it should stay in. Making the own-row enemy presence change a turn unit's magnitude might be a way to get that hold without spending another unit.

I'm weighing whether to give the vertical units an own-row hold term, since without one the pull from targets in other rows would drag the sub out of a row it should stay in. I'm also checking whether a magnitude change on the turn units could supply that hold without spending another unit.

I'm sketching a hold unit for each row that goes active when the sub is in that row and counts nearby enemies, divers, and bullets, so the vertical pull doesn't drag the sub out of a row it should stay in.

I'm weighing a hold score that combines the row's enemies, divers, and bullets with different weights, so enemies and divers keep the sub in its row while bullets push it to dodge. Enemies alone cancel out, and divers tip the score toward holding.

I'm checking whether a diver in the sub's row is actually approaching, since a diver moving away would make the hold signal keep the sub waiting for nothing. I'd need to tell approaching objects from receding ones using the trail behind them, so the hold only counts the ones coming toward the sub.

I'm now thinking about whether to hold the sub in its row when enemies or divers are present, since the vertical pull from other rows could drag it away. The approaching-versus-receding distinction would need a directional trail sum, but edge effects make that messy, so I'm leaning toward a simpler hold rule that ignores direction and accepts that objects at the edge will leave the screen soon anyway.

I'm weighing whether a diver in the sub's row is really approaching, since a receding one would keep the hold signal waiting for nothing, and the trail cells on either side might tell the two apart.

I'm weighing whether the approaching-versus-receding check for divers can be done with a position-weighted trail sum, flipping the weights for the left and right halves of the row. Shifting the weights so an object at column 9 counts as neutral would sidestep the edge problem at the screen boundary.

I'm checking the direction signal for each row by weighting the trail cells against the object positions, so approaching objects score positive and receding ones negative, with the weights flipped between the left and right halves.

I'm weighing a direction weight that flips across the row's halves, but the sub's own back cell sits in the trail channel and would pollute the sum. Zeroing the weights in the sub's window would avoid that, yet then an object right at the window edge with a trail just outside it gets misread as approaching.

I'm working out how to define the direction signal for objects in each row, since the sub's own back cell in the trail channel would throw off a simple position-weighted sum. Zeroing the weights near the sub avoids that, but the edge of that window still makes objects just outside it look like they're approaching. I'm also weighing whether the added precision is worth the cost in units, given how many row-gated weights I'd have to write out by hand.

I'm now laying out the layer-1 units: nine vertical and nine turn units, one per sub row, plus eight own-row status units and a surface unit, with a few spare units to spend.

I'm going to hold the sub in its row when enemies are present, since shooting them is worthwhile, and I'll use a simple count of enemies and divers without trying to tell their direction. A diver moving away could cost up to about 25 steps of oxygen, which is a real cost but one I'll accept for now.

I'm still weighing whether to use trail cells to tell approaching divers from receding ones, since the sub's own back cell and the edge columns make the signal messy.

I'm dropping the direction check for divers to keep things simple, and I'll give the hold unit a plain weighting: enemies count one, divers count two, and bullets subtract one.

I'm settling on a vertical score for each row, where enemies and divers pull the sub toward them and bullets push it away, weighted so divers count more than enemies.

I'm setting the vertical pull per row: enemies and divers attract with divers weighted higher, bullets repel, and the influence fades with distance. For the adjacent rows, though, I want enemies near the sub's columns to repel strongly, since moving into one of those rows would be dangerous.

I'm checking how the enemy's position matters when I'm in an adjacent row: if it sits near the sub's columns, moving into that row can get the sub killed. Turning to face it is risky if the enemy is right at the back cell, but once the sub is facing right with the enemy one cell ahead, firing still hits it.

I'm reasoning about how adjacent-row danger should affect the vertical pull, treating the columns near the sub as a window where enemy and bullet activity in the rows above and below pushes the sub away, then writing a per-row formula that combines the distance-weighted pulls from other rows with that danger term and a centering bias.

I'm reconsidering the vertical pull for the adjacent rows: a near-column enemy or bullet in the row above or below should only block moving into that row, but a single signed sum would also push the sub away from it. I might need a thresholded layer-2 decision to keep the veto from acting as a general push.

I'm working out the vertical pull for each row, now including a veto for adjacent rows where an enemy or bullet sits near the sub's columns. Rather than letting that veto push the sub around, I'm thinking of using a hold signal for it and keeping the vertical term moderate.

I'm checking how the summed vertical, turn, and hold signals will combine at layer 2, with the row-0 case handled separately since the dodge signal there just points downward.

I'm sketching the layer-2 decision units now: an UP and a DOWN unit driven by the vertical signal with a threshold, a hold check so DOWN only fires when nothing is blocking, and TURNR and TURNL units keyed to the turn signal. Those feed the output logits for up, down, right, left, and fire.

I'm settling the hold signal's scaling, combining the enemy and diver counts with the adjacent-row danger so the vertical move can be vetoed without pushing the sub around.

I'm working out the DOWN unit's activation as a linear mix of the vertical signal and the hold signal, with a threshold so it only fires when nothing is blocking the move.

I'm checking the dodge case for row 1: with the down bias there, the vertical signal should stay positive, so the sub won't be pushed up into danger.

I'm settling the DOWN and UP thresholds: with the hold term subtracted and dodge adding back, the balance depends on the vertical signal sign, and I'm weighing whether the constants I've picked actually produce that behaviour at the edges.

Checking the down and up thresholds against the three cases: with the hold term at about -1.2, DOWN stays off, and in dodge mode both moves are allowed until the vertical signal passes about 0.6 either way.

I'm checking the adjacent-row danger case: an enemy near the sub in the row above or below should block a vertical move, even when moving away from it. That is conservative but acceptable. Divers in the same row are a pickup signal. For the back-of-sub case, I'm weighing whether turning toward an enemy just behind could still land a shot on it.

I'm checking how an enemy sub in my own row, shooting at me, interacts with my own fire and the dodge logic, and whether a bullet already in flight can still hit me.

I'm weighting the enemy and bullet signals more heavily so that a bullet in flight in my row still triggers a dodge even when an enemy sits there too. I'm settling on scaling where an enemy alone gives a strong hold, a diver counts as a full pickup signal, and a bullet pushes hard the other way.

I'm weighing how adjacent-row enemy and bullet positions should feed into the vertical hold, with a bullet in the same row pushing toward a dodge even when an enemy is also there, and I'm now asking whether far-column bullets should be discounted so they don't trigger needless dodges.

I'm now folding the adjacent-row enemy count into the hold score as well, since an enemy near the sub's columns in an adjacent row should block vertical moves. Bullets in my own row still outweigh that, so a dodge still wins there, and I'll keep the danger push in the vertical signal so dodging points away from it. Next I want to pin down which adjacent-row enemies actually count as dangerous, limited to the columns around the sub.

I'm working out how each row's vertical pull should weigh enemies, divers, and bullets across the full row, with bullets counting against a move and divers counting for it.

I'm adding a centering term based on the sum of cell positions, since horizontal drift from repeated turns could push the sub toward an edge over a long episode.

I'm settling the centering term now: a small horizontal pull toward the middle of the grid, weighted so it never overrides turning when an enemy is in the sub's row, with the orientation window widened to columns 2 through 8 to stay robust.

I'm settling the centering layer: the sum of cell positions gives a signal that goes positive when the sub drifts too far right and negative when it drifts too far left, so I'm passing that through a tanh unit with a threshold near the middle of the grid.

I'm settling the constants for the vertical signal at row 0: the DOWN and UP thresholds need the start-row bias large enough that UP stays off, so I'm checking that the value there stays high enough.

I'm now checking the row-1 case, where pressing up would be fatal unless I'm surfacing. The vertical signal there needs to stay strongly positive, which means dropping the danger-below term for row 2 and reconsidering how bullets further down pull the total negative.

I'm checking the bias for the row-1 vertical unit so that bullets can't flip it, since with a few bullets it stays above the threshold and UP remains off. The one remaining worry is accidental up presses from sampling, so I need the up logit to sit far below the others when UP is off.

I'm checking the sticky-action risk at row 1: if I accidentally press up while only at row 2, the repeat could drop me into row 0 with no divers and end the run, so moving up toward row 1 without divers is the thing to avoid.

I'm weighing whether to keep the sub out of row 1 entirely when no divers are known, since a sticky repeat of up from row 2 could end the run. Requiring a surface to go up at row 2 would avoid that risk, but it also means ignoring enemies and divers in row 1.

I'm settling the sticky-action risk: forbidding the move into row 1 except when surfacing, and noting that column 2 only lights up for oxygen, so the surface check can rely on it.

I'm working out the vertical signal for row 2: targets below push down, targets in row 1 get no weight, and nearby enemies below should not push me up from there. I'm leaning toward a strong bias against moving up at row 2 unless I'm surfacing, which keeps the sticky-action risk from dropping me into row 1 by accident.

I'm weighing a policy that keeps the sub out of row 1 entirely, since a sticky up press from row 2 could drop it into row 0 and end the run. Strong logit gaps should keep accidental up presses rare, and when nothing is detected the default is to fire.

I'm settling the up-action now: it should fire when surfacing is requested and stay suppressed in dodge mode, so I'm adding a large surfacing term to the up logit and pushing the down logit down whenever surfacing is on. I'm also flagging that an enemy directly above during the ascent could still kill the sub, which I'll accept for now.

I'm now deciding how the turn units should handle rows 0 and 1, where I want to avoid spurious turns, and I'm considering whether one unit gated on those two rows can cover both.

I'm checking how the row-0 and row-1 gating can share one unit, and whether the combined turn signal stays quiet there. Then I'm working through the enemy-count unit so that in those top two rows it reads as dodge mode and pushes the sub down.

I'm weighing whether the vertical units for rows 0 and 1 can be merged, or whether they need separate danger terms. Keeping them separate makes sense, since a danger term below row 1 would push the sub upward, which is forbidden there. So at row 1 with enemies nearby below, the real choice is between firing in place and moving down.

I'm settling the row-1 vertical unit, where a danger term below would keep the sub from moving down. I'm adding a gate-only unit for rows 0 and 1 so that at those rows the default is to hold position, and I'm checking the thresholds so the sub stays put instead of drifting up or down.

I'm checking a safety gap in the row-1 vertical unit: with two danger cells, the linear sum can push the signal below the threshold and trigger an unwanted up press. My idea is to add a separate row-1 indicator that suppresses the up logit unless surfacing is requested.

I'm adding a row-0/1 indicator unit R01, so the up logit can be pushed strongly negative whenever the sub is in the top two rows, unless surfacing is requested. I'm also thinking about whether the turn units can get the same suppression through that indicator instead of needing their own row-0 gating.

I'm laying out the rest of the units: value outputs for rows 0 through 8, turn and enemy units for rows 2 through 8, and a row-0/1 indicator that corrects the turn and enemy signals there.

I'm settling the remaining units: a small count of spare slots, and I'm leaning toward keeping the design simple rather than adding more danger terms. Vertical tracking toward enemies seems fine when they're far off horizontally, since I can line up and shoot; the danger term only needs to cover adjacent rows. Default action stays fire, because firing when nothing is in line costs nothing.

Now I'm assigning the input-cell indices and the layer-one unit slots, with the vertical, turn, and enemy units each taking a block of positions.

I'm checking the gating for the row-by-row units: each row's ch0 cells feed a gate that sits near -1 when the sub is elsewhere, so the signal from the other terms has to stay small enough not to flip it. I'll give each cell a weight of 10 so the gate reads 20 when the sub is present, then set the bias to match.

Now I'm setting the vertical units for rows 0 through 8: each gets a bias, a strong self-row term, and weaker pulls from other rows that fade with distance, with adjacent rows also carrying a danger term.

Now I'm weighing the distance scaling: enemies far away would barely move the vertical signal, so I'm considering a larger weight for the pull, with divers counting double and bullets pushing the other way. I'm also starting to think about a mild idle bias toward the middle rows, slightly favoring rows 2 and 3 and leaning away from the bottom ones.

I'm setting the idle bias so rows 2 and 3 drift down and rows 6 through 8 drift up, which settles the default around rows 4 and 5. Enemies in rows 0 and 1 will be left out of the vertical attraction for rows 2 and up, since the sub must never move into row 1, and I'll keep a strong downward bias on row 2 to stop accidental ascents.

I'm checking whether row 2 needs its own up-block, since bullets just below could push its signal negative and trigger an accidental ascent into row 1. I'm considering widening the row-0/1 indicator to cover row 2 as well.

I'm settling the row-2 vertical unit by giving it only positive pulls from the rows below, so it can't push upward into row 1. With a small positive bias there, the sub drifts down when idle and never presses up.

Making the row-2 vertical unit carry a large positive bias, so it never reads as dodge and never presses up, seems the cleaner fix than adding another indicator.

I'm settling V_1 as well: a bias of 2 with no negative weights keeps it pointing down, but if danger sits in row 2 that could still push the sub into harm, so I'm weighing a penalty for nearby danger.

I'm settling V_1 with a bias of 2 and a danger penalty of 1.9 per nearby danger cell, so one danger keeps it near zero and two tip it upward, where the layer-two suppression blocks the move. V_0 gets the same bias but a penalty for danger in row 1. For row 2, I'm relying on its positive bias and the hold rule for nearby danger, though I'm still checking what happens when bullets appear there.

I'm settling the upward-attraction terms for the vertical units from rows 3 through 8, weighting each row by its distance with opposite signs for above and below. I'm also setting a fixed push for danger in adjacent rows so the sub is nudged away from it.

I'm setting the idle biases so rows 3 through 8 pull toward the middle, with row 3 leaning down and rows 6 through 8 leaning up. Adjacent-row danger gets a repel term on each side, which nets slightly negative when an enemy sits next to the sub.

Now I'm setting the idle biases for the rows 3 through 8 so the sub drifts toward the middle, and I'm moving on to the enemy units for rows 2 through 8. Each of those starts with a large negative bias so it stays quiet unless something is in its row, and the row-wide input cells get a weight of 10.

Still working out the row-2 gating for the enemy unit, checking how its own-row weights and the adjacent-row hold term balance out.

Next I'm checking the enemy units for rows 2 through 8: a strong bias keeps them quiet unless something is in their row, and an adjacent-row danger term makes them hold. Row 1 gets left out for row 2, since the sub never moves up from there except when surfacing.

Now I'm working out the T units for rows 2 through 8, comparing enemy and diver counts on the left and right sides of the sub to decide which way to turn.

I'm weighing how wide the left and right windows should be for the turn units, since two enemies moving the same way could tip the count and make the sub turn the wrong direction. I'm considering shrinking the enemy weight a bit to keep that from happening.

Now I'm weighing the turn units: for enemies to the right while the sub faces left, the count gives a positive value, so the sub turns right, and the facing-right case is what I'm working through next.

Now I'm setting the turn unit's threshold at 2.5 and checking the scaling, with x = 3, 2, and 2.5 for the different cases, to see whether a gain of 40 keeps the output near ±1.

Now I'm checking the pollution in the side windows: the trailing cells of an enemy approaching from the right could leak into the facing-left signal and push the turn the wrong way.

I'm narrowing the side windows for the turn units to columns 4 through 7, since a wider window lets an enemy's trailing cells leak into the facing signal and push the turn the wrong way. That keeps an enemy one step ahead of the sub from registering as a reason to turn toward it.

I'm checking whether receding enemies could leak trail cells into the facing signal and push the turn the wrong way, since a trailing cell at column 7 would add a false pull to the left.

I'm checking the sub's position in the window: pairs at columns 4–5, 5–6, and 6–7 keep it covered, but drifting to 3–4 or 7–8 breaks the turn signal. So the centering rule needs to fire at the edges, pushing the sub back toward the middle.

I'm working out the centering rule now: it should only fire when the sub is idle, so it doesn't pull the sub away from a turn it needs to make while firing at an enemy on the right. I'm checking how the centering units' logits compare with the fire baseline so they don't override it.

I'm settling the centering units next: a unit that fires when the sub is at the edge of the window and nothing is in its row, with the hold term suppressing it when an enemy is present, so it doesn't fight the turn logic.

Now I'm setting the surfacing unit to fire when the oxygen timer is low, comparing the oxygen-related input cells at the top of the sub's column against the ones at the surface, and I'm also tuning the scaling so it turns on at about the right point.

I'm setting the surfacing threshold: oxygen under 60 gives about 60 steps, and the trip up takes at most 8, so I'll trigger on column 2 for a safety margin.

Still wiring up the weights for the surfacing and T gating, now moving on to the R01 indicator and the sum unit.

Now I'm setting up layer two, which sums the per-row units into aggregate signals so the output can decide between moving up, down, and the other actions.

Now I'm laying out the second layer, which combines the per-row units into aggregate signals for the vertical and horizontal choices.

Now I'm setting the DOWN unit in the second layer: it pulls on the vertical signal and the hold term, and it's suppressed by the surfacing unit, with its weights pointing at the per-row units.

Now I'm writing out the weights for the second layer's UP unit, balancing the vertical signal and the hold term against the surfacing and row-0/1 suppression.

Checking the output-layer checks for the rows 0 and 1 case, and the case with the surfacing signal active, both of which keep the up and down units from firing when they shouldn't.

Checking the sign on the upward-movement weights now: the ΣV term enters with a negative coefficient, so its constant offset flips and the bias has to absorb a +48 rather than a -48.

Now I'm checking the DOWN unit's pre-activation: the vertical signal and the hold term pull it on, the surfacing term pushes it back off.

Now I'm tallying the constants for the DOWN unit: the vertical and hold terms sum to 6ΣV − 6ΣE − 6R01 − 10·SURF, with a bias of −5.8.

Now I'm setting the turn-right unit: its weight on each turn unit is 40, with a bias that puts it off in rows 0 and 1, where the turn signal should stay silent.

Writing the turn-left unit's weights now, with the pollution term from the right-side cells folded in.

Still wiring the CENTER_L unit: it takes the excitatory XR signal, is inhibited by the hold term and the rows 0/1 indicator, and I'm checking that it stays off when an enemy is pulling the other way.

Setting the output logits now: the fire action sits at a baseline of zero, and each movement logit gets a large offset so that it only wins when its layer-two unit is clearly on.

Writing the output-layer logits now: the left and right turn logits each pick up the centering unit with a small weight, and I'm setting the bias so both stay off when nothing is active.

Now I'm settling the weights for the right-turn unit in the output layer, mirroring the left side.

Still working out the output logits: the noop unit gets a strongly negative bias so it rarely wins, and the fire action stays at baseline zero. Left and right are set up as a pair with the same structure, so both turn directions get the same treatment.

Still working out the weights for the vertical units across columns 3 to 8, going row by row.

Still writing out the vertical weights for each row: the sign flips with whether the other row is above or below, and the weight shrinks with distance. Adjacent rows get a stronger repel from nearby enemies and bullets, so the sub won't step into danger there.

Still setting the vertical weights: the idle rows near the sub's position get small biases, and I'm checking whether row 3 would drift into a downward move.

Now I'm setting the weights for the V_2 unit: row 2 gets a strong positive term, and the rows below it push toward DOWN with a bias of -18.

Writing the vertical units for rows 0 and 1 now: each gets a strong self-activation with a bias of about -18, and a repel term from the row below in columns 3 to 8.

Now I'm working out the weights for the E_k units, which handle the enemies and divers in each row: a strong self-activation in the sub's own row, a repel term from neighboring rows, and a small push in the adjacent rows.

I'm checking the hold logic for enemies in the sub's own row: the weights make it stop descending, and the DOWN unit stays off. Then I'm worried about enemies in adjacent columns that the turn windows might miss, though the earlier turn should already have the sub facing them.

Now I'm setting the T-gating units for rows 2 through 8: each one is strongly on in its own row, with the weights tapering across columns 4 to 7 so the sub's facing direction is what decides whether it fires.

Still working out the T-gating weights: the facing check uses the back-column term, and I'm verifying the sign on the sub-facing-left case.

Now I'm checking the gate for each pair of columns, confirming that the bias offset is cancelled by the facing term so the sub only fires when it is actually turned toward the enemy.

I'm checking the combined turn logic: when an enemy is on the right and I'm facing left, the count reaches 2, so the sub doesn't turn, but the dodge still moves it vertically. Enemies on both sides cancel out, so I just fire forward. Next I'm setting the weights for the XR and XL units.

Now I'm finishing the centering units: the right-shift unit is tuned so it switches on once the sub drifts two or more columns right of center, and the left-shift unit mirrors that. Pressing toward the enemy when facing away just turns the sub without moving it, so the centering only matters once the facing is settled.

Checking the centering interplay now: at (6,7) facing right, pressing left just turns me to face left without moving, and the next press shifts me to (5,6). Layer-two is unused, so the remaining units don't matter. Next I want to check the vertical units when they're idle: a small negative drift from the other rows could still push them a bit, though it should stay negligible.

Still checking the gate scale: I'm bumping the per-cell weight to 15 with a bias of -30, so the inactive turn units sit firmly off even when many objects are present. The centering and dodge units should still saturate cleanly at that magnitude.

Now I'm checking the bullet case: enemy subs in an adjacent row only fire along their own row, so they're not a threat unless I drift into that row.

Checking the enemy's firing timer now: it shoots every ten steps, and its movement timer means it advances one column every six steps.

Now I'm tracing the timing of a single enemy sub approaching in my row: it fires every ten steps and advances one column every six, so the bullet catches up to me a few steps after I turn to face it.

Checking the diver pickup: I'm confirming that a diver only counts when it moves into the sub's front cell, not just when it shares the row.

Checking whether a diver counts from behind or from the front, and then whether enemies approaching from behind can be turned on in time. The turn window covers the outer columns, so an enemy at the far right can be met with a single turn before its bullet arrives.

Next I'm checking the unit indexing: the vertical units sit at 0 through 8, the T-gating units at 9 through 15, the enemy units at 16 through 22, and the R01 unit at 23, with SURF, XR, and XL after that.

Checking the output-layer weights: the DOWN unit sums the enemy and surface terms, and the arithmetic works out to 6v − 1.8 for the top two rows. For rows 2 through 8 the same sum gives a constant, which I'm verifying still stays on the right side of zero.

Checking the UP unit's signs for the surface case now: rows 0 and 1 sum to a value that stays well below zero when the surface term is off, so it holds.

I'm checking the sign and magnitude of the turn units for rows 2 through 8, and they come out to −40t − 30.46 with the bias term holding them off.

Now I'm setting the centering units: the CL and CR output weights, with the sub's x-position feeding them against the enemy and diver terms, and a bias of -30 to keep them off by default.

Writing the output weights for the action units now: DOWN gets a bias of -15 and UP a bias of 7, while the turn units and the centering units get their own small offsets so everything stays off by default.

Checking the dodge case next, specifically what happens when a bullet is already in my row.

Now I'm checking how a bullet already flying in my row affects the dodge units: with the enemy term at -1, the down and up choices overlap for mid-range heights, and near the top row only down stays active.

Now I'm checking the oxygen surface detection: the diver gauge cell at row 9, column 8 gives the index 593, and the one at column 2 gives 557, so the gauge reads correctly for both ends.

Now I'm writing the weight matrix for the first vertical unit, mapping each cell's channels into its input slots.

Still writing the first-layer weights for the vertical units...

Still writing the first-layer weights for the vertical units...

Still writing the first-layer weights for the vertical units...

Still writing the first-layer weights for the vertical units...

Still writing the first-layer weights for the vertical units...

Still writing the first-layer weights for the vertical units...

Still writing the first-layer weights for the vertical units...

Still writing the first-layer weights for the vertical units...

Still checking how the dodge and centering units respond as the sub moves between rows 6 and 7.

Still writing the first-layer weights for the enemy units...

Still writing the weights for the trigger units...

Checking the case where an enemy that has already passed my sub sits in the column just to my right: its trail would push the turn units toward turning right, which could lead me straight into it.

Still writing the weight entries for the R01 unit...

Still writing the weights for the surface and oxygen units...

Checking the starting phase: at row 0 facing left, the danger term is zero, so the down unit fires and the sub descends through the top rows. Once it reaches row 2, the enemy hold takes over whenever something sits in that row. The plan after that is to hunt until oxygen falls below about 60, then surface for a diver.

Still checking the sign of the UP unit once the surface flag is on, so that the sub keeps rising past row 1 to the surface.

Sticking with 'up' is the risk here: if the sub is ascending from row 3 and the sticky repeat fires, it can carry the sub into row 1, and a second repeat would take it to row 0 where it dies without a diver.

Now I'm weighing how the sticky-action risk adds up over a long episode, since each ascent into row 2 carries about a 1% chance of pushing the sub to row 0. Moving the top playing row up to row 3 might keep that risk out of the picture.

I'm weighing whether to give up row 2 entirely, since a sticky repeat that pushes the sub from row 2 to row 0 would kill it with no diver aboard. Row 2 targets are roughly an eighth of the spawns, so skipping them costs something, but a 1% death risk per ascent piles up over a long episode and could wipe out most of the score.

I'm checking the sticky-action risk for the turn units too: if a turn right is repeated while an enemy is sitting in the column just ahead, the sub could step straight into it. Centering should correct the drift afterward, but that single step is the danger.

I'm checking the enemy-in-column-7 case once more: if I turn while an enemy sits at 9 and then a sticky repeat steps me to 7, I should still have time to fire and clear it, so the risk seems small. Centering should pull me back afterward. Firing at divers is harmless since bullets pass through them, and I'm now looking at whether the enemy hold still applies when a diver sits in my row.

I'm checking whether an enemy's bullet in my own row triggers the dodge too, even when the enemy sub is far away and I was planning to shoot it first, since the combined term would still come out at -1 and push me out before I can fire.

I'm checking that a bullet from a distant enemy sub in my row still triggers the dodge, which seems right since it's coming toward me unless it's moving away. The turn units only read bullets with the weight on that channel, so the combined value stays low enough that I won't turn. Next I'm confirming the vertical and enemy windows both cover columns 3 through 8.

Checking the output signal magnitudes against the gating thresholds: the vertical units sit around -30 plus bias and a small signal, the enemy units around -12 at most, and the turn units stay near -30, so none of them fire by accident. The extreme column values also keep the turn inputs in a safe range.

Checking the turn threshold: the turn activation is tanh(0.4x), and since the weights are integers, x lands on whole values. At x=3 the turn fires strongly, while at x=2 it stays off, so the gate separates cleanly.

Checking the output gates: the turn unit fires at x=3 and stays off at x=2, and the off-state values for the other units keep the fire action dominant when nothing else is active.

Checking the centering behavior for when the sub sits in rows 0 or 1, where the enemy term is zero, the left-side logit still comes out positive enough to turn left confidently.

Still working out the turn thresholds and the output gating for the sub's movement.

Still writing the first-layer weights for the vertical units...

Still writing the weights for the vertical units...

Still writing the weights for the vertical unit that handles row 4...

Still writing the weight entries for the vertical units...

Still writing the weights for the V_8 unit...

Still writing the weights for the turn units...

Still writing the weights for the enemy units...

Still writing the weight entries for the enemy and vertical units...

Still writing the weights for the surface and oxygen units...

Still writing the weight entries for the vertical and enemy units...

Still writing the weights for the turn and enemy units...

Checking how the enemy sub in row 4 would pull the sub upward from row 6, I'm tracing its signal through the vertical unit and getting a value that tips it into moving up.

I'm checking that the enemy-hold and turn logic cover the case where an enemy sits a few columns ahead in my row, and I'm concluding the sub will turn and fire in time. I also want to see whether an enemy that gets past the adjacent column without a turn could reach the sub, so I'm going over the timing for that edge case.

Writing the output-layer weights for the movement actions now...

Still writing the layer-2 weight entries...

Still writing the layer-2 weights and the bias terms for the turn and enemy units...

Still checking the output-layer weights and the bias terms for the surface and turn units.

