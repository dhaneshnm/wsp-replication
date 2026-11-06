I'm figuring out a hand-crafted policy for MinAtar Seaquest without being able to run anything, so the strategy has to fit within the network's constraints. Trained DQN agents reach fairly modest scores here, so a simple heuristic of holding a depth, shooting enemies, grabbing divers, and surfacing when oxygen runs low seems like a sensible target.

I'm weighing a simple fixed strategy against the oxygen limit, since never surfacing caps the episode at about 200 steps. Staying in one row only catches a fraction of the enemies, so I'd need to move between rows to pick up divers and extend survival.

I'm turning to a position-invariant design, since the sub's location shifts and 32 hidden units make that awkward. Tracking enemy bullets from enemy subs in my row looks like the main danger.

I'm checking whether bullets from enemy subs can be dodged, and noting that enemy subs facing away from me are harmless. I'm also considering that staying at the surface row from the start is safe, since termination only happens when I drop below and come back up without a diver.

I'm settling on a baseline: sitting at the surface row is perfectly safe, since nothing spawns there and oxygen doesn't drain, but it also scores nothing. Shooting from row 0 is pointless because the bullets stay in that empty row, so any real scoring means diving, which brings the oxygen clock and the need to surface with divers back into play.

I'm now sketching a vertical-tracking policy: for each row, a hidden unit would fire when the sub sits above that row and a target is present there, pushing the sub down toward it.

I'm settling the vertical-tracking idea: one unit per row fires when the sub is on one side of that row and a target sits in it, so the net push points toward the majority of targets. When the sub is already level with a target I'd want it to hold and move sideways toward the diver, but that makes the design more involved than I'd like.

I'm weighing where the scores for this kind of agent usually land, comparing DQN results on MinAtar Seaquest with simpler methods. Since death is common, the policy has to prioritise avoiding enemy fire and sub collisions over chasing points.

I'm considering a fixed-direction shooting approach, since the sub's facing decides where its bullets go. Enemies approaching from behind could still hit me, so I'd need to account for that before settling on a row.

I'm checking the spawn timing against the edge columns: a fish appearing at x=0 in my row would land on me, so starting at the far left looks risky, and I'm weighing whether a middle column facing right would avoid that.

I'm checking whether starting at column 1 avoids the spawn at the edge, but I'd still have to turn to face an approaching enemy, and turning means moving, so orientation and position can't be changed independently.

I'm weighing a column-fixed design where the sub stays put horizontally and moves only vertically toward rows with divers, since divers drift across the whole screen and will reach a sub sitting in their row. The open question is how to handle enemies that approach from behind.

I'm picturing the sub fixed in one column and only moving vertically, which keeps its facing unchanged. Putting it on the right edge facing left looks deadly, since a fish spawning at that column in the same row would hit it immediately, so I'm checking whether column 8 avoids that while still giving me warning before an enemy from behind arrives.

I'm working out a fixed-column design where the sub stays at column 8 facing left, so the only threat from behind is an enemy spawning at column 9 in its row, which I can spot and dodge by moving vertically. That turns the danger check into a simple per-row rule, while enemies coming from the front are handled by shooting.

I'm working out how fast enemy-sub bullets reach my column compared with my own shots, since a sub spawning in my row fires about every 11 steps and its bullets move one cell per step toward me.

I'm checking the collision order between our bullets and enemy subs: since our bullet moves before the enemy, a bullet heading toward a sub registers a hit whether the sub is stationary or moving toward it.

I'm reasoning about how fast enemy bullets reach the sub's column, and noting that a constant fire pattern clears any enemy sub in front of me within about ten steps of it entering my row. The risk is an enemy sub that's already in place and firing toward me, so I'd want to watch the danger channel for incoming bullets.

I'm weighing whether a fixed column 8 facing left would work, since that leaves the enemies from the right side as a threat I can't shoot. The danger there is an enemy from behind, so I'd have to leave the row as soon as one shows up, and I'm still working out how to get the sub into that column in the first place.

I'm working out how to get the sub to column 8 facing left: it's at column 5 now, so I'd move right, but moving right at column 8 flips it to face right, which breaks the setup. Going to column 9 and then stepping left seems to land it at column 8 facing left, so I'm trying to write a rule for horizontal control that gets it there.

I'm working out the horizontal rule for the sub: if it's facing right and not yet at the right edge, it keeps moving right, and at the edge it steps back left. If it's facing left and still left of column 8, it moves right to turn around, and at column 8 facing left it holds.

I'm checking how the player channel marks the sub's front and back cells, and noting that the trail channel is what tells them apart when the sub faces right at the edge.

I'm working out how to tell the sub's front from its back when it faces right at the edge. Enemy trails in column 9 could mislead a simple sum over the player channel, so I'm checking whether any per-cell combination of player and trail can separate them.

I'm considering whether a fixed column with both orientations would be ambiguous, since a sub facing either way occupies two cells. I'm settling on the back-cell trail as the way to tell them apart, accepting that enemy trails in the same column might occasionally muddy it.

I'm weighing whether the sub can simply hold a rightward heading and skip any explicit facing control: if there are player cells in the left columns, keep pressing right until it settles at column 9 facing right. That leaves the orientation to fall out of the horizontal rule rather than being set on purpose.

I'm settling on a horizontal rule where the sub keeps pressing toward the target and only steps left at the edge, so orientation falls out of position. The remaining question is telling a sub at column 8 facing left from one at column 9 facing right, since both occupy the same two columns.

I'm checking whether a sub at column 8 facing left can be told apart from one at column 9 facing right, which the cell counts alone can't do. The plan is to press left only when the trail sits in column 8. A plain sum over the trail and player channels would false-trigger on an enemy trail in another row, so this needs a stricter test.

I'm weighing the trail-at-column-9 check against the one at column 8: the column-9 version avoids most false positives, since an enemy trail there only shows up when an enemy has just left the edge. Still, it's a judgment call about how often that happens.

I'm settling on a rule that presses right whenever any player cell sits in columns 0 through 7, since a facing-right sub at column 8 has its back in column 7. The question is whether a trail check in column 9 gives a safer left-press signal than one in column 8, and I'm leaning toward column 9 because a false negative only delays the turn, while a false positive would send the sub backward.

I'm defining the left-press unit so it fires only when the sub sits at columns 8–9 with no trail in column 9, since that tells me it's already facing right at the edge. Working through the values, the unit comes out strongly positive in that state and negative once an enemy trail appears in column 9.

Now I'm checking the vertical threats for a sub holding column 8 facing left: an enemy spawning at column 9 in my row would be a danger at my back cell, and it would reach my column in about six steps, so I need to leave that row within five.

I'm checking how an enemy spawning behind the sub at column 9 would threaten it, and I'm working out the timing for leaving that row. Enemies moving right in my row are handled by the continuous firing, but I'm checking whether one already sitting at column 7 slips past, since the bullet only reaches it at that column.

I'm checking the enemy threats in the row I'd enter: a sub already moving right fires after a delay, so I need to get there before its bullets arrive. An enemy moving left that's already ahead of me is moving away, so my bullets can chase it while its shots go the other way.

I'm now looking at vertical hazards: moving into a row where an enemy sits at the sub's column, or where one is about to slide onto it, is an instant collision. Divers moving right will reach column 8 eventually, so I need to be in their row when they arrive, and divers spawned at column 9 moving left are the other case I'm still working through.

I'm now checking the oxygen budget: with 200 steps total and one diver collected, surfacing refills air and drops the diver count by one, so I'll plan surfacing to happen while I still have at least one diver aboard.

I'm working out when to surface: the oxygen gauge drops in steps, and surfacing is only safe while I still have a diver aboard, so I'll plan the trip up for that window.

Now I'm estimating the expected score: enemies spawn roughly every 21 steps, and about half come from the left where the front-facing shots can reach them.

I'm deciding which rows to move toward by looking for reward-channel content in the columns in front of the sub, while steering clear of danger cells. Divers moving right will drift into the sub's column on their own, but one moving left is already pulling away, so I can't simply chase it there. Telling those two apart would need the trail cells, which makes this part harder to pin down.

I'm sizing the network: layer 1 has 32 units and layer 2 has 32 units, so layer 2 can combine layer-1 features with ANDs. For the vertical choice, I'm considering a per-row desirability score, which would need row-specific features that layer 2 can combine.

I'm sketching the vertical part of the network: for each row, a unit that reflects how desirable that row is from the reward cells in front of the sub, and separate units for the dangers, so layer 2 can combine them with the sub's row.

I'm settling on a per-row encoding for the sub's vertical position: a graded unit that scales with the row index, which layer 2 can then compare against thresholds to tell whether the sub is above or below a given row.

I'm working out the numbers for encoding the sub's row: tanh(0.1·r) for r from 0 to 8 spreads the values enough that adjacent rows differ by about 0.06, so a large gain in layer 2 could separate them. Since the row encoding ignores column position, it should stay stable as the sub moves sideways. I'm also weighing whether to use a single graded unit or several threshold units, one per row boundary.

I'm weighing how to split the network's 32 units between row-content detectors and a graded row encoding for the sub's position. Layer 2 could then AND those together, which would let me handle the danger-avoidance rule first: if the current row is threatened, move to whichever adjacent row is safe.

I'm still settling the priorities: avoiding danger comes first, then surfacing for oxygen, then steering toward targets, and firing otherwise. I'm also checking shot cooldown from friendly bullet positions in my row, since a bullet within the last few columns means I can't fire yet.

I'm making the danger term per row: a unit that fires when cells in that row near column 8 contain danger, weighted so the nearby cells count more than the farther ones.

I'm working on a band detector for the sub's row: a single layer-2 unit can't isolate one row from a graded position value, so I'm considering two threshold units, one for "at or below row r" and one for "at or below row r+1", and subtracting them to get a narrow band that I can gate with the danger unit for that row.

I'm now trying to put a per-row danger check directly into layer 1, so that each row's unit fires only when the sub is in that row and danger is present there. Since the inputs are binary, that conjunction can be done in one layer, but it needs a separate unit for every row to avoid cross-row contamination.

I'm weighing whether each row's unit can encode "sub is in this row and danger is present," which would need a separate unit per row. I'm also considering whether one unit per row could capture the danger above and below together, so the next choice of direction is settled in the same step.

I'm now setting each row's unit to act as an urge to move up or down, gated so that only the unit for the sub's current row is active, with inactive rows pushed to a constant offset that the next layer can correct for.

I'm setting each row's unit up as a gated AND: it sits near -1 unless the sub is in that row, and only then does it output +1 or -1 depending on whether the linear condition holds. Summing the sub's cells across all columns of a row keeps that gate independent of horizontal position.

I'm settling on the row-0 start: sliding right to column 8, then diving once row 1 is clear. Each row's unit can be gated on the sub being in that row and then pick a direction, but the surface row needs its own handling since the dive comes first.

I'm working out the decision rule for a sub at row r, looking at the danger cells in the rows above, at, and below it, and how each row's unit should gate on the sub's position.

I'm checking whether an enemy in the sub's row that's moving right will reach column 8, since that's the danger case. Shooting it could stop it, but I can't be sure a shot is ready, so I'd need to look at the trail cells to tell approaching enemies from ones moving away.

I'm checking how a bullet in my row at column 7 or lower could be a threat, since bullets carry no trail to show their direction. Enemy subs shooting left would send bullets away from me, so telling them apart from bullets coming my way is hard. I'll simplify the danger check for the current row rather than try to resolve that from bullet positions alone.

I'm checking whether danger in the sub's row, either a bullet or an enemy a couple of columns back, could reach column 8 in time, and working through how far a bullet moves per step against how far I can dodge.

I'm checking bullets in my row: one at column 6 or 7 moving toward me means I should step out, since it reaches column 8 in a couple of steps, though sticky actions make a margin worthwhile. Enemies that are moving right but still at column 7 I could shoot, yet I'd rather leave the row, since I'll have been firing at them anyway if I'd been in that row for a while.

I'm settling on treating danger at column 7 as a threat that requires leaving the row, since telling a right-moving enemy from a left-moving one isn't reliable here. I'm also weighing whether to shoot instead, but the shot-readiness check makes dodging the safer choice.

I'm checking which target rows are safe to move into: a row is ruled out if danger sits right on the sub's column, or an enemy or bullet is about to move onto it.

I'm checking whether a row is safe to enter, which means no danger in columns 6 through 9, and I'm treating danger at column 9 as a threat even if it's moving away. For the current row, I'm weighing whether danger at columns 6 or 7 should force me to leave, since a fish moving right from further back would take several steps to arrive and my firing could handle it.

I'm going to leave the row when danger shows up at column 6 or 7, even if it's moving away, since the shot might not be ready. Enemies at column 9 count as danger too, while a diver there is just a reward, so I'll keep the two separate when I pick a target row.

I'm sorting out how to weigh the rewards against the dangers in each row, with divers counting for more than enemies and bullets counting against. The remaining question is whether a diver moving toward me can be told apart from one moving away.

I'm settling on a per-row navigation rule: each row gets its own unit that scores moving up against moving down, with the score weighted over the whole board and only active when the sub sits in that row. Since the player-row gate handles the separation, each unit can take the full board as input, which means the desirability of rows above and below can be compared directly.

I'm weighing whether a single linear score per row can capture both the urge to escape danger and the pull toward rewards above and below. I'm considering adding a large penalty for danger in the row above and a bonus for danger in the current row, though a single threshold can't express every combination exactly.

I'm turning each row's up and down scores into a weighted sum: the current row's danger pushes both ways, a dangerous row above penalizes going up, and the same logic applies to rows below for going down. Attraction from the other rows gets weighed against the current one so the sub heads toward reward only when that neighbor is safe to enter.

I'm setting the output weights so that each row's up and down logits are driven by its gated score, with a constant fire baseline, and I'm compensating for the inactive rows by adjusting the bias so the sum over gated units still works out.

I'm settling the row-1 rule: moving up to row 0 only makes sense if a diver has been collected, and mostly when oxygen is running low.

I'm settling the up-move for when oxygen runs low: a term that's positive only when I already hold a diver and the oxygen gauge reads below the threshold, so surfacing is favored in that case.

I'm working out the surfacing urge as its own unit: it should fire when I hold a diver and oxygen is below the threshold, and then combine that with the per-row checks so going up is only allowed when the row above is safe.

I'm adding the surfacing signal directly into each row's up unit as a linear term: positive when I hold a diver and oxygen is low, mildly negative when I have no divers and plenty of oxygen, and neutral otherwise.

I'm working out the row-1 surfacing unit: it needs a huge negative bias so it never fires unless I hold a diver, and then the diver and oxygen gauge cells decide the urge. I'm checking how the diver bar maps to cells 3 through 8 and whether an oxygen reading of 60 is too early a threshold, since surfacing takes at least eight steps.

I'm settling the threshold for surfacing: waiting until oxygen drops below 40 leaves enough margin to climb the eight rows and dodge, even if danger slows me down.

Now I'm checking how the diver count gates a surfacing urge: at six divers the oxygen bar converts to a bonus worth up to about ten points, so surfacing then is worth pushing for, and the diver-count cell is the trigger I'd key that on.

I'm checking the surfacing term again: a diver-count gate paired with the oxygen gauge, so that at six divers the surfacing urge fires regardless of oxygen level. The sign of the diver-count contribution still needs to be confirmed before I settle the weighting.

I'm working out the rule for row 0: diving is worth it when row 1 is clear, and the surfacing urge shouldn't carry over once oxygen is reset to full, so I'd just dive. I also need to make sure pressing up at row 0 doesn't count as a surface again, since it already has.

I'm noticing a problem with sticky actions: if the sub moves up into row 1 with no divers, a repeated up press could carry it into a fish. So I'd penalize the row-2 up move when no divers are held, letting it fire only when escaping danger is the sole option.

I'm weighing whether to penalize the up move from row 2 when no divers are held, since a sticky repeat could carry the sub into row 1 and into a fish. I'm leaning toward a moderate penalty rather than a hard block, so escape upward still stays available when it's the only safe option. I also want to check the case where the sub reaches row 1 by diving with no divers, since a repeated down press from there could be just as risky.

Now I'm sorting out how the attraction score for each row gets built from its cells, starting with divers and the danger weights that go alongside them.

I'm now weighting each cell in a row: divers count as reward with a small danger offset, enemies end up mildly positive, and enemy bullets come out negative. I'm also scaling the value of cells by their distance from the sub, so nearby rows matter more than far ones.

I'm weighing whether to build the weights unit by unit with row-wise fills, or to find a more compact layout, since writing every cell out would take hundreds of lines.

I'm laying out the network in layers: row-wise attraction and danger features, a one-hot for the sub's current row, and then a second layer that gates each row's up and down decisions on the sub's position.

I'm comparing the cost of the layers now: the row-wise features go in the first layer, and the second layer uses per-row gates over the sub's position, which makes the up and down decisions linear within each row.

Still writing the layer-one weight blocks...

Still working out the row-level features: I'm settling on a binary signal per row, saturating the attraction score so each row is simply "interesting" or not, and checking whether that loses too much when several targets sit in one row.

I'm settling how the attraction score treats rows with enemies: an enemy in the current row is worth staying to shoot, while a diver moving away adds nothing useful. I'm also setting enemies in column 9 to count as danger, so they don't pull the sub toward them.

Still writing the layer-two gating for the up decision...

Still writing the layer-two gating weights...

I'm settling the danger weight at 14 so it outweighs the attraction terms, since an escape move has to win even when the other direction looks rewarding. The down-surfacing penalty then needs to stay small enough that danger still lets the sub dive out. The catch is that when danger is present and both directions are safe, the up and down units both fire with equal strength, so the choice comes down to noise.

Still working out the down-move gating for each row, and checking how the row-1 up unit should be penalized when no divers are held.

Still working out the horizontal side: I'm deciding whether a left or right nudge should be allowed while the sub is in danger, and I'm checking the case where it's sitting at the edge with a diver drifting left in its own row.

I'm thinking about whether a diver moving away could be told apart from one moving toward us by its trail, since a diver at column 7 or below with a trail on its right would be drifting left. A single linear cell weight can't tie the trail to the right object, though, so I'm leaning toward ignoring direction entirely and accepting some wasted waiting.

I'm now checking whether a diver moving away versus toward can be told apart from the trail, but the trail is ambiguous, so I'm leaning toward ignoring direction. Enemies moving away should still be caught by bullets, while divers drifting away will just waste some waiting time.

I'm working out how to tell a diver moving away from one moving toward me, since the trail might show direction. For divers at the far column, I'm weighing whether to discount the reward channel to cut down on wasted waiting.

I'm checking whether a diver in my current row that's drifting away would still be worth waiting for, since the trail alone doesn't reveal its direction. I'm weighing whether the stay weight for that row should be lowered, but enemies in the row still justify staying, so I'll keep it as is and accept some wasted time.

I'm checking whether a diver moving away could be told apart from one moving toward me using the trail. A linear sum of column positions weighted by trail versus reward would come out to +1 for a receding object and -1 for an approaching one, which would be a cheap way to separate them, though I still need to handle the edge case where a diver at column 0 leaves no trail to its left.

I'm testing whether a signed sum of column positions, weighted by trail minus reward, can tell a receding diver from an approaching one in a single row. The edge cases, like objects at column 0 or 9 with no trail to one side, make the magnitudes unreliable, so I'm leaning toward keeping the row-level signal coarse and skipping the trail-based direction check.

I'm weighing a reward-minus-danger trade-off: if each diver and enemy carries a trail, a signed sum over columns could separate approaching from receding objects. The catch is that enemies moving away are still worth chasing, so I'd want the weights to work out so that receding enemies stay positive while receding divers come out near zero.

I'm testing whether a per-row trail-versus-reward sum could tell approaching objects from receding ones, which would let divers and enemies be scored differently. I'm settling on a reward weight of 2 with no danger term near the sub, so diver and enemy both come out at roughly 3.5 when approaching and 0.5 when receding.

I'm working out a sign convention for the trail: the trail weight at each column is negative and the reward weight positive, so a receding object scores differently from an approaching one. The catch is the sub's own back cell, which sits at column 9 and would pollute its row, so I'm dropping the column-9 trail term.

I'm checking whether a diver moving away can be filtered out by the trail: a diver at column 8 that just moved left from column 9 leaves a trail I'd have to exclude for column 9, since the sub's back cell lives there. With that column dropped, a diver right next to me still reads as attractive, and stepping into its cell picks it up anyway, so that case is fine.

I'm weighing a per-row trail weight that scales with column position, so that the sub's back cell at column 9 doesn't contaminate its own row. Column 9 would get no trail term, which keeps the sub's row from being skewed, and I'm checking that a transient trail at column 8 is harmless. Spawn-side enemies at column 9 would still come out negative once the danger weight is large enough.

I'm checking the sign of the trail-versus-reward terms on both edges, with the danger weight set to -30 at column 9 and -3 at columns 6 to 8, so that a diver or enemy just spawned at column 0 comes out at a neutral 2.

I'm settling the column-8 case: I can cancel the trail term there so a diver just leaving column 9 doesn't read as hugely attractive, which keeps the row score from spiking while the object is still moving.

I'm setting the reward weight at column 8 to 2 instead of 14, since a fish there moving right would come out at -8.5 and that's fine. For column 9, a diver spawned moving left should be very attractive at about 15.5, while one coming from column 8 would sit around 3.5, which is only mildly attractive.

I'm checking the reward weights at the edges, where a spawned diver at column 9 comes out at 8 and an exiting one drops to -4. For the row score I'm using a tanh squash centred on 1.5, so a lone receding object lands near -0.96 and an approaching one near 1. Summing several objects in one row should push it toward attractive.

I'm checking the row-level weights near the edge, where the sub's back cell at column 9 is excluded from the trail term, and I'm also making sure bullets in the mid-columns don't shift the scores. Then I'll turn to which rows count as unsafe, starting with the danger channel from columns 6 through 9 and whether column 5 needs to be included too.

I'm checking whether an enemy moving left in row 6 or 7 should count as unsafe, since a bare danger check would flag it and make me skip a likely kill. The trail could tell a receding enemy from an approaching one, but bullets have no trail, so I'm leaning toward keeping the unsafe check simple for now.

I'm checking whether a danger at column 9 that is moving right, an enemy that spawned at column 0 and has already crossed the row, would still count as unsafe, since the danger channel alone would flag it even though it is leaving.

I'm working out how the sub's own row gets flagged: a tanh gate on the summed player cells should read near +1 when the sub is in that row and near -1 otherwise. I'm also checking the edge case where the back cell wraps around to column 9 if the sub is at column 0 facing right.

I'm assigning the observation channels to units: nine self-row gates, eight reward-row units, eight unsafe-row units, plus diver, surfacing, and left/right heading units, leaving three spare.

I'm setting the surfacing unit's gain so it fires once the sub is carrying a diver at full capacity or when oxygen is low, and I'm wiring the diver-held flag as a sharp on/off signal. Next I'm defining the heading units, which check whether any of the sub's cells sit in the left or right half of the board.

I'm checking the horizontal-position unit, where the left-heading check counts the sub's cells in the right half and the trail at column 9 against the sub's own back cell, which should keep it negative at home and positive on the right edge.

I'm laying out the output layer now: 16 units for the up and down moves across the rows, plus two relay units for the horizontal moves, so 18 in total. I'm working out the logit weights so that the inactive units cancel out properly.

I'm settling the output layer scaling: moving the up-action logit to 6 times the sum of the up-row units plus a constant 48, so an active up unit gives 12 against a fixed fire logit of 6.

I'm settling the row-0 down action: I'll gate it off whenever a horizontal move is active, so the sub goes sideways first instead of diving early while it's still near the left edge.

I'm now setting up the layer-2 up-action unit for each row, converting the layer-1 outputs into indicators so the weights can be written as simple coefficients on the row gates.

I'm writing out the layer-2 preactivation for the up-action unit in each row, with the self-row gate, the reward and unsafe terms, and a penalty for having no diver.

I'm working out the up-action unit's weights: a surfacing bonus of around 12 so surfacing overrides the attraction from rows below, and a matching -12 on the down units. The danger-escape term for downward moves would then drop to a small positive value, so I'm checking whether it still beats the penalty.

I'm weighing a lower attraction weight for the rows above, around 2 for the nearest and tapering to 1, so the total pull from above stays small. Then I'll raise the danger escape weight to 16, since with the surfacing penalty of 8 and the bias the downward move still needs to clear zero when the sub is threatened.

I'm checking the unsafe-row gate: with a larger penalty of 40 for stepping up into an unsafe row, the sum of danger, surfacing, and attraction terms can't push that move positive, so the sub won't climb into a row it would die in.

I'm settling the layer-1 gains so the self-row and unsafe-row outputs saturate cleanly near ±1, using a larger scale inside the tanh so small rounding errors in the weights don't swing the logits.

Still tuning the down-action weights: the row-0 dive unit needs its own treatment since there's no row above it to check.

Checking whether row 0 is actually safe, since enemies only occupy rows 1 through 8, so the dive term for row 0 can be a plain base value.

Now I'm checking how the sub behaves in a row with nothing attractive nearby: the up preactivation comes out around -1.5, so that move stays mostly off.

I'm bumping the attraction weights up, starting with a1=4, so that an attractive row just above gives a clear preference for moving up instead of a near-even split with firing.

I'm tuning the attraction weights to a1=4, a2=3, a3=2.5, and a4 and beyond at 2, then bumping the surfacing override to 20 and raising the danger weight to 30, so the escape and surfacing terms still hold against the summed attraction from below.

I'm rechecking the scale of the unsafe-row penalty and the gate offsets, and settling on the layer-1 gains so the up and down outputs stay crisp. For the danger signal I'm using a tighter gain so the row-level outputs saturate cleanly.

I'm now checking the sticky-action risk: when there are no divers, moving up into row 1 could be fatal, since a repeated up action would surface the sub with nothing aboard.

I'm now working through the escape case for row 2: with no diver aboard, the upward penalty from the missing-diver term is large, so the danger weight of 30 minus that penalty leaves the up move from row 2 suppressed.

I'm checking the row-2 up penalty: setting it to 28 leaves the escape preactivation near 0.5 plus attraction, while down-escape sits near 28.5, so down wins whenever both are safe, and up only fires when down is unsafe.

I'm settling the sticky-action risk for row 1: without a diver, an up move into row 1 could repeat and surface the sub with nothing aboard, so that entry needs a heavy penalty. I'm also noting that enemies moving rightward from the left are the ones worth chasing, since receding ones score low.

I'm checking how the attraction terms should scale with distance, and whether receding enemies are worth chasing too. Left-spawned enemies take roughly 54 steps to cross, so they're easy to catch; each kill is worth about one point, and receding ones should count the same, since a bullet closes on them quickly.

I'm now weighing the danger channel for distinguishing enemies from divers, giving enemies a bigger weight than divers in the approaching and receding cases. The open question is whether enemy bullets alone in a row should count as attractive, since they carry no reward and could pull the sub toward empty lanes.

I'm working through the reward channel as 2 + 1.5c, minus a trail term, plus a danger bump, to see how well enemies separate from divers and bullets. A receding enemy lands around 2.0 and a bullet around 1.5, while an approaching diver is much higher; I'm weighing a threshold of about 1.75 with a gain of 3 to pick out the enemies.

I'm settling on a scheme where enemies get a larger reward weight plus a danger weight, while divers only get the reward and bullets only get the danger. That should let a receding enemy stand out from both a diver and a stray bullet.

I'm settling the danger weights by column: a small positive weight for columns 0 through 5, a negative one for 6 through 8, and a heavy penalty at column 9. For objects entering from the left, a diver scores around 2.5 and an enemy around 3.5, so both are attractive, though an object already moving left drops the diver's score to about 1.

I'm settling the reward weight for each column as 2.5 plus 1.5 times the column index, and the trail penalty as negative 1.5 times the column, so each object's score tracks how close it is. For column 8 the numbers come out lower for receding objects, so they drop out of the attraction, while an approaching one still scores high enough to matter.

I'm settling the reward weight for column 8 by the same formula, and I'm checking what that does to receding objects at that edge, since their trail would fall outside the board.

I'm settling the danger weights so columns 6 and 7 get a mild penalty, column 8 a strong one to cut attraction there, and column 9 a heavy penalty. For the reward at column 9, a diver entering from the right scores high, but one already moving right would only be exiting, so it's a weak target.

Next I'm setting the reward weight for column 9 at 10, so a diver spawned there scores high while one already exiting drops to about -2. I'm also keeping the trail weight at zero for the sub's back cell, since it shouldn't pull the score either way. Then I'm scaling the reward-row preactivation by 3 and offsetting it by -4.5, which means folding the weights into layer 1 and setting the bias to match.

Now I'm scaling the per-column weights for reward, trail, and danger by 3, so the cells line up with the bias I already set.

I'm checking the reward numbers for enemies and divers at column 5 with the trail and danger terms included. A receding enemy there lands at about 1.5, which is borderline attractive, while a receding diver sits well below zero. Two bullets together would also push the score above zero, which is a concern I'm still weighing.

Checking the attraction terms at columns 6 and 7: an approaching enemy there lands below zero because of the danger penalty, which is fine since that row is already flagged unsafe. An approaching diver at those columns still scores around 12, so it stays a strong target.

I'm working out the unsafe-row term for the upward move: a penalty of ten times the summed danger across columns 6 through 9, minus five, so a row is only flagged when an object sits in the right-hand columns.

I'm checking the sticky-action case for the unsafe row: if the previous move was up, repeating it still takes the sub out of the row, so a 10% sticky step doesn't trap it there. Bullets crossing from the left should be caught by leaving the row once they reach column 6.

I'm checking how sticky actions interact with the escape moves: repeating a vertical move still leaves the row, and holding fire just delays the exit by a step, which is fine. I'm also confirming that an enemy spawning at the far right can't reach me the moment I step into its row, since it takes several steps to start moving.

I'm checking the hazard for an enemy sub sitting behind me in my row: if it fires as I enter, the bullet spawns on its own cell and steps into mine on the same tick, so that spot is more dangerous than the danger weights alone suggest.

I'm checking the case where an enemy sub on the right moves left and fires: its bullet spawns on its own cell and only reaches me later, so the early steps are fine. The real risk is an enemy sub moving right at column 6, whose bullet closes in one cell per tick, so I'd need to leave the row as soon as a bullet reaches column 7.

I'm checking the escape rule near the edges: with a diver aboard, moving up into row 0 means surfacing, which costs the diver, so I'd only do that when a danger forces the move. From row 1 the upward escape from a threat is still the right call, since it's the only way out.

I'm checking the softmax noise at row 1 without a diver, since a logit near zero for up against fire's 6 would still give roughly a quarter-percent chance per step of stepping into row 0 and surfacing. Over a long stretch that adds up, so I'd want the up logit pushed far negative whenever I'm in row 1 with no diver aboard.

I'm scaling the logits so the desired actions carry much larger values, with fire's baseline at 10 and the desired moves reaching about 20, so random non-fire actions become negligible over long episodes. I'm also planning an explicit negative term on the up logit whenever the sub is in row 1 without a diver aboard.

I'm adding a separate layer-2 unit that blocks the up move whenever the sub is in row 1 without a diver, so random noise can't push it up to the surface. I'm also making the horizontal relay units pass through a steeper tanh.

I'm checking the horizontal relay units: the right-move signal comes out near 22 when active and close to zero otherwise, and the fire baseline sits at 10, so the moves won't clash. Starting at (0,5) facing left, the sub crosses to column 9, then the back-cell trail term stays at zero, so it turns around and heads left. The open question is what happens when the sub is at column 9 facing right with a trail on that same column, since the left relay would then be switched off.

I'm checking whether a sub sitting on column 9 can be hit at spawn, since an enemy appearing on the sub's own cell would be a collision. I'll also gate the down move at row 0 on the horizontal relay signals, and watch for a case where repeated left presses at row 0 bounce the sub right and back again.

I'm rechecking the attraction distances: a fish one cell away scores about 4, three cells away about 3, and farther out it drops to about 2, with the sum still accumulating linearly.

I'm now settling the scoring gaps for the attraction terms, since with near-equal values the sub would stall between two targets. Giving nearer objects clearly larger weights, roughly 8 for distance one down to 2 beyond four cells, should let the up-or-down comparison pick a direction decisively.

I'm settling the scoring constants now: a stay weight of 10 for an attractive current row, and a danger weight of 40 so it outweighs any attraction gap. The surface and down-penalty terms also get 40, which should keep the sub from choosing down when escape up is available.

I'm now checking the down-escape case: danger weight 50 against a surface penalty of -25 still leaves a small margin, so I'm working out whether down can still win when up is blocked.

I'm setting the constants for the gating units so the unsafe-cell and surfacing signals clearly dominate the attraction terms, with the down-escape still able to win when up is blocked.

I'm recalibrating the row-2 escape: with the danger weight at 50 and the no-diver up penalty at -48, the up move only edges out the attraction terms by a small margin, so I'm checking whether down still wins when the lower cell is safe.

I'm working out the up-escape at row 2 without a diver: a penalty of -56, with a +10 boost from the row-3 down-blocked signal, gives a net around 2.5 plus the attraction term, so I'm checking whether that still leaves room for down to win when the lower cell is safe.

I'm now weighing the row-2 up escape without a diver: a penalty of -50 would leave its net score near zero, so I'm checking whether that margin is enough for the move to win only when it's truly needed.

I'm going to make row 1 unattractive when there's no diver aboard, by building the gauge check into the row-1 attraction unit itself, so the up moves don't need a separate conditional penalty.

I'm making the row-1 attraction unit depend on the diver gauge, so row 1 only pulls the sub upward when a diver is aboard. Then I'm raising the no-diver penalty on the row-2 up move to about -45, so up only wins as an escape when the lower cell is unsafe.

I'm now checking whether the Up_2 unit can carry a smaller weight into the up logit, so that when both up and down are available the down move wins clearly.

Now I'm checking the spawn timing for divers and how many steps it takes them to cross the screen, so I can judge how often a diver can realistically be collected.

I'm working out how often a diver can realistically be collected: divers on the right side hang around column 9 for a few steps before moving to column 8, so with a roughly eleven-step window I can reach almost any row in time. That should mean nearly every diver is catchable, barring enemies getting in the way.

I'm noting that once the sub has collected six divers, the bonus kicks in and the policy can surface. But each surfacing also makes the game harder, so I'm wondering whether oxygen running below 40 will force a surface before the sixth diver arrives and cost me one.

I'm settling on the oxygen threshold for surfacing: waiting until it drops below 20 risks running out, so I'll use the gauge check at (9,1), which triggers below 40 and leaves enough room to climb.

Going through the timing again, a diver on the right side sits near column 9 for several steps before drifting to column 8, so I have roughly eleven steps to reach its row, which is usually enough. Enemies are the real limit, since they'll get denser as the game speeds up and I'll probably die before the score gets very high.

I'm checking how the current row's enemies affect the stay decision: a threat approaching from far left still keeps the sub staying and firing, and an enemy receding on the same row gets chased by firing as well. I'm also wondering whether equal attraction between rows could cause the sub to oscillate, though that seems manageable. Finally, I'm making sure the vertical move check blocks entry into any row where enemies are close enough to hit the sub.

I'm settling the layer-1 unit indices for the sub's row, the rows of enemies and divers, and the escape units, with the danger check still gating vertical moves.

Writing the weight matrix for the row-state units now...

I'm setting the reward and trail weights for the row-1 to row-8 units, with danger weights that grow near the sub's column, and a bias that keeps each row unit off unless its content dominates.

Writing the unit indices for the escape layer now...

Writing the danger-escape and surfacing units now...

Still writing the weight matrix for the horizontal-move unit, row by row.

Still writing the weight matrix for the horizontal-move unit.

Still tuning the gate weights for the Seaquest policy: I'm settling the gain and the bias on the left-escape unit so it fires only when the sub is at the right edge with no trail behind it.

Writing the layer-2 weights for the up moves now, with each row's unit depending on its own sub-state and the neighboring rows' escape units...

Writing out the output-layer weights for the up moves now, with the matrix scaled into the same tanh space as the other units.

I'm converting each layer-2 unit's weights from the indicator form into the tanh-space form, so each ind term splits into a half-weight on the activation plus a constant offset. The bias for each unit is then the sum of those constants and the fixed offsets.

Working out the Up_r logit weights now, converting each row's attraction terms into the tanh space.

Still working out the layer-2 weights, now computing the attraction sums for each Up and Down unit.

Working out the layer-2 attraction sums for the Up units now, moving through each row's contributions from above and below.

Still working out the layer-2 attraction sums, now for the Down units, where each row's total comes from the rows below and above it.

Still working out the layer-2 biases, now for the Up units, where each one combines its fixed offsets with its share of the attraction sums.

Still working out the layer-2 biases for the Up units, now for Up_1 through Up_5, combining each one's fixed offsets with its share of the attraction sums.

Still working out the layer-2 biases, now for the Down units, where each one combines its fixed offsets with its share of the attraction sums.

Still working out the bias for the Down units, now checking the rest of the Down_0 pre-activation with its safe-and-positioned weights.

Checking the row-5 scenario now: with every row's attraction term at its "empty" value, the up-move unit should fire only from the baseline offsets.

Checking the current row's danger term: with the sub's row unit on, the up-move preactivation lands at 48.5, so it fires; with a second row's danger also on, it drops to -81.5 and stays off.

Still working out the per-row weights on the row-state units, with the Up_1 weights settled and the Up_2 weights next.

Still working out the layer-2 weights, now the per-row attraction weights for the Up_4 unit.

Still computing the layer-2 weights, now checking the per-row attraction values for the Up_6 and Up_7 units.

Still working out the weight matrix for the Down units now, with the first Down_1 row weights settled.

Still working out the layer-2 weights for the Down units, now checking the per-row attraction values for Down_2 through Down_4.

Still working out the layer-2 weights for the Down units, now checking the per-row attraction sums for Down_5 through Down_7.

Still writing the layer-2 weights, now for the Up and Down units, with the same per-unit setup as before.

Now I'm setting the weights for the Down_0 unit and the two horizontal-move units, then adding a blocking unit that stops the sub from going further when it is on the first row with no diver.

Still working out the output-layer weights, now setting up the logit for the up action so it lands between 0 and 20 across the row states.

Writing the output-layer weights for the up action, and the blocking unit that keeps the sub from moving up off the first row when no diver is present.

Writing the right-move logit weights and the left-move bias now...

Still working out the output-layer weights for the right move, and the fire bias, with the noop logit left at zero.

Checking that a diver approaching from row 3 pulls the sub up from row 5: the up unit gets a strong positive preactivation while the down unit stays firmly off, so the sub moves up. As it climbs to row 4 the up unit still fires, and at row 3 the current-row danger keeps both vertical units off.

Checking a tie case: a diver in row 7 and an enemy in row 3 with the sub at row 5 leaves both vertical preactivations at -1.5, so the sub would just sit there firing. I'm considering a small asymmetry between the up and down weights to break that tie, though I haven't settled on the exact offset yet.

I'm tuning the vertical units so a tie doesn't leave the sub stuck: I'd scale the below-row attraction up slightly and drop the threshold to about -0.5, which makes the down move win clearly in the row-5 case. Looking at it again, I don't have a real reason to prefer down over up, since nothing about depth favors one direction, so I'd need a different tiebreak basis.

I'm settling on a threshold of -1.0 instead of -0.5, since at -0.5 the vertical units would drift a few percent of the time into unchecked moves, while at -1.0 the chance of a stray move drops to about 0.05%. I'll keep the small asymmetry favoring down, which breaks the row-5 tie without needing a deeper reason than convenience.

I'm working through the asymmetry for the tie case: with the below-row weights scaled up by 1.25, the down move wins at distance-2 vs distance-2 but the up move still stays quiet. Pushing the asymmetry to 1.5 would make the down pull too strong and break the balance against nearby threats above. So I'm thinking the distance function needs to be steeper, with a closer-row value of 8, so near threats dominate.

I'm settling the tie-break for the vertical units: I'll keep the distance values as they are and lower the threshold from -1.5 to -1.0, accepting that a few symmetric stalemates may remain since the world keeps changing.

I'm switching to an asymmetric weight table: the below-row attraction terms get multiplied by 1.25, so each vertical unit's pull depends on which way the threat is. Then I'll recompute the per-row values for the Up and Down units.

Now I'm setting the up-move weights per row, scaling the below-row terms by 1.25 so a tie breaks toward down, starting with the Up_1 row values.

Still working out the Up_3 weights, with the row values for the Up_2 unit already settled.

Still working out the Up_4 weights, now summing the row values for that unit.

Still working out the Up_5 through Up_7 sums, which are coming out negative for Up_5 and Up_6 but drift toward zero.

Still working out the Down weights, now filling in the Down_1 row values and starting the Down_2 row.

Still working out the Down_3 through Down_5 weights, now summing their row values.

Still working out the Down_5 through Down_7 sums, which are negative for all three units.

I'm checking the bias terms now: each one is the sum of its half-weights, and the threshold drops to -1.0. Next I'm estimating the maximum attraction and confirming the unsafe penalty still wins over the strongest positive pull.

Still tuning the weights: the threshold and the surface penalty are on the table, so I'm raising the surface term and checking whether an attractive lower row can still outweigh it.

Working out the base biases for the up units now: with the gate at 200 and the unsafe penalty raised to 150, the row-3-and-up units come to -126 each, and the Up_2 unit gets an extra adjustment from its horizontal-danger term.

Now I'm finishing the bias terms for the down units, where the base for each row is set by the gate, the neighbor penalties and the surface term. For the edge unit I'm adding the horizontal danger terms as well, which brings its bias to a much more negative value. I'm also settling the weights: the gate gets a large positive weight, the same-row term gets a moderate positive weight, the neighbor penalty is negative, and the surface term flips sign between up and down.

Still computing the bias values for the down units, working through the remaining rows.

Still working out the Down bias terms, and I'm verifying the Up_5 preactivation by checking the gate, the below-row attraction, and the surface penalty.

Checking the up-unit biases against a few hand-computed cases: the up_1 case with a diver and surfacing both on comes out to -1, the no-diver case is -201, and the up_2 no-diver relative weight works out to -45. Next I'm verifying the down_0 unit.

I'm checking the down unit's arithmetic: with no threats and a safe, positioned sub, the preactivation comes out to 3, and the same case for row 3 gives roughly -1. I'm also noting that the hazard-unit weight for Up_2 depends on the diver feature, and that the layer-1 diver suppression still needs its bias worked out.

I'm raising the diver-suppression weight to 40 with a bias of -44.5, so a diver at column 9 still pushes the unit negative. I'm also noting that the sub's own cell doesn't need separate handling, since a hit there already means the episode is over.

Next I'm checking the enemy bullets: subs in rows moving right fire bullets toward column 8, so a bullet at column 5 would reach column 6 after my move and force an escape, which needs a safe neighboring cell. I'm also wondering whether my bullets can kill an enemy sub at column 2 before its first shot.

I'm checking how enemy bullets travel toward the sub's column, and whether my own shots can clear a row before the first enemy fires. Our shot cooldown means the next fire comes on the fifth step after the last one.

I'm checking the trail channel at column 9 for the left-facing unit, noting that a diver there leaves no trail when moving left, and that the trail counts only when the sub is away from home. Next I'm confirming the right-facing and left-facing units behave as expected when the sub sits at column 9 facing right, and then I'll start writing the row-by-row weights for the R units.

Still writing the per-row channel weights, now the reward, trail, and danger values for the R units.

Checking the rectified-reward values for the R units: an approaching enemy three columns out still comes out clearly positive, and a receding one only mildly so.

Checking the reward-channel values for the enemy-bullet case and the approaching enemy at column 6, both of which come out slightly negative and so mark that row as unsafe. Next I'm working through the diver cases, including a diver spawned at column 9 and one receding at column 7.

Still checking the trail weights for the right-facing units, now looking at how a diver moving right near column 8 gets treated against one that has already passed.

Now I'm checking the rows where enemy bullets could arrive: a bullet sitting at column 5 moving right would reach column 6 after my move, so the escape logic has to cover that.

Still writing the weight assignments for the S units, and the U units are next.

Still assigning weights for the upper-row units: channel 1 gets a weight of 10 at the diver-related column positions, with a bias of -5. Next I'm setting the hazard-diver unit and the surface unit, which get their own specific weights and biases.

Still writing the weights for the hazard-related units, the horizontal-right and horizontal-left ones next.

Still working through the weights for the hazard units: the horizontal-left unit's negative weights on the leftward trail and home cells, then the layer-2 combinations that feed the block unit.

Writing the layer-2 weights for the Up units now, covering the S, U, and surface connections.

Still writing the layer-2 weights for the Down units, adding the surface and hazard connections and their biases.

Still writing the output-layer weights: the down logits get a bias of 80 with weight 10 on the down units, and I'm checking that the inactive units stay low enough that their contribution is negligible.

Checking that the surfacing logic holds: with the surface flag on and the sub's upward neighbor safe, the Up unit should win, bringing it to row 0 where oxygen refills and the flag clears, so the next step dives again.

Now I'm tracing the opening moves: the sub starts at row 0 facing left, so the right-moving unit wins and it steps right four times. At the far right edge the left-moving unit takes over, and once the sub is at column 8 it dives to row 1 if that cell is safe. On row 1 with no diver in sight, the blocking unit pushes the up logit well negative, so the sub stays put and keeps firing.

I'm now checking the case where the sub sits at row 1 with no divers around: it isn't in danger there, but if a threat appears in that row with the row above also unsafe, it would have no escape. I'm also confirming that the diver-pickup and danger cells at column 9 behave as intended.

Now I'm double-checking the diver-related logic. With six divers collected, surfacing still dominates, so the upward move wins, and the R units keep pulling toward divers in the meantime. I'm also verifying the gauge encoding at row 9, where the diver-count cells should line up correctly.

I'm realizing the oxygen and diver bars share channel 5 at the bottom row, so they overlap in columns 3 through 9 and I can't read them apart from that channel alone. I need to separate the two bars, since a cell lit there could mean either oxygen or divers.

I'm realizing the oxygen and diver bars both sit on channel 5 along the bottom row, so their cells merge and I can't always tell them apart. The oxygen bar fills from the left and the diver bar grows from the right, so once the oxygen bar is long enough it hides the diver bar entirely.

Working out how to tell the oxygen bar from the diver bar on channel 5: when oxygen is below 180, column 8 lit means divers are present, but once oxygen reaches 180 or more the bars merge and the diver count is hidden. I'm considering counting the lit gauge cells and looking for a gap, since if the two bars don't overlap, the gap shows where the diver bar starts.

I'm checking whether the gauge can tell me if divers are present once oxygen is high: when oxygen is at 180 or above, the oxygen bar covers the columns the diver bar would use, so the diver count is hidden. Below 180, a lit cell at column 8 would point to divers, but I still can't rule out that the oxygen bar alone reaches that column.

I'm checking whether the diver gauge can be told apart from oxygen at all: once oxygen is 180 or above, its bar covers the columns the diver bar would use, so a lit cell at column 8 proves nothing. That means the diver signal is ambiguous right after surfacing, and I shouldn't let a lit cell there push the sub upward.

I'm realizing the gauge is ambiguous: oxygen and diver bars share row 9 and can overlap, so a lit cell at column 8 doesn't reliably mean divers are present. I'm checking whether counting the total lit cells in that row could separate the two bars.

I'm checking which cases the gauge can still settle: when oxygen is at 180 or above, the oxygen bar fills columns 0 through 8, so a lit cell there tells me nothing about divers. Below that, a lit cell at column 8 would point to divers. The open question is how to write the safe-surfacing condition so it never reads a diver count from an overlapped bar.

I'm checking whether the diver count can be read from the gauge when oxygen is still moderately high. Since the oxygen and diver bars share row 9, a lit count of 9 is ambiguous, so the surfacing rule should stay conservative. In the common case of few divers and low oxygen, the total stays at 8 or below and the diver signal is clear. The harder question is telling six divers apart from high oxygen when the bars overlap across columns 3 through 8.

I'm checking whether the gauge can settle the diver question: if column 8 is lit and at least one of columns 0 through 7 is dark, the oxygen bar can't be covering that column, so the lit cell has to come from divers. If every cell from 0 to 7 is lit, the oxygen bar could account for it, so I'd treat the diver signal as unknown and stay conservative about surfacing.

I'm working out a linear rule for the gauge: the diver bar should count only when column 8 is lit and at least one of columns 0 through 7 is dark. The weights need to act as an AND, so a lit column 8 alone isn't enough.

I'm working out a linear gate for the surfacing rule: I want the gauge cell at column 8 to count only when at least one of columns 0 through 7 is dark. Taking the constants that satisfy those cases, the weights come out to 60 on column 8, -6 on each of columns 0 through 7, and a bias of -15. Writing the pre-activation...

I'm settling on a conservative surfacing test: column 8 counts as a diver only when at least one of columns 0 through 7 is dark, because that gap proves the oxygen bar can't be the source. The weights that encode this AND come out to 60 on column 8, -6 on each of columns 0 through 7, and a bias of -15. The trade-off is that with many divers the oxygen bar fills the gap, so I won't detect them until oxygen drops.

Now I'm settling on the surfacing trigger: either there are divers and oxygen is nearly out, or six divers are on board. Oxygen below 40 means only about one gauge cell is lit, so the diver bar stays readable and the gap check still works.

Now I'm checking the low-oxygen surfacing case: when oxygen is under 40, only the first cell of the gauge is lit, so column 8 can only come from divers, and that gives a clean trigger. The case of six divers is harder, since the diver bar and the oxygen bar overlap whenever oxygen is 60 or more, and I can only confirm six divers once oxygen drops low enough to leave column 3 unambiguous.

I'm trying to see whether the gauge can reveal divers when oxygen is high, but the bars overlap too much to tell. The surfacing trigger still works at low oxygen, though only a single point is at stake then. Detecting six divers early isn't possible without memory, so I'll accept collecting that bonus only once oxygen drops.

I'm settling on a surfacing trigger that uses the gauge's gap structure: the diver bar sits in columns 3 through 8, so a lit column 8 with column 1 dark marks a low-oxygen diver case. Detecting six divers early isn't possible while oxygen is still high, so that bonus can only be checked once oxygen drops low enough.

Tuning the surfacing gate: pairing column 8 with the dark-gap test on columns 0 through 7 gives a sound diver signal at low oxygen. A second term on columns 2 and 3 is meant to catch six divers when oxygen is already low, though it is a minor bonus.

Now I'm writing the weights for the surfacing gate and checking the low-oxygen and six-diver cases again. I'm also deciding that the diver detector should be applied at the surfacing-decision level rather than inside the row-1 suppression.

I'm checking whether the row-1 suppression is even needed, since the upward move from row 2 is already blocked by the diver-detection penalty. Rows 1 targets could be ignored outright, or suppressed only by the column-8 gauge cell, which would misfire while oxygen is high.

I'm keeping the row-1 suppression simple by gating it on the column-8 gauge cell alone, since the upward move from row 2 is already penalized. I'm also setting up the HD unit at index 25 of the first layer.

Working out the scaled weights for the diver-detection unit: doubling everything gives 120 on column 8, -12 on each of columns 0 through 7, and a bias of -30, which keeps the boundary cases on the right side of zero.

I'm checking the scaled diver unit's edge cases, confirming that a full oxygen gauge or a sparse diver count can't falsely trigger it. The row-1 suppression for the upward attraction is next, and I'm keeping it gated on the column-8 cell alone.

Now I'm checking whether the surfacing trigger still holds once divers pile up, since the oxygen gauge and the diver bar overlap and can hide the count. Low oxygen should keep working, and the six-diver bonus only shows up once oxygen drops, so I'm reviewing that trade-off before settling the row-1 suppression.

Now I'm estimating how difficulty ramps: the spawn interval shrinks by one step at each surfacing, while the enemy movement speed drops every other surfacing, so episodes should stretch to a few thousand steps.

Next I'm checking how the enemies move: at move speed m they step every m+1 frames, so at m=2 they step every third frame, and the cells I use for the upward check still hold.

Now I'm checking the enemy-row weights, scaling the per-row values and confirming the indices for the Up and Down units in layer two.

Still writing the weight assignments for the enemy-row units...

Still writing the input-weight assignments for the rest of the units, working through the up, surface, and horizontal indices.

Still writing the weight assignments for the horizontal and vertical unit ranges, checking the strides for the hazard and target channels on each row.

Still writing the layer-two weight lists for the up units...

Still writing the layer-two weight lists for the down units...

Still writing the layer-two weight lists for the down units...

Still writing the layer-two bias values...

Still working out the bias values for the upward units...

Still working out the bias values for the downward units...

Still working out the bias values for the downward units...

Checking the bias arithmetic for the downward units now, and the base sum for the upward units from row 3 onward comes out to -126, as expected.

Still checking the Up_1 bias sums, now working through the case where the surfacing and danger terms are both active.

Still checking the gate math and the danger-escape cases for the upward units.

Still checking the fire and movement logits against the up and down units.

I'm checking the random-action rate now: with fire at logit 10 against movement logits near zero, a stray up, down, or left/right happens roughly once every few thousand steps, which should be tolerable over an episode. I'm also weighing whether bumping the fire logit to 12 is worth it, since it would make the move-failure rate a bit lower without changing much else.

Checking the bias arithmetic on the block unit now: in the first row the upward logit comes out to zero, as it should, and I'm working through the same check for row one with the danger unit active.

Still checking the bias arithmetic for the logit units, and the block unit comes out the same way in every row.

Still checking the edge cases: the friendly bullet isn't used, and the danger cell at column 8 in the sub's own row would mean the sub is already dead.

Still writing the layer-one weight assignments for the sub-position units, setting the strided entries for each of the first few blocks.

Still writing the layer-one weight entries for the sub-position and row units...

Still writing the layer-one weight entries for the diver-detection unit...

Still writing the surfacing-unit weights and checking their edge cases.

Still writing the layer-one weights for the hazard-row units...

Still writing the layer-one weights for the horizontal-right and horizontal-left units...

Still writing the layer-two weights for the up units...

Still writing the layer-two weights for the up units...

Still writing the layer-two weights for the upward units...

Still writing the layer-two weights for the down units...

Still writing the layer-two output weights...

Still checking the surfacing and downward-unit weights in layer two, and the bias terms for the block unit.

Now I'm double-checking the sticky-action risk: after a dive from row 0, the down move could carry the sub into row 2 without rechecking that row, which is a small gap I'm weighing.

