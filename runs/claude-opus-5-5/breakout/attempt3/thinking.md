I'm sketching a policy network for MinAtar Breakout and weighing a simple rule: steer the paddle toward the ball's x position. A better option is to predict where the ball will land, since it moves one column per step while the paddle moves one per step too, so following its x only works once the paddle is already aligned.

I'm weighing whether the paddle can just track the ball horizontally, since both move one column per step, but that only works if it's already under the ball when the ball reaches the bottom rows. A better target is the x where the ball will land, which means predicting its position from its current spot and direction.

I'm considering whether the paddle can just follow the ball's x, though that only works if it's already lined up when the ball reaches the bottom. A stronger idea is to compute a target column where the ball will land, since the ball's position and direction together determine it. The catch is that the wall reflections make that prediction nonlinear, which is hard to capture with only a few hidden units.

I'm checking whether following the ball's x works in practice: if the paddle sits one column behind and moves right, it still lands under the ball at row 8, since the catch check accepts the ball's pre-move x. So a lag of one is fine, and simple tracking holds up as long as the paddle keeps pace.

I'm checking that the paddle keeps up once the ball starts bouncing: after a hit the ball heads back up, and since the paddle moves one column per step like the ball, it stays within a step of the ball's x. Starting from the ball at the left edge at row 3 and the paddle at column 4, I'm tracing how the paddle moves left toward the ball's path as it travels down-right.

I'm checking the paddle's pace against the ball: if they start aligned, a steady one-column move each step keeps it close enough to catch. Sticky actions could throw that off, though. I'm also looking at how the paddle-hit bounce flips the ball's horizontal direction, which keeps it inside the catch window.

Bricks are involved here: when one is hit, the ball's vertical direction flips but its y stays put, so it only shifts horizontally on that step. I'm also noting that the ball never actually reaches row 9, since the bounce keeps it at row 8. And I'm checking the strike logic, where a brick hit while the strike is already active passes the ball through without reflecting it.

I'm reasoning about whether simple tracking will hold up over a long game, since sticky actions could make the paddle fall behind. Predicting the landing spot and moving there early seems more robust than chasing the ball, so I'm considering that approach next.

I'm wondering whether the paddle can stay safe over a long game, since a loop of ball paths through already-cleared channels could run until the step cap and score nothing. Deterministic tracking alone might not be enough, so I'm weighing whether predicting the landing spot and moving there early would hold up better.

I'm now considering whether the paddle should aim for the predicted landing column, since the catch direction depends on whether the paddle sits at the ball's pre-move x or at its new x. I'm weighing whether to move to that landing spot early and wait there.

I'm working through the edge case where the ball reflects off a wall: when it reaches x=0 moving left, it stays in that column for one step and only moves vertically, which shifts the timing of when it arrives at the bottom.

I'm working out the wall behavior as a folded coordinate: the ball's x repeats with period 20 across the two wall bounces. From there I want to predict the landing column at row 8 by folding the ball's current x plus its horizontal drift over the remaining steps, and treat moving-up cases separately since the ball has to reach row 0 and come back down first.

I'm working out how the ball's horizontal and vertical motion fold back at the walls and the top row, so I can predict where it will be when it reaches row 8. Going upward, the ball has to reach row 0, stall there for a step, and come back down, which adds a fixed delay before it reaches row 8. Bricks could still change that timing, so I'm treating these upward cases as less reliable.

I'm thinking about how to represent the ball's position and direction in the first layer, since the target depends on both together. Direction can be read as the difference between the ball's column and its trail's column, which a linear combination of the two one-hot inputs can capture.

I'm thinking about a gating trick for layer one: a unit that outputs the sign of the target minus the paddle only when the ball is moving in a given direction. The problem is that a plain additive gate saturates to -1 rather than 0 when the direction doesn't match, so I'm weighing how to get clean gating out of the tanh.

I'm now trying to get the target from the ball's cell and its previous cell together, by building an additive decomposition so the direction doesn't need a separate gate.

I'm checking whether the target can be split into a part from the ball's cell and a part from its trail cell, since the direction comes from comparing the two. The unfolded position x + dx*(8-y) multiplies terms together, so it isn't additive, though the product might simplify once the trail's row is substituted in.

I'm trying a bilinear form for the target so the direction is handled without a separate gate: downward motion works out to a clean sum of a ball-cell term and a trail-cell term, but the upward case doesn't match the timing I want. So I'm looking for a more general form that fits both directions.

I'm checking whether a single bilinear form can cover both directions, so I'm solving for the coefficients that make the time-to-row-8 expression come out right for downward and upward motion alike.

I'm checking whether the upward-moving case can be folded into the same additive form, since the cross terms don't separate cleanly. The downward formula would give a wrong target when the ball is rising, so I'm leaning toward a simpler fallback for that case: having the paddle track the ball's x directly.

I'm settling on a gating scheme for the first layer, since a plain additive gate saturates to -1 instead of 0 when the direction doesn't match. Then I'm looking at folding the unfolded landing position u back into range, which runs from about -8 to 17 for a downward ball.

I'm now working out how to fold the unfolded position u back into the 0-9 range, and which u values land on the left, right, and reflected sides. I'm checking when the folded target exceeds the paddle position p, and noting that the right-side condition splits into three regions: the in-range case, the case below zero, and the case from 10 up.

I'm checking the left-side condition now, which should mirror the right-side case: the paddle goes left when the folded target falls below p, and I'm testing the u values in the 0-9 range against p to confirm it works.

I'm checking the left-side condition against the folded target, using the sum and difference of the unfolded position and the paddle, and I'm working out where the stay case falls.

I'm checking the layer-one units that separate the paddle's position from the folded landing column, using sigmoids on the differences between the unfolded target and the paddle, and I'm thinking about how to combine those in the next layer to get right, left, and stay outputs.

I'm checking whether the paddle can actually get to the landing column in time: from a ball at row y, I get 9-y actions before it reaches row 8. So the question is whether the distance from the paddle to the target fits within that budget, and whether an alternative target one column further would be easier to reach.

I'm checking how long the return trip takes after a bounce, roughly nine steps, which gives the paddle about nine actions to cover the horizontal distance. The catch is that the target formula only holds for a downward ball, so for the upward phase I'll need a separate fallback, maybe just following the ball's x.

I'm now checking whether the paddle can follow the ball's x while it rises and still reach the landing column in time once the ball turns downward. The gap is at most one column of lag plus the remaining distance, which still fits the nine actions available, though it's tight.

I'm trying to find coefficients for a single linear-in-state form that gives the right landing column when the ball falls and something sensible like tracking the ball's x when it rises, by testing whether the trail's row can be folded into the same weights.

I'm trying to fit a linear form for the target so it gives the right landing column when the ball falls, but the upward case comes out as 3x plus a term in dx, not x. So a simple linear-in-state formula can't track the ball's x while rising, and I'd need nonlinear or per-cell weights to make that work.

I'm dropping the idea of fitting one linear form to all four diagonal neighbours, since the constraints look overdetermined. Instead I'm considering a sign trick: add a large term scaled by the vertical direction of the ball relative to its trail, so the downward and upward cases separate in the first layer.

I'm now checking whether the upward case can use a sign term that pushes those units to -1 when the ball is moving up, so the downward formula only takes effect when the ball falls. For the rising ball I'd compare the ball's x directly against the paddle.

I'm considering a fallback for the upward phase: keeping the paddle under the ball's x while it rises, since the downward target formula only applies once the ball turns. I'm weighing whether that tracking still leaves enough actions to reach the landing column, since the lag plus remaining distance is about 9-y, which is tight but workable.

Checking whether the paddle can make it in time: if it lags one column behind a ball that keeps its horizontal direction, the distance to the landing column is 9-y, which matches the 9-y actions available. That is exactly tight, and the alternative target one column further only makes it harder. So the catch depends on the paddle hitting the ball's x at row 8 precisely.

I'm settling on a sticky-action check: if the paddle keeps moving the same direction, a repeated action doesn't hurt, so the tight timing mostly survives. I'm also considering making the upward phase lead the ball by a column or predicting its return, though that gets complicated.

I'm weighing a tracking target for the upward phase, but the paddle moves at the same speed as the ball horizontally, so it can only stay over the ball, never get ahead of it. Looking closer at the timing, the paddle can at best sit right under the ball's x, and any lead target just goes unreached unless a wall bounce helps.

I'm noticing that a ball bouncing off a brick flips its vertical direction while its trail still shows only horizontal movement, so the downward-gating check would read D=0 at that moment. I'll need to decide how to classify the ball's direction in that case.

I'm noticing that a brick hit flips the ball's vertical direction while the trail still shows only horizontal movement, so D reads 0 right then. Whether that means "going down" or "going up" depends on how far down the board the ball is, since bricks sit in the upper rows.

I'm checking the wall-stall cases now: when the ball sits against a side wall and only moves vertically, the trail shows no horizontal change, so my formula would give the wrong landing column. I'd need the horizontal direction to be reflected, not read from the trail, for those positions.

I'm working through the unfolded-coordinate trick for the stalled case: when the ball sits against a side wall at x=0, I can treat it as sitting one step past the wall in the unfolded line, which makes the landing column come out right after folding back.

I'm now weighing whether to split the problem into separate cases for the direction-zero and wall-stall situations instead of folding them into one formula, and I'm counting how many layer-one units that split would take.

I'm now treating each direction separately: for every one of the four diagonal directions, I'd compare the precomputed landing column against the paddle, gated so it only fires when the ball's trail matches that direction. The stalled and zero-trail cases still need their own handling.

I'm working out how to handle the stall case, where the ball sits against a side wall and only moves vertically, so its trail shows no horizontal change. My idea is to bias the direction score for those wall-column cells, treating the stalled ball as moving away from the wall, so the sticky landing target still matches.

I'm working out the landing column for a ball moving down-left versus down-right when it sits against the left wall. Along the wall the same cell gives different landing columns depending on the horizontal direction, so the stalled state needs its own lookup rather than the general formula.

I'm checking the wall-stall cases in the ball's trail: when the ball sits in column 0 with no horizontal change, I'd treat it as moving right, and at the top wall with no vertical change, I'd treat it as flipping to moving down.

Now I'm settling how to handle the effective direction when the trail shows no change. A zero horizontal change at a side wall means the ball is actually heading back the other way, so I'll read it that way. A zero vertical change means a top-wall bounce or a paddle or brick hit, and in the brick rows I'll assume the ball is heading down.

I'm trying to make the direction terms linear, but the wall cases break the simple form. When the ball is in column 0 and the trail shows the same column, it has stalled and is effectively moving right, so I'd need to add a correction term for that. Checking the ball-at-0-with-trail-at-1 case, the raw difference gives -1, and a half-weighted wall term only partly fixes it.

I'm checking whether the ball's landing column can be read from its trail alone, or whether the wall stalls break that. At x=0 the left and right directions only differ by one column, so the error is small but still there. I'm considering anchoring the calculation to the trail cell rather than the ball cell to see if that avoids the stall problem.

I'm now splitting the stall case out as a dx=0 branch, where the landing table depends on which wall the ball is against: the right-moving table on the left wall and the left-moving table on the right wall. I'm also thinking about gating each direction with a penalty that scales with how far dx is from the target value.

I'm handling the stall case at column 0 by adding a bonus to the right-moving gate, so a ball sitting on the left wall still counts as moving right while one that just arrived moving left stays excluded.

I'm checking whether the left-moving units can handle the column-0 stall: their gate gets a bonus when the ball sits in column 9, so a stalled ball there still counts as moving left, while a ball that just arrived at column 0 moving left still uses the left-moving landing table.

I'm checking the brick-bounce case in row 0, where the ball may stall and then head down, so the downward table is only off by a step or two there. In rows 1 to 4, a ball with no vertical change is ambiguous, but I'm leaning toward treating it as heading down and accepting the occasional mistake.

I'm checking the gate for the downward units when the ball sits in rows 0 to 4 with no vertical change. Adding a bonus there would push the gate above zero when the ball is already moving down, which would saturate the unit wrongly, so the bonus has to be offset.

I'm trying to build the bonus term so the gate stays exactly zero when a unit should fire, using both the ball's row and the trail's row. I'm working out what function of each row gives the right value for moving down, staying level, and moving up.

I'm stuck on the rows 1 to 4 case: a ball with no vertical change could be a brick bounce going up, and no additive row term can make the down gate fire for it without breaking the other cases. My fallback is to let the units stay idle for that one step and accept the lost movement.

I'm now considering an alternative: keep the layer-1 comparisons ungated and let a second layer combine them with direction indicators, so the additive gate offsets no longer have to be exact.

I'm looking at whether a threshold unit can encode the down-direction indicator, since it only needs a positive pre-activation for the enabled cases and a negative one for the rest. A linear function of the ball row and trail row might be enough to separate them, with the rows 1 to 4 flat case as the one that's hardest to fit.

I'm picking a linear form for the vertical direction gate: the ball's row minus its trail row, plus a bonus that is positive in rows 0 to 4 and negative in row 8. That way a flat step in the upper rows still registers as moving down, while the bottom row keeps the paddle-bounce case going up.

Now I'm handling the column-0 and column-9 stall cases for the horizontal direction indicators, with the rightward signal using the ball's column offset plus a small correction for the left wall. The vertical indicator works the same way, keeping the top-row and bottom-row cases separate.

I'm checking the right-moving case at column 9: a ball that just arrived there moving right should still count as moving right, so the gate needs to keep it enabled while the left-moving table handles the other side.

Now I'm turning to the upward-moving ball: it reaches row 0, stalls for one step while still drifting sideways, then comes back down, so its horizontal target is roughly its column plus its vertical distance plus one, unless a brick bounces it earlier.

I'm weighing a target for the paddle while the ball moves upward: with a brick hit the landing column shifts unpredictably, so I'm asking whether it's better to stay under the ball or to sit where the worst-case distance to its eventual landing is smallest.

I'm checking the landing estimate for a ball that has just turned downward: if the paddle sits directly under it, there's no slack for the remaining horizontal distance, so the lag-one position is worth testing.

I'm checking the paddle's landing target once the ball turns downward: with the paddle one step behind the ball, the remaining distance is exactly enough, so tracking works. The real risk is a brick-bounce frame where the ball's row doesn't change, which could waste a step, and I'm wondering how the downward gate handles that.

I'm considering whether the paddle could lead the ball during the upward phase instead of trailing it, since a leading paddle might cover the wall bounce that a trailing one would miss.

I'm checking the paddle's position right after the bounce: if it sits under the ball's current column, the ball ends up one column ahead of it on the next step, so the paddle is lagging by one.

I'm checking whether following the ball's x with a one-step lag still works on the way down: when the ball reaches row 8, the paddle moves right onto its column and catches it. Since that holds in every phase, prediction mainly matters near the walls and when the lag grows larger.

I'm checking the catch case where the ball reverses horizontally: if the paddle sits one column past the ball when it comes down, the ball ends up level with the paddle and heads back left, so the paddle just follows with a one-step lag. Following the ball's x seems to work in every phase, and prediction mainly matters near the walls and when the lag grows. I'm now tracing the ball's path from the start, moving down-right from column 0 with the paddle at column 4.

I'm checking the paddle's tracking again: from column 4 the ball's path lands it at column 6 at row 8, and following its x with a one-step lag catches it in every phase. The one thing that could break this is sticky actions, so I'm working out how the paddle behaves at the wall: if the ball stalls at column 9, the paddle holds there and stays put.

I'm working through the sticky-action failure case: if the paddle stalls at a wall and the previous noop repeats, it can fall two columns behind and never recover before the ball comes down. That makes pure following fragile, so I'm leaning toward building in slack by aiming at a predicted landing point during the downward phase.

I'm weighing whether the paddle should aim for a fixed predicted landing during the downward phase, since that leaves it time to wait. During the upward phase the open question is which target keeps it close to where the ball will come down, and I'm checking whether a point ahead of the ball, shifted by its horizontal direction, would work better.

I'm weighing whether the paddle should aim ahead of the ball during the upward phase, so that when the ball turns downward the remaining horizontal distance is smaller. The gap between the paddle and the ball's eventual landing point should then be roughly the vertical distance left to travel, adjusted by how far ahead the paddle has been set.

I'm considering whether the paddle could sit ahead of the ball during the upward phase, around a target that is about six steps out. That would leave plenty of slack once the ball turns downward. The catch is that the paddle can't get ahead of a ball moving at the same speed unless a wall helps, so I'm checking whether it can actually build that lead.

I'm noticing that a stationary target might work during the upward phase: if the paddle aims at a fixed landing point built from an assumed return row, the ball's horizontal drift cancels out, so the paddle can move there and wait. The open question is which return row to assume, since the bricks make it uncertain.

I'm weighing a fixed up-phase target built from an assumed return row, so the paddle can move there and wait. If the ball actually turns higher than assumed, the landing shifts by two columns per row, so the estimate would be off by that amount.

I'm working out the up-phase target in terms of the turn column x', since the landing depends on the brick row r where the ball actually reverses. With an assumed row of 3, the target stays fixed along the upward path, and I'm checking how far it sits from the true landing when the ball turns higher.

I'm working out the up-phase target as a function of the turn column, and the gap to the true landing comes out to 2 columns per brick row the ball has to clear. Assuming the brick row is 3 gives zero offset, while higher reversals leave more travel to cover, but there are still at least several actions of slack in each case, which beats pure following.

I'm redoing the up-phase target with a general assumed return row r0, where the target is x + dx(y + 7 - 2r0). Working through the offset from the true landing, the gap comes out to 2(r0 − r) columns, so it's zero only when the assumption matches the actual brick row.

I'm testing whether a target of r0 = 1.5 would balance the slack better than r0 = 2, since the r=3 and r=-1 cases come out to 2 and 4 columns of distance.

I'm settling on a fixed up-phase target built from an assumed return row of 2, which leaves at least three steps of slack across the likely brick rows. The paddle has about 4 to 8 steps during the upward phase to reach that target, and if it doesn't get there in time, the exact down-phase target takes over with whatever slack remains.

I'm settling on the paddle lookup: a table keyed on the ball's cell gives the target position, and the paddle compares its own one-hot position against it. I'd need four such tables, one for each combination of vertical and horizontal direction, plus two direction indicators to select among them.

I'm writing the pre-activation for each direction's ball-target comparison, then adding per-direction threshold units that fire when the target is above or below the paddle. I'm also adding the two direction indicators, horizontal and vertical, that gate which of the four tables applies.

Writing the layer 2 AND gates and output logits...

Setting the layer-2 output logits so the right and left actions each get a boost of C only when one of their gate units fires, with a baseline on the no-op logit so the paddle waits when it's already on target.

I'm settling the output layer: with the left and right actions each driven by a bias of -10 that flips to +10 when a gate fires, the paddle moves only when a target is clearly off. Then I'm asking whether the layer-1 units can be merged to cut the eight threshold units down.

I'm checking the bounce case where the ball is at row 8 moving down: the target is simply the ball's column, so the paddle either stays put or steps onto that column, and either way the catch still works. I'm also noting that the sticky action could matter in that moment, but otherwise the simple rule holds.

I'm settling on the catch: if the paddle is exactly under the ball, the bounce keeps the horizontal direction, and the ball effectively stalls for a step at the bottom row. Without any paddle influence, the trajectory becomes a plain billiard path, and I need to check whether it can loop forever without reaching the bricks.

I'm checking whether the ball's trajectory, with the paddle always catching it dead-on, could just circle around the grid forever and never reach a brick. The vertical bounce period works out to 18 steps and the horizontal one to 20, so the orbit repeats every 180 steps, and I'm wondering whether that cycle leaves some bricks untouched.

I'm checking whether the orbit covers all cells: the diagonal path over the unfolded torus only reaches half its points, and folding into the 10x9 grid could leave some parity classes of bricks untouched.

I'm checking that every cell gets visited: each cell has preimages in both parity classes on the unfolded torus, so the diagonal orbit reaches all of them, and bricks should eventually get hit, though reflections off bricks and sticky-action deviations will change the path.

I'm checking the claim that the ball can't loop forever: the bounce keeps the ball on a predictable path, and the paddle's catches only shift the timing. Bricks should still get hit eventually, though a brick reflection changes the phase. I'm also confirming that the refill happens only when the ball reaches the bottom row and the brick count hits zero.

I'm defining the down-phase lookup tables now: for each horizontal direction, the landing column is the ball's column shifted by its distance to the bottom row, folded back into the grid. The stall cases at the walls need care, so I'm checking how a ball sitting on column 0 gets classified depending on whether it just arrived or is holding still.

I'm checking the down-left case at column 0: a ball that just arrived there and heads down-left should reach column 7 − y by row 8, and the formula agrees with that when y is below 8. At row 8 itself the ball bounces back onto column 0, so the paddle catches it there and the fold of 0 gives the right target.

I'm checking the bounce cases at the walls: when the ball is on row 0 and stalls, its target is simply its column shifted by 8 in the direction of travel, folded back into the grid. Brick bounces at rows 1 to 4 work the same way, since the ball has already moved horizontally and only the remaining rows to the bottom matter.

I'm working out the up-phase lookup: when the ball is moving up, the landing column is its column plus dx times its height plus three, folded back into the grid. I'm checking that this target stays fixed along the path, and then I'm turning to whether the assumed offset of two still holds when the ball is in the upper rows, where bricks might have been cleared.

I'm now asking whether the up-phase target should use a different assumption for low rows, since the ball may be near the top with bricks possibly still above it. If there's a brick directly above, it would turn the ball right away, which changes the expected landing column compared with assuming a clear run to the top wall.

I'm considering whether the up-phase target should use a constant offset of 3 for rows 4 and up, but for rows 1 to 3 the possible turn points spread out too widely. A midpoint of 9 would hedge between a brick right above and a clear run to the top wall, though that creates a jump at y=3 that I need to check.

I'm weighing how the up-phase target should behave near the top, where a jump of 3 at the boundary between rows 4 and 3 would be awkward. Keeping the offset at y+3 for rows 3 and up would be smoother, and I'm considering a different assumption only for the very top rows, where the ball may be heading toward the wall.

I'm settling the up-phase target for the upper rows: for a ball at row 2 going up, the likely turn is either at the top wall or off a brick on row 1, so I'm taking the midpoint of those two estimates. Row 1 has no brick above it that could turn the ball, so the top-wall case applies there. That leaves the question of how to handle a ball on row 0 that is still heading up.

I'm working out the return-phase targets for the upward movement: from row 0 the ball stalls and then drops back down, which gives a target of 9 columns over, and at row 1 it comes to 10. For rows 2 and 3 the possible turn points spread out, so I'm leaning toward midpoint values of about 8 or 9 there, and for row 4 and above I'm still weighing whether the y+3 assumption holds.

I'm settling the return-phase targets for the upward movement: at row 0 the ball stalls and drops back to a target 9 columns over, and at row 1 it's 10. For rows 2 and 3 I'm taking midpoint values, and I'm checking that the lookup stays roughly smooth as the ball rises.

I'm now checking the return-phase numbers on the upward path: if the ball bounces at row 8 and climbs to a brick at row 4, the round trip adds up to roughly ten columns, which is what the target needs to cover.

I'm tracing the ball's path after a paddle bounce at its start column: it goes up, bounces off a brick in row 3, and comes back down to row 8, which lands it at the mirrored column 9 − x8. That means the paddle has about ten steps to cover the distance |9 − 2x8|.

Checking the upward-phase numbers on the next step: the ball's first step after the bounce at row 8 is a horizontal one, and I'm working out how the target stays at 7 − x8 as it climbs. Then the vertical classification after that bounce comes up next.

I'm checking the corner case where the ball sits at (9,8) after hitting the paddle while moving down-right: it flips to up-left and stays in the same cell, so the trail matches the ball and both differences come out to zero. The horizontal and vertical indicators still read correctly as left and up.

I'm checking the input scaling next: the horizontal indicator's values come out to about 0.5 or 1 in magnitude, so a steepness of 6 to 8 keeps the tanh saturated. I still need to look at the vertical bonus for rows 5 and up.

I'm settling on fixed comparison thresholds: with a scaling factor of 6, the tanh saturates to about 0.995, so the sign of each difference drives a clean result.

I'm now writing out the output layer: the right-move logit is a weighted sum over the direction units, with a scale of C/2 applied to each unit's activation.

I'm settling the output logits now: the right-move score comes from summing the direction units with a scale of C/2, and I'm choosing C = 20 with a bias of 30 so that no match gives about -10 and a single match gives about +10. Only one direction can match at a time, so the right and left outputs stay exclusive, and the no-op, up, down and fire logits stay at zero.

I'm settling the final scale for the output logits at ±15, so the right-move choice is clearly favored when it fires. I'm also noting that stationary no-op behavior is acceptable, and that a sticky repeated move only costs one step that the paddle can correct later.

I'm now setting up the lookup tables for the return-phase targets, laying out the ball's position in each row. The indexing for the ball channel works out to one row of ten values per unit, so I can write each row out directly.

Writing the lookup tables now...

Writing the lookup tables for the down-phase units now...

Filling in the lookup tables row by row, computing the offsets for each unit.

Still filling in the lookup tables, row by row, for the down-right target column across each ball position.

Still filling in the down-left lookup tables, row by row.

Filling in the down-left lookup rows now, mirroring the down-right table.

Still working out the return-phase targets for the upward path, with the ball's bounce from row 0 setting the baseline before I check the row-1 case.

Still working out the upward-path lookup tables, now for the rightward targets from each row.

Still working out the upward-path lookup tables, now computing the leftward targets as the mirror of the rightward ones.

Writing out the upward-path lookup tables now...

Writing the up-phase lookup tables now...

Writing the ball-channel rows of the first-layer weights now...

Still writing the weight tables, one list per unit, and I'm deciding how to write the mirrored left-moving units.

Still writing the weight tables, and I'm working out whether I can scale whole column ranges at once or have to do each unit separately.

Still writing the first-layer weight rows, one list per unit, and I'm settling on 72 lines since copying between columns isn't an option.

Still writing the first-layer weights, and I'm now setting the H unit's ball-channel weights: each column gets its index as weight, with a small bonus at the edges, all scaled by 8.

Still writing the first-layer weights, and I'm switching to per-column lines for the H unit's ball and trail channels, since that's shorter than per-row.

Still writing the weight rows, filling the V unit's ball and trail channels row by row with scaled weights.

Still writing the vertical weights, setting the trail channel to a negative step per row.

Still working out the edge cases: the trail never reaches row 9, and at episode start the ball and its trail coincide, so the direction signals come out as down-right from column 0 and down-left from column 9.

Still writing the layer-2 weights, and I'm setting up the four direction units with their scaled comparisons...

Still writing the layer-2 weights, setting the right and left move units for each direction.

Writing the layer-2 weights now, setting each unit's right or left move to fire only when the direction and sign checks all agree.

Working out the output logits: with a weight of 15 on the direction units and a bias of 45, the right and left scores come out to -15 when nothing matches and +15 when one does. I'm placing those weights on the matching right and left units, and the hidden units beyond the first ten stay at zero.

Still checking the layer-2 saturation margins, and the down-phase target is fixed to the ball's predicted x at row 8.

Checking the wall-stall cases now: from x=8 moving right, the fold gives 9, 9, 8, 7, which lines up with the unfolded positions. The vertical count also holds, since the down-phase assumes a straight descent from each row to row 8 with no stalls in between. The up-phase lookup is consistent too: arriving at row 0 going up, the next step is a horizontal stall, so the return time comes out to 9.

Checking the top-row edge case now: if the ball bounces off a brick from row 0, its vertical direction flips and it heads back down, which my row-0 "down" classification may not capture exactly.

Checking the paddle-bounce case now: after the ball bounces off the paddle, its horizontal direction flips, so the trail still shows the old direction while the ball actually moves the other way. That mismatch could throw off the direction classification right after a paddle hit.

Next I'm checking the paddle-bounce case once more: when the ball hits the paddle, its horizontal direction flips, so my trail-based classification is wrong for one frame, but the error is harmless early in the up-phase. I'm also wondering what happens when the ball reaches row 8 right as it bounces off the paddle.

Checking the episode start now: the ball at (0,3) moving down-right has a target of column 5, so the paddle needs to shift right to 5 and wait there. I'm tracing the ball's path forward from there to confirm it stays reachable.

I'm checking the right and left move signals against the paddle: a target to the right gives a positive pre-activation, so the right unit fires, and a target to the left does the same for the left unit.

Still writing the weight tables, one list per row, starting with the down-right targets for the first two units...

Still writing the weight tables, and now the mirrored left-moving rows for the down-left targets.

Still writing the lookup rows for the up-phase right-moving units, starting with the T9 target row.

Still writing the up-phase lookup rows for the left-moving units, one list per target.

Still writing the first-layer weight indices, now for the ball rows from y=0 through y=4, and checking that the scaling covers each one.

Still writing the first-layer weight indices, now filling the V unit's trail channel row by row with its per-row step values.

Still writing the first-layer weights, now filling the H unit's ball and trail columns with their scaled values and setting the biases for the first eight layer-1 units.

Still writing the weight tables and the edge-case checks, confirming the ball-plus-trail sums at the start and at the bottom row come out right.

Still writing out the edit blocks and wrapping up the design notes.

