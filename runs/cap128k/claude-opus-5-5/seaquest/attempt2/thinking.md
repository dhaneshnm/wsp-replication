I'm sketching a hand-written policy since no tools are available, and I want it simple but workable. Trained MLP agents on MinAtar Seaquest only reach a modest score, so a basic approach that shoots enemies from a fixed row could be enough. The catch is oxygen: it runs out after about 200 steps, and surfacing without a rescued diver ends the episode, so the plan has to account for that.

I'm settling on a simple shooter: sit in one row, face a direction, and keep firing. The problem is that enemies only show up in my row about one time in eight, so that alone gives a low score. Shifting rows to line up with enemies and dodging them would do better, and rescuing divers to extend the oxygen is worth the extra complexity.

I'm weighing whether a 32-unit first layer and a 32-unit second layer can handle this, and the real obstacle is that "enemy in my row" depends on the player's position, which is a conjunction a linear unit can't express. I could approximate it with a per-row unit that fires only when both the player and an enemy sit in that row, but that costs roughly one unit per row, which eats most of the budget. Comparing enemy rows against the player's row for "above or below" is harder still, so a simpler design might be better.

I'm working out how to detect enemies above and below the player with tanh units, one unit per candidate player row that also checks for enemies in the rows beyond it. That gives about sixteen units for the two directions, which fits the budget and lets the second layer sum them into a single up-or-down signal.

I'm weighing whether to position the sub at a screen edge facing inward, since enemies travel horizontally and spawn at the edges, though spawning right at the edge could put enemies on top of the sub.

I'm now looking at how fast enemies and bullets move, and whether our own shots can keep up with the enemy fire pattern.

I'm checking the bullet collision logic next: a shot hits an enemy when they land on the same cell, and since enemies move slowly, that works out. I also note that the sub only collides with enemies at its front cell, while the back cell is purely visual. Next I want to test a middle-column turret that can turn to face either direction.

I'm weighing a simple high-score approach against collecting divers and surfacing, since the latter adds time but is complex. My sense of typical MinAtar Seaquest scores is that a decent chase policy might land around 5 to 8 points within the 200-step limit.

I'm checking how the diver gauge sits in the same channel as the oxygen bar, since the two overlap. When oxygen is low, the bar stays in the leftmost columns, so the rightmost cell of the gauge can show a diver count without much ambiguity. Above about 180 oxygen the bar reaches that cell, so the reading breaks down there.

I'm checking when it's safe to surface: if oxygen is low and the diver gauge shows at least one diver, heading up makes sense, but going up with no diver just ends the episode. I'm also noting that staying in the top row is safe while oxygen lasts.

I'm noting that at row 0 the oxygen never drops and enemies never appear there, so the top row is a safe spot. Dipping down and coming back up without a diver would end the episode, though.

I'm now weighing a diver-collecting approach, since picking up divers extends the oxygen and makes each surfacing more valuable. Still, the added complexity may not be worth it given how the difficulty ramps after each surfacing, so I'm leaning toward keeping the policy simple.

I'm now breaking the plan into four parts: chase enemies by moving into their row and firing, steer clear of enemy paths and bullets, treat divers as safe targets since they're in the reward channel, and surface only once oxygen runs low with at least one diver aboard. The hard piece is getting the sub to move vertically toward targets, which means handling each player row with its own bilinear unit within the 32-unit budget.

I'm trying to fold the row-above and row-below checks into one unit each, weighting the target rows against the player's row, rather than spending a unit per row pair.

I'm trying to express "any target above the player's row" with one linear unit, where each row's weight would have to depend on the player's row, which a single unit can't do. A steeply decaying weighting per target row might let the top rows dominate the sum, so the threshold only trips when a target sits above.

I'm weighing how to scale the weights so the topmost target dominates the sum, using a base around 6 to keep the values within a workable range.

I'm thinking about whether a single unit can capture "nearest target above," since a plain sum just counts everything. One option is a per-row unit gated by the player's row, which would be cleaner but costs too many units. I'm now considering whether the enemy positions can be encoded so that the player's row acts as a switch between up and down signals.

I'm considering a gated version: one unit per player row, active only when the sub is in that row, with its sign showing whether a target lies above or below. That would take about sixteen units in total, leaving the rest of the budget for facing and firing.

I'm weighing a restricted vertical range, with the sub staying in a middle column and moving only up and down toward targets while facing them to fire. Turning would mean shifting columns, so I'd alternate between two central columns instead.

I'm now checking how enemy subs threaten the sub: they fire bullets along their row toward me, and since bullets move one cell per step, a sub facing me in the same row is a real danger unless I shoot it first or leave that row.

I'm working out how an enemy sub's shots would reach me: it fires about every 11 steps, and its bullets take roughly four steps to cross the middle columns. If I'm lined up and facing it, my own shots should kill it first, though moving vertically into a row with a bullet or enemy right beside me is the main risk.

I'm weighing the danger of moving vertically: stepping into a row with an enemy or bullet right at my column means instant death, and the threat also spans nearby columns. Checking the cells above and below would bring the bilinear dependency back, so I'm considering fixing my column to simplify that check.

I'm settling on a fixed column for the sub so the vertical danger check depends only on its row, which keeps the per-row units manageable.

I'm trying a different encoding: indexing hidden units by target row, or using an exponentially weighted sum so that a target above the player's row pushes the sign one way, though the player-row term still makes it bilinear.

I'm checking whether one exponentially weighted sum can separate "a target lies above the player's row" from "all targets lie at or below it," using per-row weights with a base of 7 so the largest weight stays under the limit. It only works if there are few enough targets per row, so I'm weighing how many could appear at once.

I'm weighing a plan that handles each target row with its own unit, since a single unit can't check "nearest above" against the player's row. Another option is checking only the rows just above and below the sub, which would be more readable even if it's less general.

I'm weighing a simple vertical patrol between rows, but every move up or down adds collision risk. I'm also estimating what a reasonable RL baseline might score on Seaquest, based on what I recall of the MinAtar results.

I'm laying out a per-row design: for each player row, one unit that fires when the sub is in that row and a weighted count of nearby targets above and below pushes the sign toward up or down. Units for rows the sub isn't in get pushed far negative by the gating term, so they stay quiet.

I'm checking whether the sub's position can ever be off the grid when it faces left at the right edge, since the back cell would then fall outside the board. Pressing right from column 9 keeps it facing right, so that case seems to come up only if the start or a left move leaves it facing left at column 9.

I'm settling the gating term for each player row so the target contribution stays active only when the sub sits in that row. With the sub's two cells always in the same row, a large weight on the row indicator keeps the unit quiet otherwise and lets the target sum decide the sign when it's active.

I'm going with one unit per player row, gated so it's only active when the sub sits in that row, with its sign giving the up-or-down preference. When the sub is elsewhere, the gate pushes that unit to a steady negative value, and the other rows' bias terms can cancel it out, so only the active row's unit matters.

I'm settling the vertical drive as a sum over eight per-row units, where an inactive row saturates to about -1 and the total comes out to -1 when the sub sits in row 0, so it always heads down from there.

I'm now deciding how a single signed unit per row can also express "stay put" when a target sits in my own row. The sum of same-row targets doesn't fit cleanly into that signed output, so I'm considering distance-weighted pulls where the nearest target dominates, plus a separate unit for holding position. I also need to keep in mind the danger of moving up into a row where a bullet or enemy is close.

I'm checking whether danger in the row above should be folded into the same signed unit, since a hazard there only matters if I move up into it. Pushing the unit negative for danger above would bias me downward, but if danger sits below as well, those contributions would cancel out.

I'm checking whether an enemy sub in my own row is a threat, since its bullets travel toward me at one cell per step. Facing it and firing should kill fish before they close in, but the sub's earlier shots could still reach me, so I'm weighing how its firing timing affects that.

I'm working out a separate dodge mechanism for enemy bullets already in my row, since the signed per-row unit can't express "leave" without a direction, and I'm counting how many units that would take.

I'm working out how to read facing direction from the observation, since the back cell appears in the trail channel. I'm also counting the units for each row's facing signal so I know the total stays manageable.

I'm checking whether I can tell which way the sub faces by using its column position, since the trail channel also picks up enemy trails and makes a direct read unreliable. If I'm at columns 4 and 5 facing left, pressing right should flip it to face right, so the column occupancy would show the change.

I'm checking whether the trail channel can tell me my facing direction in general, not just per row. Comparing trail cells at columns 4 and 5 across all rows would be simpler, but enemy trails crossing those columns in other rows could throw the reading off.

I'm weighing a firing approach that doesn't depend on a fixed column. Letting the sub drift changes which columns matter, so a per-row orientation unit based on trail cells at columns 4 and 5 would break once it moves.

I'm trying to get the sub's facing direction without relying on a fixed column, since the sub can drift. One idea is a per-row unit that compares where a target sits against the player's column, which would tell me whether it's to the right or the left. The difficulty is that this comparison is bilinear in the column positions, so a plain weighted sum doesn't express it cleanly.

I'm working through the facing signal for each row, where the gated unit should lean one way or the other depending on whether targets sit to the left or right of the sub. The offset has to be arranged so that a row with no targets still gives a sensible value, and I'm weighing whether per-cell weights can handle that without a separate existence check.

I'm reconsidering the overall action choice now: if a target is in my row, I face it and fire, otherwise I move vertically toward the nearest target while avoiding danger, and I go up when oxygen runs low. I'm also wondering whether the sub should stay near the centre, since turning toward a target shifts it by one column, and it may drift back and forth around a single column.

I'm weighing whether to add a weak centering pull toward the middle columns, since being at the edge is risky when enemies spawn at column 0 or 9. It would only apply when there's no target in my row, but that adds complexity. Drift may be acceptable. I'm also starting to think about diver pickup, treating divers like targets so the vertical drive chases them and the facing signal lines up with them.

I'm noting that divers only get picked up when they walk into my front cell, so staying in a row with an approaching diver is what collects it. That makes the vertical drive toward diver rows work, as long as I remain there until the diver reaches me.

I'm separating divers from enemies by subtracting the danger channel from the reward channel, since bullets only show up in danger. For the vertical drive, I'll treat the reward sums in other rows as attraction, weighted by how far away they are.

I'm noting that enemies already moving away still count, so chasing them would be wasteful, though bullets reach them fast enough that shooting them is still fine. For rows where a target sits in my own row, I want the vertical drive to stop, so I'm leaning on the fire and turn outputs to win out over the up and down logits when a target is directly in line.

I'm working on the horizontal part now: a per-row unit that should point toward a target in that row, with its sign set by which side of the player it sits on. Expressing "target to the right of my front cell" as a linear function is awkward because it depends on both positions, so I'm trying to fold the player's column into the weights.

I'm settling on a centering effect here: with no target in my row, the horizontal signal reduces to a pull back toward the middle columns, and with one target it gives the signed distance to that target. The trouble is that with two targets on the same side the sum no longer matches the distance cleanly, so I'm checking how that case behaves.

I'm checking the player term: with the front at column f and the back one column away, the centred sum comes to roughly -(f-4.5) plus or minus a half, so the facing offset only nudges the result slightly.

Now I'm checking the orientation signal: summing the column positions of the player's cells gives the front plus the back, and the trail channel at the back cell can help separate which one is which, as long as no enemy trails cross that row.

I'm stuck on the orientation reading: the trail channel is ambiguous because an enemy in the same row leaves its own trail next to it, which would corrupt any column-weighted estimate of which cell is the front. Since I have no memory between steps, I can't use history to resolve it either, so I'm considering whether I can avoid needing orientation at all.

I'm weighing whether per-column weights could capture the sub's facing direction on the board as a whole, rather than relying on a single row. Shooting the wrong way wastes the five-step cooldown, though, so I'm settling on a mixed policy where the right and fire outputs both rise when a target is to the side.

I'm checking whether the orientation can be read per row, since enemy trails in the same row would otherwise throw off a column-weighted estimate of which cell is the front.

I'm checking whether the orientation can be read from the row itself: a unit that adds the player's column weights and subtracts twice the trail weights would give the front-minus-back difference, but any enemy trail in that row would corrupt it. My idea is to cancel that contamination by also subtracting the reward channel, since an enemy's trail sits one cell off the enemy's own column, with the sign depending on its direction of travel.

I'm checking how the orientation signal behaves when enemies share the row: the enemy contribution shows up as a ±2γ term tied to their direction of travel, which is about the same size as the facing signal itself.

I'm looking at whether a unit could read the sub's orientation from its row, but enemy trails in that row would throw the estimate off. Since the trail sits next to the enemy and the sign depends on its direction, I'm wondering whether a local check next to the player would be less affected.

I'm now looking at a per-row approach that would handle orientation inside the second layer, but that layer only gets tanh features from the first, so the row structure has to be settled earlier. Since orientation reads are thrown off by enemy trails, I'm considering a simpler firing rule: shoot whenever a target is in my row and press toward it sometimes, accepting that cooldown will swallow some shots.

I'm weighing a simpler route: skip explicit orientation and instead fire and press toward a target whenever one shares my row. A wrong-facing fire press only costs cooldown when the timer is already zero, and turning toward the target still closes the gap, so over a few steps the mix should still land kills.

I'm weighing a rule to press toward a target only when it's far enough away, since moving into an adjacent enemy means a collision, while a bullet fired at an adjacent target still hits.

I'm now considering a per-row orientation reading that uses the trail and reward channels together, but the enemy trails keep contaminating it. A more promising direction is an AND across the whole board: a cell where both the player and trail channels are active marks the sub's back, though that still needs per-cell logic. For firing, the magnitude of the row signal should track distance, and I'd derive it from two threshold units.

I'm checking a version where the orientation sum also picks up the reward channel, but an enemy that has just spawned, with its trail off the grid, would still add a large term, so that doesn't work either.

I'm weighing a simpler rule that skips the orientation question altogether: when the target is far away, lean toward it and fire, and when it's close, just fire, since pressing toward an adjacent enemy would mean a collision.

I'm checking whether a danger test can stop the sub from moving into a row where an enemy sits within a column or two of it. The column comparisons are not linear, so that part is harder to express than the simple distance check.

I'm considering holding the sub's cells fixed at columns 4 and 5: turning left or right then just swaps which cell is front, so the position stays put, and only pressing further in one direction drifts it.

I'm fixing the sub's columns at 4 and 5, so the orientation can be read per row from which of those two columns carries the enemy trail. For each row I'd get an orientation unit and a target-side unit, which makes 24 units across rows, plus a few more for oxygen and divers. The second layer would then need to AND the side and orientation signals together to decide when to fire.

I'm considering whether a single per-row unit could merge the target-side and facing signals, so the second layer only has to decide between firing and turning.

I'm working out a per-row unit that gates on whether the sub is in that row, so it can say "target to the right while I face left" and trigger a right press. A second unit would cover the opposite case. Firing would then be the default whenever a target shares the row and neither turn unit is active, though that means one more indicator per row for target presence, and I'm still deciding how to gate it cleanly.

I'm writing the unit's pre-activation as a gated sum: the player-in-row gate and the target-right count feed in positively, the facing-left check adds positively, and the facing-right trail at column 4 is subtracted so two targets can't fake a turn.

I'm trying to cut down the unit count: right now each row needs turn-right, turn-left, vertical, and target-presence units, which adds up to 32. One idea is to fold the fire decision into the turn units with a stronger weight, so the target-presence signal only has to be read once per row.

I'm weighing whether a per-row unit that flags a target to the right while I face left could handle the turn decision, with a separate unit for the opposite case. The open question is where the "target in my row" signal for firing should come from, since adding one more unit per row would push the count past what I can spare for oxygen and divers.

I'm now weighing whether the orientation can be read globally, summing the trail difference across all rows, but enemy trails passing through columns 4 and 5 would contaminate that sum often enough to make it unreliable.

I'm trying to cut the unit count by combining the horizontal and orientation signals into one per-row unit, but a product of the two isn't linear, so I'm looking at encoding both in a single scaled sum and decoding it with thresholds in the second layer.

I'm trying a single signed value per row, x = 3·D + O, where D is the target's side and O is the facing direction. Its four non-zero combinations separate cleanly: fire when both agree, turn right or left when they don't. A second-layer threshold on the summed units could then pick out each of those cases.

I'm checking whether the count of targets on each side breaks the scheme: with two targets to the right, the sum would land on a different level than with one, so the thresholds need to hold across those cases too.

I'm checking how the sum behaves when the player is in row 0: every gate is off, so the reading lands at the "fire left" level, which is harmless for a bullet but means "go down" has to win through a separate term. The bigger problem is rows with two or more targets on the same side, since the count pushes the sum to a different level and the thresholds would misread it, so I'm looking at whether the target weights can taper with distance to keep that from happening.

I'm trying to keep the count down by encoding orientation with a large weight and the target side with a smaller one, so each row's output decodes into fire or turn based on where it falls against a few thresholds.

I'm setting the four threshold units at ±b ± a/2 so they split the single sum into fire-right, turn-left, turn-right, and fire-left regions, plus a fifth unit at zero. The open issue is that tanh compresses the values, so the layer-one scale has to keep those regions separable even when up to three targets share a row.

I'm checking the precision margins now: the inactive units need a large gate so they sit at -1, and with a gate of about 5 the leftover term stays small enough to keep the readout clean.

I'm settling the divers in the same row: the target count D stays limited to columns 6 and up, and the far side at 3 and below, so the back-cell trail at 4 and 5 never gets counted.

Now I'm weighing whether divers should count toward the target total for a row, since a diver drifting away would keep the sub facing it for many steps. I'm considering switching to the danger channel, though enemy bullets complicate that choice too, so the counting rule is still unsettled.

I'm weighing whether enemies alone should drive the fire decision, since divers and bullets in the same row would otherwise trigger it too. One way to do that is to weight each cell by type, so a single enemy adds more than a diver or bullet, and then set the thresholds between those levels.

I'm working out how to handle danger in my own row: an enemy sub there fires bullets at me, so the vertical unit may need to push me up or down toward a safer row, but a single signed unit can only push one way.

I'm checking how a bullet already on its way toward my row could reach me before I can turn and fire, so I'm treating an incoming enemy shot as a reason to dodge vertically rather than answer it.

I'm checking the danger in row k-1 and k+1 at columns 3 through 6 before deciding whether to dodge vertically, since an enemy or bullet landing on the front cell is lethal while the back cell is safe.

I'm thinking about dodging bullets in my own row, since they're the main lethal threat there. Enemy subs fire along their direction of travel, so a bullet can reach my front cell before I can turn and shoot back. The unresolved part is which vertical direction to move in, because a single signed push can't express "get out either way."

I'm now trying to fold the dodge logic into the vertical unit itself, adding a term for bullets in my own row, though the sign of that push is still undecided. Giving each row its own danger gate would mean roughly eight more units, which leaves a handful for the oxygen and diver logic.

I'm weighing how the vertical unit should handle danger in my own row: any push up or down can only be applied in one direction, so the sign has to be picked from whichever adjacent row looks safer. I'm also checking whether the vertical push can override the fire decision when a bullet is closing in, since a dodge that loses to the target logic would still leave me dead.

I'm working out how attraction from other rows should combine into the vertical push, keeping it weaker than a dodge so it doesn't override the target logic. The plan is to weight nearer rows more heavily than distant ones, and I'm starting to settle on the first weight.

I'm settling how the vertical push from other rows should be weighted, so that nearer rows count for more than distant ones. The idea is that each row's target count pulls the sub toward it, with the nearest rows giving the strongest pull and the pull fading with distance. I also want the target count in each row to include divers, since a diver drifting away would otherwise be ignored. With row 0 all gates are off, so the sum sits at its lowest level, and that reading should be treated as a strong pull downward, the same as a dodge.

I'm working out the oxygen-surfacing rule now: when oxygen runs low and I'm carrying a rescued diver, the vertical push should go up strongly, overriding everything except an imminent danger. I'd check the intermediate rows for danger on the way up, and read the low oxygen off the gauge bar.

I'm working out the oxygen check: the gauge's bottom row only lights up at column 2 once there are at least three oxygen cells, so reading that cell tells me when oxygen is low. I'm combining that with the diver indicator at the far end of the bar to build a surfacing unit that pushes upward when I'm carrying a rescued diver and air is running out.

I'm now deciding that surfacing should also trigger when all six divers are on board, since the bonus scales with remaining oxygen and the six-diver count is unlikely to be topped up anyway. The idea is to read that state from the gauge's diver segment, which would fill to column 3 at six divers, and surface immediately when it does.

I'm checking whether the oxygen gauge can tell me when divers reach six, but when oxygen is at least four cells the bar fills the same way whatever the diver count, so the count is unreadable. It only shows up cleanly when oxygen is nearly gone, so a bonus-driven surfacing rule won't be reliable.

I'm weighing whether surfacing should trigger at a higher oxygen level, say when oxygen is below four cells and I'm carrying at least one diver, since each surfacing trades a diver for points and more surfacing could make the difficulty ramp faster.

I'm now checking whether surfacing should be a separate signal in the second layer rather than part of the vertical unit, since a danger-above veto would get mixed into the attraction sum and be hard to separate out.

I'm now worried that danger in the row above shouldn't be treated the same as danger below, since pressing down to escape an upward threat could walk me into a bullet from below. Folding both into one signed value means the sign can end up wrong, so I'm considering keeping the above-danger out of the down push entirely.

I'm splitting the danger handling out of the attraction sum: a separate per-row unit for dodging and vetoing, so that danger above only blocks moving up rather than pushing me down into something below. That leaves the attraction unit to deal only with targets, and I'm counting roughly 24 units for the per-row pieces, with a handful left over for the surfacing signal.

I'm putting the danger checks into a separate safety unit, where a bullet below pushes up and a bullet above pushes down. I'm still deciding where the own-row dodge should live, since it doesn't fit cleanly with the attraction sum.

I'm now considering how the own-row dodge should combine with the veto: if the dodge pushes up but the row above is unsafe, the sign should flip toward down, so I'd need a second-layer unit that reads both the dodge and the unsafe-up flag together.

I'm working out how the own-row dodge fits with the veto, since the attraction and dodge both feed into the same vertical sum and a dodge needs to be stronger than a target pull. I'm considering whether a second-layer unit that reads the sum together with the safety signal could decide the direction when a dodge and an unsafe side collide.

I'm now weighing how an enemy bullet already in flight should affect moving into a row: a bullet well to the side could still reach me within a few steps, and I can't see its direction from the screen alone, so I'm thinking about whether to veto entry into any row with a bullet on it.

I'm treating enemy bullets in a row as making that row unsafe to enter, at least anywhere in the middle columns, since a bullet's direction isn't visible from one frame. The plan is to weight the danger and reward channels linearly: bullets count as danger only, divers as reward only, and enemies as both.

I'm settling the weights so that bullets count as danger only, divers as reward only, and enemies as both. Near-column enemies and any bullet should make a row unsafe, while far-column enemies stay as targets.

I'm deciding how own-row bullets should be handled: a bullet in my row at the outer columns means I should leave the row. That's the main risk once I've entered a row with an enemy sub, since its shots arrive quickly.

I'm weighing how to fold the own-row dodge into the per-row units, since a bullet already in my row needs a stronger push than any attraction. Mixing it into the same signal as the target pull looks awkward, so I'm trying to see whether it can ride along in one of the existing per-row channels.

I'm settling the vertical logic so that each row's attraction and safety terms combine into one push, with the safety vetoes flipping the sign when a direction is unsafe. Then a separate per-row unit would handle an own-row bullet, and the bias toward middle rows has to be strong enough that row 1 never drifts up into the surface.

I'm checking the row-1 bias: it needs to be moderate so that a surfacing signal can override it, while danger vetoes in other rows stay strong enough to block moves into them.

I'm making sure row 1 gets a negative bias so the dodge always pushes down, since attraction can never pull upward from there. Surfacing can then add an upward push in the second layer, but only when there's at least one diver aboard.

I'm checking the row-1 case now: with no divers aboard, any up press from there would surface and end the episode. Since sampled actions can still pick up with some probability, I need the up logit in row 1 to be very low when there are no divers. The sticky-action repeat is the trickier part, because a move up from row 2 could carry over into another up press.

I'm weighing whether row 2 should carry the no-divers guard, since a sticky repeat of an up press from row 1 would send me into the surface. Adding a gauge input directly to the row-2 up logit could block that, so I'm sketching how it would look.

I'm checking whether a diver-count test can use the oxygen gauge, since a full gauge at the start looks the same as a diver aboard. I'm considering whether a middle reading of the gauge, such as cell 5 being off, could separate the two cases.

I'm checking whether the count of divers aboard can be read from the oxygen gauge, since a full gauge looks the same as having divers. One idea is to use the top gauge cell as a diver signal, but a full gauge early on makes that ambiguous, so I'm testing whether a middle cell being off can tell the two cases apart.

I'm making row 1 off-limits unless I'm surfacing, since a stray up press there with no divers aboard would end the episode. I'm checking whether the gauge can tell me if a diver is aboard, but a gap in the cells doesn't reliably separate the cases.

I'm checking whether the shield signal can stay active when oxygen refills after surfacing, since at that point the sign should flip back toward down.

Now I'm checking the sticky-action risk: a repeated up press from row 3 could carry me into row 1, and a second repeat would push me into the surface, so I'm working out how often that chain could actually happen.

I'm laying out the layer-1 units now: eight horizontal units for orientation and enemy side, eight vertical units for attraction and safety, eight own-row threat units, and one surfacing unit.

I'm weighing whether the own-row threat should get its own unit, or whether it can be folded into the vertical channel. Enemies right beside me matter too: if I'm facing one and my cooldown is ready I can shoot it at once, and turning and firing takes only about two steps, so those are usually manageable. I'm also noting that a bullet moving away from me might make me leave a row needlessly, which I can accept.

I'm working out the dodge term for the vertical units: it adds a push toward the safer side when a bullet is in my row, and the danger vetoes can flip that sign if the chosen direction is unsafe.

I'm settling that vetoes should only block a move rather than push against it, since a push would drag me out of a row where I'm shooting. So the danger signals just gate "up allowed" in the second layer, and I'm using three magnitude levels: weak for attraction, medium for vetoes, and stronger for the dodge.

I'm weighing whether to split the safety signal into its own units, separate from the vertical attraction, so the two don't blur together at the thresholds. The idea is to keep the dodge with the safety term rather than mixing it into the attraction, which should give a cleaner result.

I'm weighing whether the dodge should live in the same signed unit as the safety vetoes, since that would let one value say which way to move. The trouble is that the dodge has urgency while the veto only has direction, so I'd need to keep them separate. I'm also wondering whether a single global bullet signal, summed across rows and gated by my current row, could drive the dodge without a unit per row.

I'm weighing whether the dodge could go into the spare units, since rows 2 through 8 would each need their own, and row 1 can skip it because I'm only there while surfacing.

I'm now checking the unit count against the budget: with horizontal units for rows 2 through 8 and the vertical ones in the same range, I can drop the row-1 horizontal unit and still fit. For row 1 I'll skip the vertical unit too, since being there only matters while surfacing, so the readout there should just read strongly down.

I'm checking the row-0 and row-1 readouts for the vertical units: with the row-1 unit dropped, being in row 1 should read as strongly down. The worry is the X units: if row 1 reads as "up unsafe," a surfacing move from row 1 would be blocked, so I need to flip the polarity so that a down-unsafe reading covers those rows instead.

I'm working out how the gate should behave when a row is inactive: if the gate pre-activation is strongly negative for inactive rows, those units output -1, and I'm considering whether flipping the offset would make them output +1 instead so the readouts line up.

I'm now checking the polarity of the readouts: with inactive units set to +1, the row-0 and row-1 readouts come out as "down unsafe," which would block moving down from row 0. So I need to flip that convention so the inactive case leaves the harmless direction open.

I'm stuck on the inactive-value problem: if inactive units all sit at one value, the readout for whichever row is active gets shifted by that value. Balancing +1 and -1 across units doesn't fix it either, since the offset then depends on which row is active. So I'm considering giving the X units separate, unsigned veto signals instead.

I'm trying to set the vetoes inside the V units themselves: keep attraction small, push the safety signal to larger magnitudes, and read "up unsafe" from the extremes.

I'm checking whether the veto can be encoded in the magnitude of V: a strong negative value would block up without pushing, and a strong positive one would block down. The catch is that a strong veto also cancels attraction, so when I want to go up while down is unsafe, the sum lands near zero and I lose the up preference.

I'm now testing whether a single V unit can carry both the attraction and the down-unsafe veto through its magnitude: a small attraction stays under the threshold, while a large veto pushes the value far enough to block the move without driving it the other way. I'm checking the numbers, and the one case I can't cover is attraction toward up when down is unsafe, which just leaves the agent neutral.

I'm checking whether the attraction weights stay small enough that a few targets together won't push the sum past the veto threshold. The numbers look fine at around 1.1 total, so I can keep the veto large enough to still work. Then I'll come back to the dodge question.

I'm working out how the dodge fits into the second layer, using a separate signal for the bullet threat. The idea is to pick a dodge direction from the vertical unit's veto state: move down if up is blocked, up if down is blocked, and otherwise follow the attraction sign.

I'm reconsidering whether the dodge can be a signed value like the vertical units, with its direction chosen by row. But a signed version would need a bullet-presence threshold, and that only gives an unsigned flag. So I'll keep the dodge flag unsigned and let the second layer choose the direction from the vertical veto state.

I'm settling on a dodge signal that is unsigned, with the direction picked in the second layer from where the vertical veto sits: if the value sits above -0.3 the dodge goes up, and below that it goes down. I still need to check whether moving down is actually safe in the range between -0.8 and -0.3.

Next I'm checking whether dodging up from row 2 could strand the agent in row 1, but since the row-2 vertical unit leans down, that case mostly takes care of itself.

I'm tracing the row-1 case now: with no V unit active there, the readout reads -1, which my encoding treats as "up vetoed", so the agent would sit still instead of moving down. I need to fix that so row 1 doesn't stall.

I'm now working out the unit budget again: dropping the row-1 horizontal unit leaves room for a separate row 0/1 detector that pushes strongly down. Since horizontal units only matter for rows 2 through 8, the readout for rows 0 and 1 will need to be handled explicitly rather than falling out of the inactive value.

Now I'm weighing the inactive output of the horizontal units. Both extremes read as "fire" in this encoding, so I'll rely on a separate row 0/1 unit to push strongly down and beat the firing signal.

I'm worried the orientation check could flip when the sub is pushed one column off center, since a sticky left press would make the back cell read as facing right. So I'm working on an orientation reading that stays correct even when the sub drifts, and checking how weighting the columns across a row could keep it from looping toward the wall.

I'm checking whether a weighted sum over each row can recover the sub's facing direction without being thrown off by enemy trails in the same row. Using a back-cell weight that cancels out the front position gives an exact sign for the sub, but any targets sharing that row add their own offsets, which could swamp the signal.

I'm checking whether a position-and-orientation decoder can work from the trail counts in a row, since the simple difference breaks once the sub drifts a column off center.

I'm working on whether a linear weighting over each row can recover the sub's position and facing at once. The idea is that one weighted term gives the offset between the front and back cells, and a second term tracks where the targets sit relative to the front, so the turn decision comes from a single combined value.

I'm now weighing a separate orientation signal for each row, which would mean two units per row, but the trail contributions from enemies in the same row make that linear weighting unreliable. I'm leaning toward keeping the sub centered and using a window-based reading of its facing instead.

I'm now going through the sub's possible positions near the center, both facing left and right, including the cases where a sticky repeat has drifted it one or two columns off. I want an orientation readout that holds across all of those cases, and a window of columns 3 through 6 should cover the sub without being pulled off by stray trails.

I'm checking each case against the target side: if the sub faces the target, it fires, and if not, it presses toward the target to turn. Pressing right from the drifted-left cases moves it toward center, and the same logic handles the rest, with recentering when no target is in the row.

I'm working out how to recenter the sub from drifted positions: from the left-drift case it takes two presses right to get back to a centered right-facing sub, and from the right-drift case it takes two presses left. I'm now checking whether a linear weighting over a window of columns can give the sign of front minus back, but enemy trails inside that window could throw the readout off.

I'm checking how enemies moving left leave trails that fall inside the orientation window, so a close enemy could skew the readout. The contamination from those trails is large, which could push the firing decision the wrong way when an enemy is nearby.

I'm narrowing the orientation window to columns 3 through 6, since that covers all the centered and drifted positions I care about. Enemies approaching from either side leave their trails outside that window, so the readout should only pick up contamination from enemies that have already passed.

I'm checking whether enemy trails near the back cell could skew the readout when an enemy approaches from behind. Turning right from that case would bring the sub to a drifted right-facing position, and a tight enemy timing could still cause a collision. I'll keep this as a rare edge case and use a weighted position term on the window of cells 3 through 6.

I'm now laying out a two-unit budget per row for horizontal control: one unit for orientation and one for the target side, with the centering bias folded in when no target is present.

I'm settling the horizontal decision table now: fire when the target side and the orientation agree, otherwise turn toward the target, and recenter when nothing is in the row. Four AND units, FR, TR, FL and TL, will give the fire, right and left logits.

I'm defining the drive signal as a tanh of target counts minus a small position penalty, so an empty row still gives a weak signal that nudges the sub back toward center. Strong values will mark a real target, and weak values will mean recentering, with the sign still deciding which way to turn. I'm also thinking about treating an enemy as the overlap of the target channel and the right channel.

I'm weighting each target by its distance from the sub's center, so a target at column 9 counts for more than one at column 6. The question is whether that offset from center can stand in for a plain left-or-right sign once the sub has drifted off center.

I'm weighting each P cell by its offset from the center column, so the player's position contributes a term proportional to how far the sub sits from center. With an enemy at column t, the combined sum should come out to something like 2w(t − center), and the recentering push from an empty row then depends only on the drift.

I'm checking whether a drift of two columns would make the recentering push look like a real target, since the two magnitudes overlap. If it does, the decision thresholds on the drive signal would fire or turn when the sub should just move back to center.

I'm checking the drift case numerically: with the player weighted by distance from center, a sub two columns off center gives a recentering push of about 2w, while a single enemy contributes 2w(t − center), so the magnitudes can overlap. I'm now trying to scale the position term separately so recentering stays distinct from target signals.

I'm checking the recentering moves from each drifted position: the sub presses toward center whichever way it faces, and it lands centered after one or two presses. I'm also noting that if a target shows up in the row while recentering, the target signal should take priority.

Now I'm checking whether the target signal, the fire decision and the vertical moves all still fit within the per-row budget. I'll keep the fire behavior as is, since the sub can stay put in the row until the target is gone.

I'm settling how many horizontal and vertical units each row gets, with two spare slots left over. I'm also checking that the row-8 bottom case stays within the sub's vertical range, and that no separate row-1 unit is needed beyond surfacing.

I'm working out the gating for each row: a player cell's weight in row k is set so that when the sub is in that row the two player cells cancel out, and when it isn't there's a large negative bias. With a gate of 4, the inactive rows get pushed to about -8, so the content terms only shift a strongly saturated value that stays firmly off.

I'm working out how the inactive rows get suppressed: with gate G=5 their pre-activations sit near -10, so the content terms from other inputs can't flip them. That leaves the readout summing to about -6 plus the active row's value, and in rows 0 and 1 everything stays off, giving a readout near -1 that the decoding layer can read as a no-op for fire, up, and dodge.

Now I'm writing out the vertical unit for each row, which pulls toward any target in other rows with a strength that falls off with distance.

I'm now setting the vertical attraction for each row: targets in other rows pull the sub toward them, with the pull weakening as the distance grows, and divers count while bullets don't. I'm also adding a veto so the sub won't move up into a row where danger sits in the middle columns.

I'm checking whether bullets in the row above could be told apart from divers with one weighted unit, since both sit in other channels. A diver far off would push the vertical signal up and wrongly block the move, so a single linear weight won't separate them cleanly.

I'm weighing whether to veto far-away bullets in the row above, but a single weight can't tell bullets, enemies and divers apart: vetoing bullets would wrongly block the sub from moving toward far enemies or divers. So I'm leaning toward not vetoing far cells, and only watching the middle columns near the sub.

I'm widening the veto window for adjacent rows to columns 2 through 7, since a bullet at column 2 or 7 can reach the sub's column in a step or two. Entering a row at that distance leaves room for a dodge, so I'm weighing whether the wider window blocks too many useful vertical moves.

I'm checking the veto window for the adjacent rows: columns 3 through 6 get a strong negative weight, and columns 2 and 7 get a slightly weaker one, enough to still block the move. I'm also wondering whether attraction from a target in that vetoed row should be cancelled out, but that's where I stop for now.

I'm setting the veto thresholds for the adjacent rows: cells in columns 3 through 6 get a strong negative weight, and columns 2 and 7 a somewhat weaker one, with extra margin so that other targets pulling the same way can't push a veto below the cutoff. The same logic applies in reverse for the row below, with the signs flipped.

I'm checking the upward veto at the top row, where row 1 is ignored, and noting that the sub can't move down past row 8. For row 2, the attraction term is zero, so the bias of -0.3 is what matters, and it nudges the sub slightly downward unless a danger above vetoes that.

I'm correcting the row-2 bias from -0.3 to -0.5, since at -0.3 the dodge decode would wrongly read "up." With -0.5 the dodge points down as intended. I'm also noting that the surfacing override pushes the up logit high, but it has to yield to the up-veto when the veto is active.

I'm now deciding how the row-1 and row-0 cases get handled, since the vertical veto would otherwise leave the sub stuck in row 1 during surfacing. The plan is a separate unit that detects the top two rows so surfacing and the down-move still work there.

I'm laying out the layer-2 units now: one that fires for the top two rows when surfacing is active and pushes up, and one that pushes down there when it isn't. For the lower rows, I'm checking whether the surfacing signal can go up without hitting the veto.

I'm laying out the layer-2 threshold units now, comparing the summed up-desire and down-veto readouts against fixed cutoffs.

I'm laying out the recentering unit for the right side, so it fires whenever the diver signal is far enough to the right, and checking whether it would fight the fire logit when firing is already active.

I'm working out the decoding layer now: the right-moving logit gets a positive term from the recenter unit and a negative term from the fire and turn-right units, so it doesn't pull the sub toward a target it's already facing. Each of these 0/1 units can be built from the ±1 tanh outputs by a simple shift, with constants folded into the bias. Then I'll set the dodge units, which split on the sign of the diver-row readout and whether the vertical readout is above or below -0.3.

I'm settling the priorities for the output units: dodging and the row-1 surfacing or descent come first at around 8, surfacing upward at 6, then fire and turn at 4. Vertical attraction sits lowest at about 2.5, and I'm checking whether that margin is enough so the sub doesn't drift away from a target it should be shooting.

I'm setting the fire and attraction priorities at 5 and 2, and adding a 1.5 baseline on the no-op/fire logit so the sub doesn't drift randomly when no signal is active.

I'm now setting the movement baselines: no-op at 0, fire at 1, and left, right, up and down at -2 each, so the sub stays put unless a drive pushes it. The vertical attraction should be weak enough that a target in the same row still gets fired at, so I'm weighing fire against that pull before tuning the numbers. With no horizontal signal the readout sits near zero, so the sub doesn't drift sideways.

I'm laying out the first-layer weights now, starting with the input indexing scheme and the units for the vertical veto, the attraction readouts, and the surfacing signal.

I'm now assigning the input units for each row: the danger, diver and surfacing readouts each get a per-row unit, with the player's row gating every cell and the content weights added on top. Each of these is set to fire only when the summed contributions clear a fixed bias, and I'm checking that the bounds stay tight when cells in other rows are active.

I'm working through the weight scheme for the vertical units, weighing a gating weight of 10 with bias -20 against the smaller content terms from other rows, and I'm checking that inactive units stay far enough below zero to read as off.

I'm setting the attraction weights for the vertical veto units, with the pull from each row falling off with distance and reversed for rows below. I'm also laying out the up-veto and down-veto weights on the cells in the adjacent row, using stronger values in the central columns.

I'm checking the veto terms for the vertical units: the up-veto and down-veto cells in the rows above and below, with the stronger weights in the central columns. The top row needs no special case here, and I'm noting that the column spread assumes the sub stays near the middle, which a one-cell drift still covers. Attraction from enemies and divers in nearby rows is already accounted for, so I'm moving on to the remaining weights.

I'm weighing whether attraction toward enemies would pull the sub back into a row it just dodged out of, since the bullet veto only covers a limited set of columns.

I'm writing out the bullet-veto logic for the per-row dodge unit, which should fire on any enemy bullet in the sub's row, whichever side of it the bullet is on.

I'm setting the bullet-dodge unit for each row so it fires whenever an enemy bullet is in the sub's row, with a weight of 3 that leaves an active unit clearly positive and an inactive one clearly negative. A diver in the same row would cancel the signal, which I'm treating as rare enough to ignore.

I'm now working out the observation-side weights for the offset-from-center channels, testing whether a simple linear weight per column keeps the back-cell and front-cell contributions balanced.

I'm checking the scaling for the offset-from-center outputs, using a factor of 2 so they land near ±0.96, and comparing the contamination from enemy trails in the middle columns against a narrower window.

I'm checking the edge cases where an enemy sits at or just behind my position, since those are the only times the scaled readout would pick up trail contamination. If the sub is centered, a bullet or enemy on my cells means I'm already in trouble, so that's an emergency case I'll handle separately.

I'm checking the contamination from enemy trails at the edge of the window, where a nearby enemy would only add a small error. Then I'm setting the D-channel weights so enemies push the readout hardest, with divers and bullets weighted less, and the player's own cells pulling the readout back toward center.

I'm now weighing whether to use step-shaped weights instead of linear ones for the diver and enemy readouts, since a linear weight would let a far-off diver outweigh a nearer enemy. A sign-based scheme would keep enemies stronger than divers, but it would lose the relative position information once the sub drifts off center.

I'm settling the weights for the diver and enemy readouts: columns on the left side get -1 and columns on the right get +1, with the center columns left at 0, so a far-off diver can't outweigh a nearer enemy. Recentering comes from a separate term tied to the sub's offset from the middle, and each enemy on one side should give about twice the signal of a diver or bullet.

I'm checking the recentering numbers against the enemy signal: when the sub has drifted two columns to the left, the pull back toward center partly cancels an enemy on that side, which could drop it under the firing threshold.

I'm trying a scale factor so the tanh outputs don't saturate and the enemy, diver, and recenter signals stay distinguishable, and I'm comparing the margins at a few offsets.

I'm checking whether the diver and enemy readouts stay separable after scaling the values down by 0.4, and the margins are small, about 0.03 in tanh space, so I'm considering a steeper second layer to sharpen them.

I'm checking how the recentering term behaves at the sub's drift: a single diver on one side would still push the readout toward that side with a moderate signal, which is fine since it nudges the sub toward the diver. The recenter band sits between about 0.08 and 0.72 in tanh space, so a diver alone lands inside it and would press the sub toward the diver's side.

Now I'm checking the diver-versus-enemy weighting in the layer-2 readout, and whether bullets pulling toward the recenter band could cause a bad move, which the vertical dodge would handle.

I'm checking the Seaquest unit that flags a hostile row and the rule that picks a row, which both depend on the enemy and diver counts. I'm also confirming that one row-0-or-1 unit switches on whenever the player occupies either of those rows, with its threshold set so it flips cleanly.

Now I'm defining the Layer-2 units and checking whether the readout thresholds still separate cleanly.

I'm working out the layer-2 readouts now, choosing a scale K and bias so each threshold splits the value ranges cleanly, and testing whether a distance-6 target would still clear a threshold of 0.05.

I'm adjusting the attraction weights so the nearer targets count for more and the farther ones taper off, with a threshold of 0.06 to decide what registers. The veto cases are still a concern, since a strong opposing attraction could partly offset them.

I'm checking whether the vertical dodge should trigger when the attraction readout is positive but weak versus strongly negative, and I'm considering a split point at -0.3 to separate the cases.

I'm now checking the dodge logic, where the down-dodge is gated on the attraction readout dropping below -0.06 and the up-dodge takes the remaining cases. In row 8 the down-dodge can't do anything, so I'm noting that the sub just stays put if the up-move is vetoed.

I'm now setting the scale factors for each layer-2 readout: a steeper slope for the vertical attraction thresholds, a moderate one for the diver and recenter bands, and a gentle one for the offset signs. The sign-based and direct units can use the full ±0.99 range as they are.

I'm checking the combined condition for the firing unit: the diver readout has to clear its threshold and the oxygen sign has to be positive. I'm setting the weights so a strong enemy signal with a negative oxygen term still ends up below zero.

I'm checking whether a single AND-style unit can combine the diver condition with the oxygen sign. The diver readout is continuous, so a linear sum with the oxygen term doesn't cleanly separate the cases. I'm weighing whether to steepen the diver unit in the first layer or spend extra units on that split.

I'm combining the diver readout with the oxygen sign in one linear term: a steep weight on the diver value, offset so that a negative oxygen signal pushes the total below zero.

I'm checking the AND-style units next: a continuous diver readout combined with a binary oxygen sign, using a large weight on the binary term so the continuous range can't overpower it. I'm working out the coefficients for the mirrored cases too, the left-enemy and right-enemy conditions gated on the oxygen sign.

I'm writing the AND-style readout for the right-enemy case, where the continuous diver value is combined with the oxygen sign in one linear term. I'm also setting up the mirrored left case and the recenter units, which turn on based on the diver readout's sign.

Still writing the veto and dodge units...

Still writing the dodge-up condition...

I'm working on the dodge-up unit now, gating it on the vertical attraction being above the midpoint and on a bullet being present in the row above, with the bullet readout offset so it only fires when that signal is strong.

Now I'm working out the surfacing unit: it should fire when the sub is in rows 2 through 8, the surface signal is on, the row-0-or-1 flag is off, and the vertical attraction isn't vetoing the move up.

I'm setting the surfacing unit's weights so it only fires when the surface signal is on, no enemy-row flag is set, and the up move isn't vetoed.

I'm settling on the surfacing unit as a logit-level combination instead of an explicit AND: the up logit gets a positive weight on the surface signal and a negative penalty from the down-veto unit, with the row-0-or-1 unit weighted higher so surfacing from row 1 still wins.

I'm now writing out the logit formulation: each layer-2 indicator gets a 0/1 form, and the output weights are halved so the sums convert cleanly into the W3 and b3 terms.

Still writing the right-move logit...

I'm working out the up-move logit: it starts at a base of -3, gains from the dodge-up and surfacing signals, and takes a heavy penalty when the up move is vetoed. In row 1 with the surface signal on, the surfacing term outweighs the veto so the sub still goes up, while without the surface signal the up logit drops very low so it doesn't surface by accident.

I'm setting the up-move logit as a sum of indicator terms: a base of -3, a boost from the dodge-up and surfacing signals, and a heavy penalty when the up move is vetoed. That way, the sub only surfaces in row 1 when the surface signal is on, and otherwise the up logit stays low.

I'm checking the baseline for the movement units: at -3 an up move would still fire about 1.7% of the time in row 2, which is too often given the sticky-up risk, so I'm lowering it to -5. That leaves the attraction term too weak against the fire logit, and I'm working out how to rebalance it.

I'm setting the fire baseline at 1 and the moves at -6, then raising the attraction term to +9 so a move wins clearly over firing once a target lines up. The intermediate check gives about 0.85 for moving, which I'm treating as strong enough.

I'm tuning the recenter and dodge weights so the dodge logit clearly wins, and now I'm checking how the surfacing term should compare against the fire baseline.

I'm adjusting the surfacing and veto weights so that up stays suppressed when the veto is active, and down gets a strong penalty when the vertical signal says it's unsafe. The remaining question is how to keep fire from winning in rows 0 and 1 when an enemy lines up with the sub.

I'm checking the up-move and down-move logits in rows 0 and 1, where the veto and the surfacing term have to balance. Down wins there once the no-surface case is on, and fire gets suppressed by the row-one flag. I'm now working out the surfacing term for row 1.

Still writing the up-move logit, combining the wall-check, dodge, and surfacing terms with the veto penalty...

Still working out the fire logit...

Now I'm checking the left and right logits, which add a turn term and a centering term. For the left case, the turn term only lines up when the left enemy is actually present, and the centering term cancels out when either enemy flag is set, so the logit comes to 7 in that case.

Still working out the dodge-unit weights so the thresholds line up with the fire and turn conditions...

Still working out the per-cell weights for the player term, where the recenter pull scales with the distance from the middle column, and checking the enemy and diver contributions against the tanh threshold...

I'm checking the fire and turn baselines against the recenter weights, and the scaled diver and enemy contributions land just above and below the tanh threshold, so the midpoint still works out.

I'm checking how a diver at column 8 pulls the sub right, with the recenter drift only slightly weakening that pull, so the right move should win for a while. Once the sub is adjacent to the diver it should pick them up, and then the recenter term will push it back toward the middle.

I'm now working out the object-position term, where a single cell pair would be enough if the sub stays inside the window, but the window cutoff could skew the sum when it sits outside.

I'm checking the object-position sum for the orientation signal: with the window at columns 3 to 6, the configs A through F stay inside it, so the sum comes out right. Case A works out to -2, facing left, and I'm running the remaining configs next.

I'm checking the orientation sum against the remaining configs, which all come out right, and then settling the diver weights in each row. The thing I'm stuck on is a bullet and a diver landing on opposite sides of the same cell, which cancels the dodge term and leaves no dodge, so I'm accepting that edge case for now.

I'm weighing whether to give the bullet and diver trails a partial weight, but two enemies would then falsely trigger a dodge, so I'm keeping the reject weight at -3. I'm also setting the vertical unit weights for the veto case and moving on to the surfacing gate on the W1 cells.

I'm working out the indices for the row-9 and row-0/1 cells in the weight table, and checking that the veto case still holds when the enemy sits in our own row.

I'm checking the dodge logic for the case where an enemy approaches from behind while I'm firing at another in front: the two sides cancel, so there's no dodge and attraction pulls me out of the row, which is fine. A remaining risk is oscillation after dodging into an adjacent row, since a bullet off to the edge columns won't veto the return move, though bullets should clear the window quickly.

Writing the layer-2 weights now, starting with the up-move logits from the veto and surfacing sums...

Still working out the layer-2 weights, combining the veto and dodge sums into the down-move and right-move logits...

Still working out the layer-2 weights, folding the dodge and attraction terms into the turn and centering logits.

Still writing layer-2 weights for the veto and surfacing terms...

Now I'm checking the bias term for the veto units, confirming the float precision stays safe with sums around 500, and noting that the inactive units still sit near -1 because their pre-activation stays well negative.

Checking the right-move logit for the enemy-right, facing-left case: the enemy term is strong, but the facing-left orientation pulls the other way, so I'm computing that sum next.

Still working out the right-move logit, with the diver and turn terms weighted against the centering term...

Now I'm setting the logits for the move and fire outputs, with the up and down terms built from the surfacing and dodge sums. The fire logit comes out to 1 plus 6 for each enemy-facing term and minus 6 when the row-one flag is set, so it resolves to 1 in the current case.

Checking the row 1 case with the surfacing term included, the up logit comes out well above the down logit, with fire still at 1.

Still working out the output weights for the fire and move logits, turning each indicator's coefficient into a half-value added to the matching weight and bias.

Still working out the up-move and down-move logits in layer 3, so the surfacing and dodge terms feed in with the right weights.

Now I'm setting the down-move logit in layer 3, where the next-row and same-row terms and the dodge-down term each get their own weight.

Now I'm checking the fire, left, and right sums with all their indicators off, and they come out to 1, -6, and -6 as expected. Next I'm laying out the W1 index scheme, where each cell's channel offset is row times 60 plus column times 6 plus channel, so the per-row units can be written as strided ranges.

Still setting the input weights for the V-indicator units, with each row's cells feeding its unit and a veto term on the row above.

Still working out the veto weights for the neighboring rows, deciding to use a slightly stronger magnitude at the edge columns so the enemy term reliably crosses the down threshold.

Still working out the attraction weights for each unit, row by row, with the falloff values for the distance from its row.

Still working out the window-column weights for the outward-facing units, setting the gate and the per-column values across the row.

Still setting the weights for the diver units, with the row-k cells running from about 10.27 down to 9.73 across the columns.

Still setting the input weights for the diver units, with the danger and attraction channels in each row set to small signed values that push toward the center.

Still writing the input weights for the Y units, with the bullet and diver channels in each row set to counter each other.

Checking the row-3 case next: if the enemies sit at rows 2 and 3 with no veto on the down move, the attraction keeps pulling the sub downward through the middle rows.

Now I'm checking the case where a fish enters row 3 at the far right, moving left toward the sub in row 5, to see how strongly the attraction pulls the up-move logit.

Now I'm checking the case where the sub has reached row 3 and the enemy in the far right column is closing in: the attraction is strong enough to turn it right, and a bullet fired right should hit within a few steps. While the gun is cooling down, I'm looking at how the sub holds its position.

Now I'm checking how the sub holds its position when the gun is cooling down: it keeps pressing fire as a no-op until the target is gone, and once the kill happens the diver signal drops back to zero. Our own bullets don't count toward the danger or attraction channels, so they won't pull the sub around.

Now I'm working through the surfacing logic: the surface signal kicks in when oxygen runs low and a diver is held, so the sub climbs while the veto keeps it clear of enemies, then steps to row 0 and drops back down once the oxygen refills. The open question is what happens without a diver, since the oxygen would run out around step 200, so I need the diver attraction to keep pulling the sub toward rescues.

Now I'm weighing how the diver count and the surfacing cost trade off over a long run. Each surfacing adds a diver but speeds up the spawns and quickens the enemies, so the run should eventually end, though it should score well before that. Once six divers are held, the attraction just keeps pulling toward rescues without any bonus I can detect.

Now I'm checking the down-move threshold, which depends on the veto signal and the Y-dodge term.

Now I'm checking the trigger thresholds for the two down-and-up dodge units around the veto value, and the overlap band where both fire, which I'll resolve either way. Next I'm confirming the case where the sub sits in row 2 and only the dodge-down term is active.

Now I'm checking the layer-2 dodge-down bias against the no-bullet and bullet cases, and it stays off when no bullet is present and only turns on when the veto is weak.

Now I'm checking the threshold conditions for the up, down, and dodge units against the veto and bullet cases, confirming each one switches on only where expected.

Still checking the signs on the remaining gate sums, where the fire, left, and turn terms each come out to the expected constant after cancelling the six-unit offsets.

Now I'm checking the bounds on the inactive units: their small residual outputs stay negligible once multiplied by the weights, since the pre-activations sit far below zero.

Checking the active gate sums for the outward units: the player's own row gets gated by the sum over the matching columns, and the stray weights outside the window could push an off-center sub to the wrong value.

Now I'm checking the recentering case: a drift of one column trips the threshold, so the sub moves back toward center, and with the recenter logit above fire and no-op the recentering wins out.

Now I'm checking the recentering case against the attraction term: the recenter logit only wins when no stronger signal is pushing the sub elsewhere, so attraction should take priority. I'm also considering whether an enemy right beside the sub, or one drifting away on the right, would change the fire decision, and it looks fine since a shot facing away still kills it.

I'm checking the veto for row 1 and the attraction from rows with enemies in my column, which should be fine since the veto only applies when a row is adjacent. I also want to confirm that bullets entering from the sides at the edge columns get dodged rather than hit me, and that the policy just keeps firing when nothing is around.

I'm checking that the shared-sign terms for the spare units and the layer-2 copies cancel out to zero, so they don't leak into the outputs. Next I'm working through the surface-trigger threshold for the S unit, starting with the case where the sub is in row 1.

Now I'm checking the surface-trigger units, which I'm verifying with the layer-1 values: when both the surface and row-1 signals are on, the output is about 4.9, and when only one is on it drops to about -5.1.

Writing the first-layer weights for the attraction and veto units now...

Writing out the first-layer weights for the attraction units now, starting with the veto offsets around each row.

Writing the first-layer weights for the next attraction unit, starting with the rows around row 3...

Writing the veto and attraction weights for the next units, working through each row's offsets.

Still filling in the first-layer weights for the veto and attraction units, now working through the rows around row 7 and row 8.

Still filling in the veto and attraction weights for the last unit, now working through the rows around row 8.

Still writing the first-layer weights for the outward units, now filling in the per-row offsets for the next block...

Writing the first-layer weights for the diver units now...

Still writing the first-layer weights for the diver and Y-dodge units...

Still writing the first-layer weights for the diver and Y-dodge units...

Still writing the second-layer output weights and biases, now filling in the columns for the up, down, fire, and turn units.

Still writing the second-layer output weights and biases, now setting the last few columns for the sub's reserve and depth-handling units.

Still writing the layer-3 weights for the movement outputs.

Still writing the output-layer weights for the movement units, now checking the sums that decide up and down in the top rows.

Still checking the layer-3 sums for fire and left in the rows near the bottom, confirming the signs come out as expected.

Checking the sticky-action risk in row 2: with no danger there, the up logit sits around -6 against fire near 1 and down near 3, so going up is very unlikely.

I'm double-checking the upward and downward logits in the top two rows, which come out as expected once the surface signal is absent. I'm also looking at whether enemies in my own row, approaching from either side, get handled by the bullet dodge and the fire logic, and it looks fine. The remaining worry is a rare sticky-action repeat that could push the sub up into danger from row 2, which I'm noting as unlikely.

Now I'm wrapping up the first-layer weights for the diver and Y-dodge units, using a per-column offset for the diver channel and a fixed gate for the Y units. The remaining step is writing out the full network as described.

