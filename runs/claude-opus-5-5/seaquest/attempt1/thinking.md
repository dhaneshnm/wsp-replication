I'm working out a hand-written policy for Seaquest without tools, aiming for something practical. I'm weighing a simple strategy: hold a row, face a direction, and fire continuously, which should catch enemies crossing that row, though I'm unsure how well it covers enemies in other rows.

I'm reasoning about how enemies in other rows can't hurt me, and that oxygen runs out after about 200 steps unless I surface with divers. Shooting from a single row would only yield a few kills, so I'm leaning toward moving vertically to line up with enemies. Enemies approaching from behind are the real danger, so turning around matters.

I'm weighing how a sub's bullets would come at me if it moves toward my row, which makes that a real hazard. Hand-building a full policy with only 32 hidden units looks hard, so I'm looking for a design simple enough to fit. I'm settling on a plan that starts with shooting any enemy in my row in front of me, which needs a feature detecting an enemy in the same row as the player.

I'm settling on the idea of moving vertically to line up with enemies, facing them and firing, and turning around when something comes from behind. I'm still working out how to encode the player's row and whether to track direction with the few hidden units I have.

I'm sketching the rest of the policy: keep an eye on oxygen and collect divers, since they're safe to grab and bullets pass through them. My plan is to move vertically toward whichever object is nearest, enemy or diver, surfacing when oxygen runs low, and once aligned, face the target and fire.

I'm working out how to encode the player's row so the policy can tell whether targets are above or below. Per-row indicator units seem like the cleanest starting point.

I'm looking at a conditional unit that should fire only when the player is above some threshold row and a target sits at or below it, so I can tell whether targets are below me.

I'm making the player-above conjunction robust by weighting the player term more heavily than the target count, so a few targets alone can't trigger it. Then the sum over thresholds of these units should roughly measure how far below the player the targets sit.

I'm weighing whether a simpler strategy could still score reasonably, since the hand-built vertical targeting is costly with 16 units. Each enemy is worth a point and surfacing with divers adds a bonus, so even a modest kill rate per oxygen cycle might get a decent average.

I'm noticing that the row-0 idea is a loophole: oxygen only drains below the surface, and enemies and divers never appear in row 0, so sitting there is completely safe. That would keep me alive indefinitely but earn no points, so the real question is how to mix a short dip into the lower rows with a return to the top.

I'm noting that moving to row 1 and staying there earns little, since it's only a few enemies. Once I drop below the surface, I can't return to row 0 without a diver, so I have to commit to the oxygen cycle. The plan is to hunt enemies and divers below, then surface once oxygen runs low, which should give a more realistic score than hovering.

I'm sketching the vertical targeting features as threshold units: one set that fires when the player is above a boundary row and targets sit below it, and another for the reverse, about 15 units in total.

I'm weighing whether enemy subs belong in the target set too, since shooting them scores but their bullets come straight at me. The danger channel minus the reward channel should isolate bullets, which would let me detect incoming fire in my row.

I'm separating enemy bullets from divers by subtracting the reward channel from the danger channel, though divers would still register as negative there. Then I'm trying to get a same-row check between the player and enemies, and I'm thinking about whether horizontal aim could be handled by keeping the sub near the center and turning toward targets in its row.

I'm weighing whether to keep the player at a fixed edge column, say column 9 facing left, so one fire direction covers the whole row. Enemies spawn from both edges, so a spawn at the player's own column would still need handling.

I'm weighing the risk of enemies spawning right at my column, since a spawn in my own row would end the episode immediately. I'm leaning toward standing at column 8 facing left, though enemies coming from behind would then force me to dodge vertically.

I'm sketching a fixed-column setup where the sub sits at the edge and always fires in one direction, so the whole row is covered, but enemies spawning at its own column would be a problem. I'm also considering letting the policy approximate facing and turning with a few layer-2 conjunctions, since the player's column and row can be coarse features and tanh units should handle the ranges.

I'm looking at keeping the player near the center column so that "left" and "right" targets map to simple column ranges. The catch is that turning to face a target moves me a column, and re-centering would undo that, so I'm weighing a center band with no pressure to move, to avoid oscillating between two columns.

I'm weighing a fixed-column setup where the center band removes any pull toward recentering, so turning to face a target doesn't cause oscillation. Shots only fire once every five steps, so spamming fire mostly does nothing, which is acceptable. I'm now looking at whether row-relative targeting can avoid a costly threshold scheme, perhaps by summing player row weights, though comparing targets against that value isn't linear.

I'm considering whether to keep the player on a fixed row and only shoot what crosses it, but that would cover just a fraction of enemies. A patrol approach using vertical thresholds plus per-row side conjunctions would be too many units, so I'm trying to merge the left and right same-row checks into one signed unit gated by the player's row.

I'm checking whether the two-unit-per-row pairing for left and right same-row detection can be collapsed, since each row's gate currently costs two units and the total is already near 16. I'm thinking about whether I can keep the player at a fixed column band and only track which side enemies sit on within the player's row, which might remove the need for per-row side conjunctions.

I'm checking whether a single unit could detect a player and enemy sharing a row by summing per-row weights, since that would need a row-coded scheme where enemies and the player each carry a weight that only lines up when they match.

I'm checking whether one unit can flag a bullet or a same-row match by mixing row-coded weights, and it looks impossible for three or more rows since the sums can't separate every pair. Using two opposing units per row might work instead, though that's the expensive route again.

I'm laying out a layer-2 scheme where a "down" unit fires when the player's row is above a row that has a target, built from the one-hot player-row features and per-row target features.

I'm checking whether same-row detection can be done in layer 2 by first building a per-row conjunction, since summing across rows doesn't work because a player in one row and an enemy in another would also add up to the threshold.

I'm checking whether the same-row left and right units can be computed directly in layer 1 with a gate built from the player's row, since that would save the separate conjunction layer. The problem is that each per-row gate still costs units, so the budget stays tight.

I'm trying to fold the oxygen check into the same layer-1 budget, with 31 units already spoken for by the row-side and vertical units. That leaves one spare unit, which could be a low-oxygen gate that pushes upward when divers are present.

I'm noting that the oxygen and diver gauges share row 9 of the same channel, so their cells overlap and can't be told apart by position alone. Column 9 can only be oxygen, and column 0 can only be oxygen too, since the diver bar never reaches that far left.

I'm checking which gauge cells can only come from oxygen: the low columns 0 through 2 can't be diver-driven, while column 8 lights up for divers whenever oxygen is below 180. That lets me combine an unlit column 2 with a lit column 8 into a single surfacing signal that pushes upward.

I'm checking whether a single unit can keep the policy from surfacing at row 1 when there are no divers, since sampling noise could push "up" there and end the episode. I'm considering a strong negative bias on the up logit, or a dedicated unit for row 1 without divers, but the layer-1 budget is already nearly used up.

I'm checking the sticky-action risk: if the previous move was up and the policy lands on row 1, a 10% repeat of that up move would take me to row 0 with no divers, which is fatal.

I'm weighing whether to exclude row 1 as a target so that moving up never lands me there by choice, since a sticky repeat of "up" from row 1 would drop me to row 0 and end the episode. Ruling out row 2 as well would cut the leftover risk, though it would cost coverage.

I'm now checking the down-moves: from row 0 or 1, I can move down toward any target at or below, and row 1 targets are fine for downward moves. Since the sticky repeat of a down move is harmless, that's consistent with the plan. The horizontal side is still open, since "left" needs to be measured from the player's column rather than a fixed midpoint, and I haven't settled how to do that.

I'm considering using the enemy's direction of travel instead of its position: one moving right has come from the left edge, so if it sits to my left it's coming toward me, while one moving left and sitting to my right is coming at me too. Enemies moving away are harmless, though still worth shooting for points since bullets outpace them.

I'm weighing a fixed-column band for the player so that left and right can be defined relative to a stable position, and I'm checking whether the sub's orientation could also show its facing from the trail channels.

I'm thinking about horizontal centering: if the sub sits at column 3 or less, I want a rightward push, and at column 6 or more, a leftward one. Those can be single linear units over the player cells, with no conjunction needed. The sub's front cell is the tricky part, since channel 0 covers both front and back, so I'm considering using channel 0 minus channel 4 to isolate the front.

I'm testing whether the front cell can be picked out from the channel-0 and channel-4 difference, but enemy trails would pollute column sums. So I'm falling back on counting channel-0 cells in columns 0 through 3, where a count of at least 1.5 means the sub sits too far left.

I'm checking the band logic again: with the sub's two cells kept inside columns 3 through 6, turning in the middle just swaps which cell is the front, so the pair {4,5} stays put.

I'm checking whether the back cell matters at all, since collisions in this game seem to hinge on the front cell only. If that holds, then a diver crossing my row toward the center would reach my front and get picked up, while one moving away never would.

I'm noting that an enemy moving right would hit my back cell harmlessly and then only be dangerous once it reaches my front, so the orientation matters for timing. Divers moving toward the center will reach my front cell and get picked up no matter which way I'm facing, so I'm defining the left and right zones as columns 0 to 3 and 6 to 9, with columns 4 and 5 left ambiguous.

I'm settling on a facing rule: if the enemy is in my row on the left and I'm facing right, I turn left first, and if I'm already facing left I fire. I'm now working out how to detect my orientation from the channel cells, with the front cell being channel 0 without channel 4 and the back cell being both.

I'm still weighing how to tell which way the sub is facing from the channel cells. Channel 0 alone can't separate the front from the back, and channel 4 picks up enemy trails too, so a plain linear sum over columns gets polluted. I'm considering whether a per-cell conjunction would work, though that would take more units than I have.

I'm still stuck on orientation: a per-cell conjunction would tell front from back, but the trail channel pollutes any column sum, and I don't have the units to spare for it.

I'm stuck on the same orientation problem: a single linear feature over ch0 and ch4 would pick up enemy trails from other rows, and per-cell AND needs more units than I have. I'm trying to find a weighting that cancels the trail contribution or to accept that orientation can't be read cleanly.

I'm now considering whether the left-wall boundary at column 0 could make orientation irrelevant, since pressing left there just holds the sub in place.

I'm settling on the left wall as a special case: at column 0, pressing left only turns me without moving, so facing right there is the useful stance for shooting across the row. I'm now checking the spawn edge case, where an enemy appearing on my cell at the wall would be fatal unless I've already moved vertically.

I'm checking the spawn edge case at the left wall: an enemy appearing at x=0 in my row could hit me unless I've already moved vertically, and that risk adds up to something like half the episode. So I'm thinking about standing at x=1 instead, where a spawn at x=0 would take several steps to reach me.

Checking the spawn case at the left wall: an enemy appearing at x=0 in my row could reach x=1 in a few steps, so I'd have to dodge vertically rather than turn toward it. I'm also noticing that facing right at x=0 leaves me with an ambiguous orientation, and I'm not sure yet how to read it from the state.

I'm checking the edge positions in the wall case: from x=9 the sub can only have reached that cell by moving right, so it's always facing right there, and from x=0 it can only have arrived by moving left, so it's always facing left. That means the wall positions have a fixed orientation I can rely on.

I'm weighing whether the trail pollution in channel 4 can be cancelled by using the reward channel, since each trail cell sits next to the object that left it, so the trail weights could be offset to isolate the sub's orientation.

I'm checking whether the trail pollution can be cancelled by subtracting the reward channel from the trail channel, since each object's trail sits one column off from it. That would leave only a ±1 offset per object, which I could fold into the orientation estimate.

I'm checking whether constant weights could help, but a plain sum over channel 4 minus channel 2 only gives about 1 for the back cell, which doesn't tell me orientation. I'm now wondering whether restricting the weights to the band columns and matching the compensation in neighboring columns could cancel the trail pollution.

I'm now sketching per-row units that would decide directly whether to turn left or right, since the orientation signal from the trail channel is too polluted to use cleanly. Each row's unit would need to combine whether an enemy sits on that side with my facing, rather than relying on a single global orientation estimate.

I'm now looking at whether the player's orientation could come from the row's own cells: enemies in my row leave trails in that same row, so the signal is tangled up with what I'm trying to read. One idea is to pin the player to columns 4 and 5, where facing left would show as front at column 4 without a trail there, though I still need a clean way to read the trail at column 5.

I'm checking whether the difference between column 5 and column 4 in channel 4, summed over rows, can reveal the sub's facing. The sub adds plus one when facing left and minus one when facing right, but objects moving through the middle leave trails that add their own offsets, so I'm tallying those contributions column by column.

I'm checking whether the trail pollution from objects in the center columns can be separated out, since it biases any orientation sum. Since the orientation only matters when an enemy sits in my row, I'm considering per-row units that gate on the player's row and read facing from that row's own cells.

I'm sketching per-row units so that firing is the default action, since shooting costs nothing and is simply a no-op during cooldown. Each row would get two turning units, one for an enemy on the left and one for the right, which gives 16 units for the rows, plus 14 more for vertical movement.

I'm counting the per-row units and find 33 total, one over budget. I'm considering merging the bottom-row down unit with the next one, or dropping a top-row turn unit, so the design fits.

I'm weighing how to keep the sub alive while it fires at me, and I'm treating shooting as the default action since it costs nothing during cooldown. The concern is that bullets already in flight keep moving after a sub dies, so I need to watch for a sub entering my row at the edge, where its first shot would arrive quickly.

I'm stuck on the danger side now: moving into a row where an enemy bullet is already flying, or an enemy is right next to me horizontally, could kill me. I'd need some kind of unit that moves me vertically when that threat is adjacent, but I'm short on budget and wondering whether layer 2's unused units could take that role.

I'm wondering whether a single layer-1 unit could cover several rows at once, since each conjunction of "player in row r" with "enemy left in row r" normally costs its own unit. I'm sketching weights where the player's cells in each row and the enemy-left cells in each row feed one shared threshold for "turn left."

I'm trying to see whether a single layer-1 unit could cover several rows at once, but a plain weighted sum can't express "player and enemy in the same row" across rows. I'm considering a threshold decomposition instead, where a family of units tracks whether the player's row is at or above each threshold.

I'm narrowing the design to targets in rows 2 through 8 so the per-row units fit the budget, with the down units handling the climb out of the bottom rows.

I'm checking the vertical budget: targets in rows 2 through 8 need seven down units and six up units, which leaves room for two danger-avoidance units. I'm also considering whether the player can simply wait at row 0 at the start, since oxygen doesn't drop there and no enemies appear until around step 30.

I'm now deciding which objects count as vertical targets: enemies and divers both, since the reward channel covers them. Horizontal facing will only key off enemies in the danger channel, and I'll accept that I won't deliberately steer toward divers in my row.

I'm weighing whether the up and down units could fight each other when targets sit both above and below me, since the larger count would win and I might oscillate. I also need to make sure that when an enemy is already in my row I suppress vertical movement and turn or fire instead, which means the turn units have to take priority over the vertical ones.

I'm wondering whether the per-row units should also carry the facing signal, so one unit can say both "enemy in my row" and "which way to turn." I could make each row unit output a graded value: below zero when I'm not in that row, near zero when I'm in it and already facing the enemy, and high when I'm in it but facing the wrong way.

I'm working out how each row's unit should encode both presence and facing: the signal would come from the player's cells in that row plus the back cell's position relative to the front, with the trail in the band columns telling me which way the sub points.

I'm working out the orientation for each row by taking the difference between the front and back cell columns, which gives +1 when facing right and -1 when facing left. The trail cells in that row add a large negative pollution term, so I'm checking whether it swamps the signal.

I'm checking whether the player's orientation can be read off the front and back cells in each row, with trail pollution from enemies in the band columns kept small. Enemies in the left zone mostly leave their trails outside the band, except when one sits right at the boundary, and by then it's close enough to matter anyway. The open question is how the player-row gating interacts with that orientation term.

I'm settling on a per-row unit whose pre-activation adds a constant weight on the player's cells, so presence doesn't get lost, and then adds a signed term for front minus back to capture facing.

Now I'm settling the orientation weights for each band cell: the front cell gets a weight tied to its column, and the back cell gets a negative weight of twice its column, so front minus back comes out to +1 or -1. A constant offset on the back cell would shift both values without changing their sign.

I'm weighing a shared weight per row where the trail cells contribute a term proportional to their column, so an enemy's trail registers as a negative pull on that row's unit. I'm considering whether to offset that by adding a matching positive weight on the reward channel for objects at the same column, so the net effect of an enemy in my row doesn't wash out the presence signal.

I'm trying to make the trail pollution in each row roughly cancel out, so I'm testing whether position-dependent weights confined to the band columns can work, since the scale ratio of orientation to pollution is fixed for linear weights.

I'm checking the orientation weights at the edges of the band, where a back cell at column 6 with the front at 7 gives the wrong sign, so I'll look at the mirrored case next.

I'm checking the edge cases at the far columns, where the back cell falls outside the band and the sign flips. Extending the same weights across every column makes the orientation come out as front minus back everywhere, so I'm now looking at how trail pollution in the row interacts with that.

I'm noticing that a trail-based pollution term in my row weights can be large and direction-dependent, which breaks the ±1 orientation signal I'm trying to read off. Centering the weights on the player's column doesn't fix it, since far-away trails still produce big values. Maybe I can cancel the pollution exactly by using which way each enemy is moving, instead of relying on fixed weights.

I'm checking whether a single layer-1 feature could give me orientation without the trail pollution, since the linear weights tie the signal scale to the pollution scale. I'm considering computing the facing in a second layer from features the first layer already isolates, rather than from raw channels.

I'm thinking about whether the front column alone can tell me my orientation. If I stay at the pair {4,5}, the front is 5 when facing right and 4 when facing left, so the position would encode the facing. The catch is that finding the front cell still needs an AND between the player channel and the column, which a single linear unit can't give me.

I'm considering whether to keep the player pinned to columns 4 and 5, so that the difference between the trail cells at those two columns tells me which way the sub is facing. That would avoid the trail pollution problem, since only two columns are involved.

I'm checking whether pollution stays harmless if I keep the player pinned to columns 4 and 5, since trails from enemies near those cells would mean an imminent collision anyway. I'm also weighing whether turning can keep the sub within that pair so the orientation signal stays clean.

I'm settling on a centering rule: if the sub's cells sit at columns 5 and 6, I press left to shift the pair to {4,5}, and if they sit at 3 and 4, I press right. Once the pair is at {4,5}, turning in place keeps it there, so the orientation trail cells stay at just those two columns.

Now I'm testing a centering rule that nudges the sub toward columns 4 and 5 whenever it drifts to the edges, and I'm checking whether a global orientation feature built from the column 4 and 5 trail cells stays clean enough given how far pollution from objects near the center can reach.

I'm writing the per-row left-zone unit now, with a positive weight on the player's two cells, a sum over enemies in columns 0 to 3, and an orientation term that flips sign depending on whether the back cell is at 4 or 5.

I'm now setting the level targets for the left-zone unit: no output near -1 when the player isn't in the row, about +1 when an enemy sits in the zone and the sub faces the wrong way, about 0 when it faces the right way, and -1 when the zone is clear. I'm sketching a pre-activation that combines the player-presence count, the danger count in columns 0 to 3, and the signed orientation term to hit those levels.

I'm settling on a three-level target for the left-zone unit: a pre-activation near +4 when the player is in the row, an enemy sits in the zone, and the sub faces the wrong way; near 0 when it faces the right way; and near -4 when the zone is clear. I'm checking the arithmetic for the current weights, which gives +1.5 and -1.5, and those land close to but not at the middle level I want.

I'm checking the arithmetic for the n=1 case, which pins down c=2 and leaves 2a+b+d=2. Then the n=0 case with the player fully in the row forces b to be at least 7, but that choice runs into trouble with two enemies facing the correct way, where the unit would wrongly read as facing wrong.

I'm weighing whether a per-row unit can handle two dangers in the left zone, since a summed count would misread a correctly facing sub as facing wrong. One option is to split presence and orientation into separate units per row, though that adds up to 21 units. I'm also considering whether a single unit could carry a shared orientation signal across all rows.

I'm trying to keep the orientation signal tied to the player's row by combining the presence, side, and facing conditions into one unit per row. The issue is that a count of enemies in the zone saturates badly, so I'm testing whether a conjunction with a threshold on the danger count can avoid misreading two enemies as a wrong facing.

I'm testing a conjunction with the orientation term weighted above the danger count, so that two enemies facing the correct way don't flip the unit. Working through the constraints, I settle on b=1, c=3, and 2a+d=-3.5, then check the zero-player case, which pushes d below -3.

I'm checking the case where only half of the player's pair sits in the row, with one enemy on the left, to see whether the sum stays below the threshold.

I'm settling on a scaled version of the left-zone unit, where the weights give a clear margin: the active case lands at 0.5s while the inactive cases sit at -0.5s or below, so the threshold separates them cleanly.

Still weighing whether to stop vertical movement when an enemy sits in my own row, since moving away could cost the shot, but the risk of dithering between target rows makes me want a rule that holds steady.

I'm weighing a shared trail-based enemy-in-row signal against per-row units, since the budget is tight and I'm still two units short of covering a row-suppression term for vertical movement. I'm also considering whether the danger count can be folded into the left and right turn units so they handle presence as well.

I'm weighing whether vertical seeking should ignore enemies in my own row, since moving away would cost the shot. I'm wondering if making the vertical pull weaker, or only pointed at nearby targets, would keep me steady without another per-row unit.

I'm weighing whether vertical seeking should pull me away from an enemy row, since shots from my current row usually land within a few steps, and dithering between target rows would waste more time than staying put.

I'm considering whether a global alternative could work: giving the vertical seeking a per-row "enemy in my row" suppression, though that would cost seven more units than I have, so I'm wondering whether firing by default and letting the vertical pull handle the rest would be enough.

I'm considering a global orientation unit O that sums the difference of ch4 at columns 4 and 5 across all rows, and I'm checking how trails from objects at columns 3 to 6 contaminate that sum. An object at column 3 moving left would leave a trail at 4 and push O up, while one at column 4 moving left would push it down, so I'd need some compensation from the object channel to cancel that pollution.

I'm checking whether the trail pollution can be cancelled by subtracting a neighbor-based term from the object channel, but averaging the trail effect only gives zero in expectation, leaving ±0.5 noise. That's not reliable enough for a global orientation signal, so I'm dropping that approach.

I'm considering dropping the orientation signal entirely and instead letting the sub's facing follow from how I press left and right: if I press toward an enemy in my row, I'd end up facing it. The problem is that the centering move would then pull me back and flip my facing, unless I suppress centering whenever an enemy is in my row.

I'm considering letting the player's pair drift freely within columns 3 to 6 and reading orientation per row using a column-weighted difference over the band from columns 2 to 7. Trail pollution from objects should only come from adjacent cells in our own row, so that reading stays clean. I'm looking at whether an orientation value per row, combined with presence, could feed the per-row units.

I'm checking whether shifting the column coordinate fixes the edge cases, since the raw weights break for the player at columns 7 and 8.

I'm checking how the trail pollution behaves under the centered weighting g(c) = c - 4.5, since trails from left-zone enemies moving right would land at low columns and push the orientation reading the wrong way.

I'm restricting the orientation weights to columns 3 through 6 so that trails outside the band can't pollute the reading. With g(c) = c - 4.5, each adjacent pair inside the band gives the expected ±1, and the pair at columns 2 and 3 breaks that pattern because one cell falls outside.

I'm checking the outside-band cases, where the orientation reading flips for pairs at columns 2 and 3, so I'll have centering take priority there. Inside the band the reading stays exact, and in-band pollution from nearby objects should be rare. Now I'm turning to how presence gets weighted per row.

I'm writing the left-zone term as a count of enemies in columns 0 to 2 and checking whether a column-3 enemy should be counted too, since it would be adjacent to the sub when the pair sits at 4 and 5.

I'm settling the zones for the left and right turn units: the left zone covers columns 0 to 3 and the right zone covers 6 to 9. An enemy sitting on my back cell still counts, since it's about to reach me. Once an enemy lands on my own cell, the next move kills me, so that case matters too.

I'm settling the zones to match: the right zone covers 6 to 9 and the left covers 0 to 3, which leaves enemies at columns 4 and 5 uncounted when the sub sits at 5 and 6. I'm accepting that gap rather than making the zones relative to the front position. Next I'm checking the orientation term O, which relies on the ch4 weights, and how an enemy at column 3 on the back cell adds a trail at column 2 outside the band. Then I'm turning to the right-zone unit and the vertical logic that should keep me in a row while enemies are present.

I'm checking whether a 3-level version of the turn units can separate "enemy on that side, facing correct" from the other cases, since the count term may be what's blurring them together.

I'm checking whether a three-level version of the turn units could separate "enemy on that side, facing correct" from the other cases. With the orientation term weighted that heavily, the presence count can't push the output into a separate band, so the levels blur together.

I'm checking whether the presence count and the orientation term can be separated into three levels, and it turns out they can't: for the enemy-facing-correct and enemy-facing-wrong cases to fall into distinct bands, the count weight has to be larger than the orientation weight, yet the count's robustness requires the opposite. The only way it works is if the count only ever takes the values 0 or 1.

I'm weighing whether to count enemies only, since a sub and its bullets would add up in the presence term. Using both channels doesn't isolate fish and subs cleanly, because divers would match too. I'm guessing multiple same-side enemies in one row will be uncommon, given how spawning is spaced out.

I'm weighing whether suppressing vertical movement while an enemy sits in my row actually matters. One case: an enemy fish in my row approaching from the left, plus a diver in a lower row. The down units would fire strongly, and the left-turn unit would too if I'm facing the wrong way, so the turn would have to win that competition.

I'm considering whether to suppress vertical movement when an enemy shares my row, since turning and diving could compete and cost me the kill. I'm weighing a separate per-row unit that fires when I'm in a row with any enemy, though the turn units can't cleanly carry that signal themselves.

I'm tallying the unit count so far: 21 for the enemy and turn units plus 13 for vertical movement, which brings it to 37, too many. To trim, I'm considering limiting the player to rows 3 through 8, which gives 18 for the presence and turn units, 11 for vertical, and 29 in total before the center and surface units.

I'm weighing whether to drop the per-row enemy unit and rely on the turn units alone, which would bring the count to 30 with two spare. I'm also checking whether the vertical units can skip enemies in my own row by construction, since each threshold only counts targets below my current row.

I'm weighing a simpler fallback: keep vertical seeking as it is, and accept that the fire constant has to be tuned against vertical logits when targets sit in other rows. Without knowing which row an enemy is in, the fire unit can't be made conditional, so the balance comes down to picking a constant default.

I'm weighing whether dithering between turning and vertical moves is acceptable, since the time needed in-row is short. I'm also considering a variant that drops rows 1 and 2 and restricts the player to rows 3 through 8, which would free enough units to include per-row enemy suppression, at the cost of ignoring a quarter of the targets.

I'm considering whether to replace the turn units with per-row enemy-presence units, which would be cleaner, but the unit count goes over budget by about five, so I'm looking at a different way to split the orientation signal across rows.

I'm considering whether the orientation could be encoded in the sub's position instead of in the pixels: keeping it at one pair when facing right and at another when facing left. The catch is that turning would then take a few extra steps to shift the pair, though it would sidestep the trail pollution from other rows.

I'm considering a different encoding: using the sub's position to signal its facing direction, so pressing left until the front reaches column 3 locks in a left-facing state. The catch is that the same columns could also mean facing right, so the mapping isn't yet unambiguous.

I'm checking whether pressing left until the sub's front sits at column 3 can serve as a dependable left-facing signal, since the column-3 count works across all rows. I'd also need to decide what to do if the front overshoots to column 2.

I'm checking the left-facing trick further: if the sub's front sits at column 3 or less, I'd treat that as facing left and fire, and otherwise keep pressing left. Whether a row has an enemy to the left is a per-row check, while the column-3 signal is shared across all rows, so combining the two should be a second-layer step.

I'm checking the wrong-direction case: if the sub is at {3,4} facing right, the column-3 feature would still be true and it would fire the wrong way. That should only happen if I switch from left mode to right mode and press right while the back is still at column 3.

I'm checking whether the front-specific version works: count only cells where the front is in columns 0 through 3, which should separate a left-facing sub at {3,4} from one facing right at the same spot. The problem is that a front at column 3 and a back at column 3 look alike unless I subtract the back channel.

I'm testing whether the left-station condition can use the pair {2,3} instead of {3,4}, so that a left-facing sub is distinguishable from one facing right, since the column-3 signal alone can't tell them apart.

I'm noticing the station check using columns 2 and 3 still reads as "facing left" even in right mode, so the first right press could lock me into the wrong state. The fix I'm considering is adding a little randomness to the fire decision, so the left move occasionally wins and the sub reorients.

I'm settling on a per-row enemy-left and enemy-right unit for each row, which gives me a count of 14 and also serves as the in-row enemy signal for vertical suppression. I'm also adding two station units for when the sub's back sits on the far left or right, plus a surface unit, bringing the total to 14.

I'm now settling the row coverage: keeping rows 2 through 8 gives exactly 32 units with no spare, so row 1 is a risk since the player could get stuck there with no awareness. I'm also thinking through how to avoid drifting up into row 1, since the up-move for targets in row 2 could push the sub there on repeated presses.

I'm weighing a feature that fires on any left-side ball in columns 0 through 3, but a sub facing right at {3,4} would also trip it and fire the wrong way. I'm considering a stricter version that requires both cells to sit in columns 0 through 3, so that a {2,3} pair is the only left-station signal.

I'm settling the station positions: the left station is the pair at columns 2 and 3 facing left, and the right station is the pair at 6 and 7 facing right. I'm going to leave out any centering move back to the right near the left edge, since that could lock the sub into the wrong facing if left mode is active at the time.

I'm settling on absence-based features for the stations: the left station is "no ball cells in columns 4 and beyond," and the right station is "no ball cells in columns 5 and below." That way a pair at {2,3} or {6,7} is detected from the lack of other cells rather than a single column hit.

I'm checking the left-station absence feature, where a pair at {2,3} shows up as no cells at column 4 or beyond. The open question is the wrong-direction case: if I'm at {2,3} facing right and the mode flips to left, I'd fire the wrong way, so I'm considering a small chance of pressing left in that state to break the loop.

I'm checking the drift problem next: if the sub keeps pressing left past column 1, it ends up pinned at column 0 facing left, where any bullet fired is off the grid straight away. Keeping a bullet alive means firing from column 1 or higher, so I'll need to stop the left-drift before it reaches the edge.

I'm weighing a stochastic left-press in the left-station state, around 12%, so a {2,3} pair facing right can flip back and break the deadlock. The drift toward column 0 is the concern, since firing from there faces off the grid immediately.

I'm considering a tweak where the left-press probability in the left-station state drops when the sub is already at column 0 or 1, so it doesn't drift off the edge, and I'm thinking of using the two spare units to flag any ball cells in those low columns.

I'm settling the fallback for the left-station state: if the sub isn't at the station yet, press left hard; once it's there and not too near the edge, keep firing with a mild chance of pressing left. I'm also considering whether orientation can be read from the station cells, but that's unreliable because trails from other rows pollute the same channel, so I'm dropping it. Next I'll see how vertical suppression fits in as a layer-2 term, summing the in-row enemy signals, and whether divers in my row need their own handling since they aren't in the danger channel.

I'm weighing whether divers belong in the same horizontal signal as enemies, since they aren't in the danger channel and vertical seeking might pull me away from a diver that's about to reach my row. I'm leaning toward having divers count as targets too, because I need them to survive past about 200 steps, but I haven't settled how that interacts with the enemy-left and enemy-right units.

I'm weighing whether divers should count in the same left and right signal as enemies, using the danger-free channel that includes fish, subs, and divers rather than bullets. That way I'd move toward an approaching diver to pick it up sooner, though a diver receding from me would just cost a few columns of drift.

I'm weighing whether to score the enemy-left and enemy-right signals using the danger-free channel, which would count divers as well as fish and subs. That would have me move toward an approaching diver, though a receding one would just pull me along the row, and I'm wondering whether to partially suppress vertical movement while waiting for one to arrive.

I'm checking whether a sub spawned at the far left can be shot in time: if it enters at column 0 and fires about ten steps later, I'd need to reach the left station and fire quickly, so that would likely finish it before its first bullet reaches me.

I'm weighing whether a bullet already in my row can reach me once I move vertically into it, since stepping next to an incoming shot would be fatal unless I dodge. I'm considering a dodge rule that triggers on an enemy bullet close to my front in the row I'm entering, but I haven't yet found a way to tell which row a bullet belongs to from the global channels.

I'm accepting that some deaths are unavoidable and not over-engineering the design. The concern is that enemies approaching from behind while I'm at the left station could create a conflict: an enemy receding left and another approaching from the right would both activate the left and right signals at once.

I'm now asking whether the left and right signals can both be active at once, since an approaching enemy on one side and a receding one on the other would conflict. One option is to weight each side by how close the object is, another is to use the trail direction to tell approaching objects from receding ones, so I can give priority to whichever one is coming toward me.

Now I'm weighing a simpler version: the left and right signals just count whether something is present on that side, and if both sides light up at once, I'll let the two pulls add together rather than trying to rank them.

I'm settling on the design rather than a simpler row-independent approach, and turning to the oxygen-and-diver rule: when air is low and I'm carrying divers, I surface. I'll read the oxygen level and diver count off the gauge row, using the cells that light up in the bottom bar to decide whether to go up.

I'm settling the oxygen threshold: the surface signal reads column 2 of the gauge row, which only lights once oxygen is at 60 or above, so going up when that column is dark and a diver is held works. Surfacing a bit early costs a diver, but it keeps the air margin safe.

I'm settling on column 1 of the gauge row as the oxygen cutoff, so the surface signal fires below 40 instead of 60, which leaves enough margin to climb eight rows even with enemies in the way. If oxygen is low but I'm not carrying any divers, surfacing does nothing useful, so I'll keep hunting in that case.

I'm checking that the oxygen-and-diver surfacing rule holds up: at the surface the air refills and one diver is spent, and once the oxygen gauge is no longer low, vertical seeking takes over again. I'm also noting that the surface signal shouldn't fire at high oxygen, and that a fresh start with no divers means the rule stays dormant. The main thing still open is how vertical movement into an occupied row can end in a collision.

I'm now looking at the risk of moving vertically into a row where an enemy or bullet already sits in my column, which would be fatal. Since my rules can only see global channels, I can't easily check the destination row, so I'm estimating a couple of unavoidable collisions over an episode and accepting that.

I'm estimating collision risk now: with about three enemies over 80 cells, any given cell has roughly a 4% chance of being occupied, so vertical moves into occupied rows will cost a few lives per episode. I'm also noting that the rows I pass through without targets are safe, but the rows with targets are where the risk concentrates, since my vertical seeking stops at the first target row.

I'm noting that a target in the row I'm entering could sit right in my front column, which would mean an immediate collision. With targets spread across about ten columns, that's roughly a one-in-ten risk each time I move into a target row, so I'm weighing whether a danger signal for the cells just above or below my front could help, though it's hard to express relative to my row with only global channels.

I'm weighing whether to only enter a target row when the target sits far to the side, since a target landing in my front column on entry would be an immediate collision. Restricting the vertical seek to zone-edge targets would avoid that, but it would also skip the central targets I'd otherwise chase.

I'm weighing whether the player should idle in the center columns and only chase targets in the edge zones, since a target one or two columns from the station is still close enough to be risky. Moving toward the center would keep the entry gap at least two columns wide.

I'm considering whether the station should sit closer to the center, say at {3,4} facing left and {5,6} facing right, so turning doesn't require moving toward the target. Working through the turn sequence from {3,4}L to face right, the pair just slides across the middle columns, which keeps the entry gap wider.

I'm settling on seeking targets only in the outer zones, columns 0 to 2 and 7 to 9, and I'm checking whether the zone-mode signals should use the same bands. Since the player's pair sits between columns 3 and 6, enemies in those middle columns are the ones most likely to collide on entry, so I'm weighing how to keep the zones from overlapping them.

I'm limiting vertical seeking to targets in the outer edge zones, columns 0 to 2 and 7 to 9, since those are the only ones that are safe to enter a row for. Enemies in the middle columns I'm accepting as a risk, along with any hazards in the intermediate rows I pass through.

I'm estimating how often passing through intermediate rows could hit an enemy in my column, which comes out to roughly 4% per vertical step. Over a full episode with dozens of vertical moves, that adds up to a couple of deaths, so I'm checking the real numbers on how many enemies and bullets are on screen at once.

I'm now working out whether a danger-below check is worth the extra units, since each vertical move into the next row carries roughly a 5% death risk from enemies and bullets in the cells just beneath my front columns. A feature that fires when I'm in row r and danger sits in row r+1 across columns 3 to 6 would cover it, though it costs several more units. I'm also considering whether a single unit could combine those conditions instead.

I'm now considering whether to move vertically only when it's necessary, since each step into a row with danger at that moment carries a real chance of collision, and I'm weighing how to limit those moves.

I'm estimating that a danger in whichever row I move into or pass through has about a 5% chance of sitting in my column at that moment, so each vertical step carries a real risk of death. Since dangers can also drift into my cell during the crossing, I'm treating every row I pass through as a roughly 5% hazard.

I'm considering whether to skip the per-row danger checks, since they'd cost about fourteen units. Instead I'm looking at a layer-one profile of danger across the band columns, which might let layer two combine it with the player's row without a separate unit for each row.

I'm trying a threshold trick to detect danger directly below the player's row, using counts of dangers in rows at or beneath each level. The difference between two counts would isolate one row, but the row I care about depends on where the player currently is, which is the conjunction I can't express linearly.

I'm considering folding the danger check into the per-row move units: a unit that fires only when the player is in row r, targets lie below, and row r+1 has no danger. The concern is that a count of targets could overwhelm a penalty for danger, so I'm weighing how to weight the target signal.

I'm sketching the danger penalty as a weighted sum: the player's row cells get a larger weight, each target adds a little, and each danger cell in the row below subtracts heavily. I'm testing the threshold against the cases with and without a target present, to see whether the penalty can be made to dominate.

I'm now checking how a danger-below rule could be folded into the per-row move units, so that stepping down into row r happens only when a target sits lower and row r+1 is clear of danger. That would need about eight units for downward moves and six for upward ones, close to the original budget, but I'm still unsure how the target and danger counts will balance against each other.

I'm folding the in-row target check into the downward-move units as a negative weight, so a target in my own row suppresses stepping. That brings the total to about 28 move and horizontal units plus a few features, leaving one spare unit, which I'm considering for dodging. I'm also wondering whether row 1 needs its own horizontal units, since the player can pass through it.

I'm reconsidering the row range: letting the player occupy rows 1 through 8 would need 33 units, one over budget. So I'm restricting the vertical seeking to rows 2 through 8, which brings the edge-zone horizontal units down to 14 and keeps the total within limits.

I'm now checking whether targets in the middle columns should count for vertical seeking, since they'd vanish from the edge-zone check once they drift inward. If they do, the horizontal mode could switch off mid-row and leave me vertically seeking while a target is still close.

I'm checking whether shooting alone handles enemies closing in from the edges: a bullet fired from the front cell reaches an approaching enemy within a couple of steps, so a fast-firing player should catch most of them. Middle-column objects are the gap, since they cross without ever entering my targeting zones, and vertical moves into rows where they sit could still be risky.

I'm checking how to handle enemy bullets, since they're lethal in my row but my targeting channel ignores them. The spare unit might cover dodging, though that would need a separate unit for each row, so I'm leaning toward skipping it.

I'm considering widening the destination-row danger check so bullets in the outer columns also count, since those can reach me within a few steps. The trouble is that bullets and fish share the same channel, so I'd have to separate them as bullets being channel one minus channel two, which makes edge enemies and divers push the penalty in opposite directions.

I'm weighing whether bullets in the outer columns of the destination row should count as danger too, since they could reach me within a few steps. I'm stuck on how to tell bullets apart from enemies and divers that share the same channel, and I'm leaning toward accepting the risk of rare bullets rather than adding dodge logic.

I'm weighing whether edge-column bullets should count toward the destination-row penalty, and I'm considering giving edge columns a -10 weight for channel one and a +10 weight for channel two, so divers there offset it. The worry is that a diver's +10 could cancel out a middle-column danger penalty, so I'm thinking about setting the middle-column danger weight higher, around -20, to keep it dominant.

I'm now weighing a huge player-gating weight, around 15 per cell, so the player-absence check dominates any positive boost from divers at the edges. I'm also questioning whether a danger check on the destination row even matches the band I actually need to guard.

I'm checking whether bullets in the destination row's outer columns should count as danger, since my current danger check skips them. Still, I'm leaning toward accepting that risk and treating the edge-zone waiting as cheap, since blocking entry into a row with danger at cols 2..7 already covers most cases.

I'm considering making the up-move also serve as a surfacing move when oxygen runs low and a diver is present, by adding a surfacing term to the MoveUp units alongside the existing target-above count. I'm wondering whether that surf signal should override the danger gating, since surfacing matters more than avoiding a risky row.

I'm noting that the surfacing problem doesn't fit a per-row budget of 33 units, so I'm considering a global Surf unit that pushes up directly. The catch is that it skips the danger checks, so I'm thinking about adding a surf term to the upward units for rows 3 and above, letting the rest rise only when they're clear.

I'm laying out the unit budget by row: move-down units for rows 0 through 7, move-up units for rows 3 through 8, and edge-zone horizontal units for the rows I'm still tracking, which should bring the count to about 33. I'm also considering a separate global surfacing signal for the top rows, since per-row units can't cover them without going over budget.

I'm checking whether the Surf signal should also gate the lowest move-down unit, since at row 0 the oxygen should already be refilled and surfacing no longer matters.

I'm making sure the down units stay off whenever the surfacing condition holds, since a linear suppression term would backfire at the edge case where the signal is -1. So I'll handle it instead with a conjunction in the second layer, feeding a suppression of the down logit into the output.

I'm now making the down units switch off whenever the surfacing condition holds, which I'll do with a suppression term in the output rather than a linear term that would flip sign at -1. I'm also adding a surfacing term to the upward units for rows 3 and above, so they can rise safely while still checking danger above.

I'm checking whether the MoveUp units should also open when oxygen is low and no divers are present, so the upward term uses a negative weight on the column-one signal, with a bias of +3 to cover the case where that signal is unlit. That way going up toward row 2 stays available whenever oxygen is below 40, even if it's a bit pointless there.

I'm trying to pin down a surfacing signal that holds only when divers are present and oxygen is low. A raw linear combination of the two column flags would flip the sign in the common case of no divers, so I'm looking for a way to isolate the exact condition.

I'm testing a candidate threshold for the MoveUp unit: adding a bias and a weighted difference between the two column flags, then checking which combinations of target count, player presence, and danger switch the unit on. The case with no targets above and only one flag lit is the one that currently fails to turn it off.

I'm searching for a threshold where the bias and the two column weights give the right on/off pattern: the unit should be active when there are targets above or the surfacing condition holds, and off otherwise. I'm checking the case with no targets, where I need a negative bias but a positive weight on the divers column, and I'm running into a constraint that the bias has to be both positive and negative.

I'm testing a bias of -0.5 with a weight of 0.4 on the column-one flag, and a weight of 0.7 on the column-eight flag, to see whether the threshold gives the on/off pattern I need. Most of the cases check out, and I'm verifying the last one with one target above and only column one lit.

I'm settling on a threshold unit where the target count adds 10 per target, the column-eight flag adds 7, the column-one flag subtracts 4, and the bias is -5. I'm checking that this gives the right on/off pattern across the cases, and scaling the player gate and the danger penalty of -40 to match.

I'm settling the MoveUp unit's formula so it turns on for surfacing and for targets above while staying off under danger. The surfacing piece only needs to hold when divers are present and oxygen is low, so I'm working toward a threshold that separates that case from the others, with rows 3 and up using this unit and rows 1 and 2 handled by the global surfacing signal.

I'm now setting the MoveUp weights for rows 3 through 8, so that targets above and the surfacing condition both push the unit on while danger above turns it off, and I'm working on how the player and in-row terms should scale against those.

I'm now considering a simpler split: keep each MoveUp unit tied to targets above and no danger above, and handle surfacing separately in the second layer, so the surfacing gate doesn't have to be squeezed into one threshold.

I'm now weighing whether the MoveUp units should also account for danger above and surfacing together, since a pure safety gate wouldn't tell the unit when to actually want to rise.

I'm checking which columns count as danger for a destination row, noting that columns 2 and 7 overlap with the edge targets and so block the move conservatively. I'm also confirming the player stays within the station pairs, with the startup position at columns 5 and 6 being fine.

I'm now writing out the MoveDown units for each row from 0 to 7, summing the player's presence in that row, the targets below it in the edge columns, and a penalty for danger in the row beneath, with a suppression term when a target sits in the same row.

I'm settling the MoveDown weights so the in-row suppression is strong enough to win, giving the in-row target a -30 weight and setting the bias to -2G - 5 so the unit stays off with no target and turns on only with a target below.

I'm settling the absent-player case: with at most eight targets adding 10 each, a bias of -85 keeps the unit off, and I'm setting the player weight to 40 so being in the row dominates the sum. Danger in the row costs -40 per cell, and I'm keeping these raw values rather than scaling them down, since the ±5 margins already saturate the output.

I'm now defining the MoveDown units for each row, counting targets in the rows below that sit in the edge columns, with a strong suppression when a target shares the row and a penalty for danger in the row beneath.

I'm working out the MoveUp units for rows 3 through 8, weighing the player's presence, targets above in the edge columns, and in-row suppression against danger in the row beneath. I'm trying to set a surfacing term that fires without targets, and I'm starting to tune the bias to match.

I'm finding that the in-row suppression of -30 per target is too strong for surfacing to override, since the surf terms can only be scaled to about one target's worth in this linear setup. I'm considering lowering the in-row suppression for MoveUp so that surfacing can win when I'm in a row with a target.

I'm weighing whether the MoveUp surfacing term can ever beat an in-row target, since the -30 suppression is hard to overcome. I'm considering a shorter oxygen threshold for the surfacing trigger, with column 2 instead of column 1, to leave more time for the climb and for waiting on a receding diver.

Now I'm setting the MoveUp surfacing term as a shorter oxygen check on column two, and I'm verifying the case where there are no targets above and the surfacing signal is on, which comes out just barely positive.

Now I'm scaling the MoveUp weights up: the player term at 80 per cell, targets above at 20 each, and the surfacing signal from column eight and column two at 14 and -8, so the margins are wider than before.

I'm rescaling the MoveDown weights to match: 80 per cell for the player, 20 per target, -60 for in-row suppression, -80 for danger, and a bias of -170. That gives a small positive margin when a target sits below and the player is present, and negative margins otherwise.

I'm raising the MoveUp danger penalty to -200 per cell, since four targets above could otherwise outweigh a danger cell, and making the in-row suppression -100 so that a target in my row still wins over the surfacing signal. Those larger values also keep the absent-player case negative, since negative terms only help there.

I'm rescaling the Seaquest unit weights again, this time making the MoveUp danger penalty -200 per cell and checking the surfacing margins against that.

I'm settling the EL unit's weights: 10 per player cell in the row, 6 per target in columns 0 through 2, and a bias of -23, so it fires only when I'm in the row with a target nearby.

I'm settling the ER unit to look at targets in the right-hand edge columns, and the two station units by whether any player cell lies to the right or left of columns 3 and 4, with weights that flip sign depending on which side the pair sits on.

I'm settling the mode logic for the left and right pull: the left mode turns on when a left-side station unit is active, and the right mode when a right-side one is, with both adding if they fire together. In the left mode I'm weighing whether to press left when the station isn't yet on my side, or to fire when it is, and I'm noting that drifting too far left would leave the fire useless against the edge.

I'm checking the drift problem: a mild rightward press from the correct left-facing spot would tip it back into the deadlock state, so that fix doesn't hold up.

I'm checking whether a mild left press fixes the stuck state: from the wrong-side position it puts the station back on my side in one step, and from the correct spot it only shifts me one column. The remaining issue is drifting too far toward the edge, so I'm looking at a separate far-left correction.

I'm now looking at whether the left-press logic can cover the far-left drift without needing two more units, since the list is already at 32 and there's no room for new ones.

I'm trying to make the StL unit grade its output, so that the exact pair at columns 3 and 4 scores high, nearby pairs on the left score near zero, and pairs reaching the right-hand columns score negative.

I'm settling the station units with a graded output: a clean pair at columns 3 and 4 scores highest, pairs one column further left score lower but still positive, and anything reaching the right-hand columns goes negative. I'm checking the level values so that the pair at columns 1 and 2 doesn't land in the same bucket as a non-station state.

I'm trying a smaller slope on the station unit, with the danger and the far-left penalty folded into one value, so that the pairs at columns 3–4 and 2–3 come out clearly separated from the edge pairs. The lower outputs for the pairs further left and for the ones at columns 4–5 are still too close together, and I'm not yet sure the weights keep them apart.

I'm now sorting out the layer-two mode units for the left press: I want the fire to trigger whenever the station sits at columns 3 or 2 on my side, and only add a mild left press when it's clearly at 3 and 4.

I'm now defining the layer-two units that combine the left-mode indicator with the station signal, so the left-mode gets a go-left unit that fires when the station isn't on my side.

I'm defining the layer-two unit that fires only when the left mode is on and the station is not yet on my side, using a weighted combination of the mode indicator and the station signal. I'm also converting the mode from the sum of the row units into a plus-or-minus-one value so the weights can be set cleanly.

Writing layer-two gating units now: one fires when the left mode is on and the station is on my side, another when it isn't, and a third for a stronger mild-left press, with the pre-activations scaled so the signs come out right.

I'm settling the mild-left idea: I'll fold the fire into the default action so that only the strong left press is a separate unit, and check whether a mild left press at the {2,3} spot pushes the station into the not-quite-there range.

I'm checking whether pressing left at the {2,3} spot can drift too far, and whether a wider station unit that also covers the {1,2} and {0,1} pairs would keep the left logic from pulling the player further toward the edge.

I'm thinking about the drift risk now: mild left presses could push the player toward x=0, where firing is useless and enemies from the left can hit right away. I'm considering lowering the mild-left probability to around 5% and checking how often the station gets stuck on the right side.

I'm checking whether the stuck state can arise during a switch from right mode to left mode. If both the left and right targets are active at once, the station on the left side fires while the right press takes over, and that can leave me oscillating in the middle.

I'm noting that the edge-zone check fits within columns 0 to 2, so a drift to {1,2} still overlaps it, and that's acceptable. Without an active mode, I'd keep the player near the center, since the stations already sit next to the middle. Vertical movement is only driven when no mode is active; once one is on, I'm suppressing the up and down moves while an in-row target remains.

I'm checking whether pressing up or down could be triggered by accident, since at row 1 an up press with no divers around would be fatal. I'm settling on a bias for down and fire as the defaults, with up held back.

I'm checking whether a sticky up-press could carry the player from row 2 into row 1 and then row 0, where there are no divers to be saved by. Each such step is small, but over many rows it adds up, so I'm considering dropping row 2 from the targets altogether.

I'm checking whether pressing up could carry the player into row 1 by accident, and I'm settling that a 1% risk per arrival at row 2 is acceptable, so I'm keeping row 2 targets in play. Row 1 gets no in-row logic, so descending from there is fine. The open question I'm turning over is what horizontal behavior to use when an enemy approaches in-row but has no target.

I'm checking the edge cases now: a target in the middle columns isn't counted as in-row, so moving vertically there is a reasonable dodge. A receding diver near the left edge will still be caught by the fired bullet, though I may have to wait up to about 12 steps for it to leave.

I'm turning over how the mode and vertical moves interact: if targets sit both above and below, the up and down logits both fire and the choice turns random, though the danger check keeps each step fairly safe. I'm leaving that as it is and watching for a possible stall where a target below sits three rows down while danger covers the row in between.

I'm checking whether an enemy in the middle columns of my row could approach unseen, and concluding that arrival checks plus the edge-zone targeting cover most of that. The remaining gap is enemy bullets in the edge columns, which I'm not checking yet.

I'm now weighing bullets against enemies and divers in the destination row's edge columns: bullets should be penalized, while enemies and divers need separate handling so the weights don't block useful moves.

I'm weighing the bullet penalty against the diver bonus in the destination row's edge columns: a diver's +200 could cancel a middle-danger penalty, so I'm considering scaling the danger weight up to -500 and the presence weight to 400 per cell so the gating stays negative when nothing is there.

I'm weighing whether a bullet check is worth it in the destination row's edge columns, since a diver's +200 bonus could override the in-row suppression and pull me toward a diver in an adjacent row. Enemy bullets only matter on the edge columns, and with roughly one bullet on screen at a time, I'm leaning toward skipping that check.

I'm settling the bullet check for the destination row's edge columns: a bullet there is penalized, and a diver gets a matching bonus. I'm weighing whether that bonus would overpower the in-row suppression, which pushes me to tune the in-row penalty to keep it in check.

I'm checking the edge-column case in the destination row: an enemy sitting at column 2 would count toward both the middle-danger penalty and the edge-zone weights, so I need to decide how to define the edge columns so the penalties don't double-count.

I'm checking the scoring numbers for the move-up logit now: with the per-cell presence weight at 300, the base bias comes to -610, and the edge-column surf terms only shift the result by small amounts. The cases I'm testing are the ones where the destination row has no danger and no in-row target, and the sums there come out at a few points either way.

I'm checking the up-move scoring with the surf terms: when an in-row target is still present, the -200 suppression keeps the logit negative, and only once that target is gone does the edge-column surf pull me up.

I'm settling the destination-row edge weights: bullets there get -150 and divers +150 on the same cells, with the target count adding +20 on top, so a diver nets +170 and an enemy stays near zero. The middle columns of that row carry -400 for danger, which keeps those moves blocked.

I'm checking whether the diver bonus at row 1 would pull the player up there for no reason, since only rows 2 through 8 count as targets. I'm considering giving row 1's edge columns only the bullet penalty and no diver bonus, so the move stays clean.

I'm now going to finish the edge-column scoring: enemies and divers in the destination row's edge cells should net roughly zero or a small bonus, and I'm keeping row 1 in mind so a diver there doesn't pull me upward for no reason.

Next I'm handling the per-cell presence weights and the edge-zone targeting for rows 2 through 8, then the global Surf and Top units for rows 1 and 2. I still need to suppress the down logit when Surf is active, which means a layer-2 adjustment.

I'm now setting up the layer-2 downward unit: it should fire only when some down-move unit is active and Surf is off, so I'm folding those two conditions into one weighted sum.

I'm checking the layer-2 gating now: the DOWN unit should stay negative whenever Surf is on, and the UP unit should fire on any active up-move or on Surf together with Top. I'm writing the thresholds for those as weighted sums, and I'll give the left-gate unit a bias so it only turns on when the left-edge enemy count is positive and StL is negative.

I'm writing the activation gates for the left and right edge units next, with a mild-steering variant for each side based on the sign of the steering input. I'm also considering whether to add a mode unit that combines those edge gates.

I'm now writing the layer-2 output logits: a down unit gated on any downward move being active and Surf being off, an up unit that fires on any upward move or on Surf together with Top, and left/right units gated on the edge-enemy counts and steering, with mild variants alongside them.

I'm now setting the output logits: fire gets a default bias of 2, the other actions sit near zero, and up is pushed down to -4 so it doesn't fire by accident. I'm checking the down action next, since a stray down move risks collisions, and I'm estimating the resulting sampling probabilities to see whether fire ends up dominating too much.

I'm settling the output logits: fire gets a high default of 6 so it dominates, and the active movement actions need around 12 to beat it. The mild steering variants get a weight of 3, which keeps them near 5% sampling probability. I still have to deal with the conflicts where left and right, or up and down, both fire at once.

Now I'm setting the output logits for the up action: a baseline of -4, with a boost when the any-up unit is active and a larger one when the surf-and-top unit is active, so surfacing overrides everything.

I'm setting the output biases so that fire stays the default, with up at 16 minus its contributions, down at 6, and left at 7.5, so each active movement reaches about 12 and beats fire's 6.

I'm now checking the left and right mild-steering units against their firing thresholds, and confirming that a mild move comes out near 3 so it stays around 5% sampling probability.

Checking the sign of the GoL pre-activation at the boundary case, where the left-edge count is one above its threshold and the steering value is just under the neutral point.

I'm checking the left-gate output at the {3,4} boundary: the mode unit comes out around 2.8, so left stays well above fire's default but still sits near the mild-steering range.

I'm double-checking the stop-left boundary values: at column pattern {1,2} the steering comes out near -0.46, so the left gate ends up slightly active and pushes the player toward x=0. Once there, the steering reads about -0.905 and the left gate keeps firing, so the player would press left at the edge indefinitely in that mode.

I'm checking the stuck state where we're at {3,4} facing right in left mode: the steering still reads positive, so we'd keep firing right, and the mild left only triggers about 4% of the time. An enemy coming from the left could reach us in roughly 24 steps, so I'm wondering how often this state actually happens.

I'm checking the initial state under the right-mode policy: starting at columns 5–6 facing left, the right-steering reads as a station, so the agent would just fire while still facing the wrong way, and the mild right move only triggers about 4% of the time.

I'm thinking about lifting the mild-steering probability to around 25%, since drift is capped at the {2,3} station and a wasted step at {3,4} costs little, which would also repair the stuck right-facing state faster.

I'm checking the mode-R stuck case: from {2,3} facing left, a right press moves me to {2,3}R, and then the right gate pushes me on to {5,6}R. If the mode flips to L while I'm at {2,3}R, the steering reads as a station, so I'd fire facing the wrong way, with only about a 0.6% chance of a left correction.

