I'm sketching out a policy network by hand, aiming to keep the approach simple. The game has the player at a position on rows 1 through 8, with one entity per row that slides sideways every few frames, and getting hit costs a life while a collision with gold counts as a point. My working idea is to avoid the enemies, starting with a basic heuristic about which row to stay in.

I'm checking whether a fixed-column strategy works better, since the enemies' absolute positions make relative features hard to compute with a single hidden layer. Tanh units could approximate the needed conjunctions of player and enemy position, but only if I limit where the player can be.

I'm weighing whether a fixed column x0 makes the enemy-threat features absolute, so each row's danger can be computed on its own. I'd then need a layer-1 unit for each row and relation (same, above, below) to pair the player's row with the danger there, which runs into the 32-unit budget.

I'm working out how to make the danger for each row a single unit: a tanh that fires only when the player is in that row and an enemy sits near the fixed column. Summing those per-row units in the second layer would give the total threat for the player's row.

I'm now looking at how the enemies move: they start at a slow pace and speed up as the ramp progresses, reaching one cell per frame after about 800 frames, with spawns arriving every frame by around 900.

I'm recalling the MinAtar paper's Asterix results to gauge what a trained agent scores, roughly in the teens to twenties. At full speed, every row stays filled and the player has to dodge constantly. Moving one cell per frame, the player collides with an enemy that steps onto its cell after the player's move, so a sideways step into an oncoming enemy is caught on the first check.

I'm working out the collision rule for a sideways escape: if the player steps left and the enemy moves right into the next cell, nothing hits, but the enemy keeps coming, so the player has to keep moving or switch rows. For a vertical move, the danger in the new row comes from an enemy already at the target column or one adjacent to it that steps in on the move frame.

I'm working out how an enemy's trail position tells me which way it is moving, since the cell behind it shows the direction. Staying in place is risky too, because an enemy at a neighboring column closes in every move, so I need to keep watching for threats beside me as well as on my current cell.

I'm working out how an enemy's trail reveals its direction at the edges, where a missing trail is ambiguous. Since each row holds only one entity, a trail in that row always belongs to that row's enemy. For a fixed player column x0, the threat in a row is an enemy approaching x0, which I can read from which side the trail sits on.

I'm working out how to tell an enemy moving toward the player's fixed column from its trail: a trail just behind it on the near side means it's closing in. Since gold shares the trail channel, I still have to confirm an enemy is actually there before counting it as a threat.

I'm settling on a linear feature for each row: enemies inside a window around the fixed column count positively, and a trail sitting between an enemy and the player, meaning it's receding, counts negatively.

I'm working out how a trail at a given column tells me which way its entity is moving, and whether that means it's approaching or receding relative to the player's column. A trail on the far side of an entity means it's closing in, and I'm weighing how to assign a negative weight to trails that belong to receding entities.

I'm working through a fixed-column threat feature, where a trail on the far side of an enemy would mark it as approaching. The trouble is that a trail at a given column could belong to an approaching enemy on one side or a receding one on the other, so I'm looking at a different pairing.

Simplifying the threat check: I'll drop the direction tracking and treat any enemy within a distance of one or two cells of the fixed column as danger in that row, accepting that it's conservative. The player just picks whichever row looks least threatened, and getting boxed in is fatal regardless, so I'm also keeping in mind that gold adds to the score.

I'm wondering whether gold is the real goal, since I only collect it when I happen to be in its row as it passes my column. Survival seems to matter most, because at full difficulty spawns come every frame and a third of them are gold. I also half-recall MinAtar Asterix scores from DQN and PPO being somewhere in the tens, so I'm trying to gauge what a good target is.

I'm settling on a fixed player column, which lets me drop left and right from the action choice and only weigh stay, up, and down. For robustness I'd still like a centering term that nudges the player back to that column. I'm also considering a large logit gap against the horizontal moves so they almost never get sampled.

I'm settling on column 5 as the fixed position, since the player never needs to move sideways and a large logit gap keeps horizontal actions almost unsampled. I'm also weighing whether an edge column would be worse, since entities spawn at the border and could land right on the player.

Now I'm working out the danger for staying put at column 5: an enemy at column 4 moving right or one at column 6 moving left would hit me this frame. Moving up means checking row r-1 for an enemy sitting on column 5, or one coming from column 4 or 6 in that row.

I'm checking how the danger of a receding enemy at column 4 or 6 changes the stay option, and how entities at distance 2 or 3 should be weighted as lookahead threats.

I'm now checking the threat levels for each row at column 5: an enemy at column 4 with its trail at 3 is fatal, and so is one at column 6 with its trail at 7, while those further out only add lower-level danger. I'm trying to work out whether I can compute, per row, the case where an enemy sits at 4 and its trail at 3 in one pass.

I'm working out the threat signal for a row at column 5: an enemy at column 4 with its trail at 3 is moving toward me, while one at 4 with its trail at 5 is moving away. Since each row holds a single entity, I can express "enemy at 4 moving right" as a difference of the enemy and trail channels there.

I'm checking whether a single row's threat can be written as a sum of two inputs: the enemy's cell and its trail cell. Since each row holds only one entity, at most one enemy cell and one trail cell are active per row, so an enemy at column 4 moving right can be captured by thresholding their sum.

I'm writing the danger score for each row as a linear sum over the enemy cell and its trail cell, since only one entity sits in a row at a time. Gold also leaves a trail, so I'll need thresholds to keep it from being counted as a threat.

I'm going with a zero trail weight for every cell except the one just behind an entity, so gold stays neutral and direction only matters through the trail. The trail at column 5 is the useful signal: it only appears for an enemy at 4 moving left or at 6 moving right, both of which are receding, so a large negative weight there should cancel the danger at distance one.

I'm weighing whether a trail at column 3 can be attributed to an approaching enemy at column 4 or a receding one at column 2, since both produce the same cell. Assigning per-column weights to enemy and trail cells would let each row's danger reduce to a sum over at most two active inputs.

I'm now assigning a value to each cell of the enemy and trail channels, checking the four fatal and near-fatal combinations at columns 4 and 6, plus the approaching cases at columns 3 and 7.

I'm weighing trail weights b so that the sum for each row stays near zero for gold, keeping false danger out, while receding enemies get pushed down.

I'm setting the trail weight at column 5 to cancel the receding cases, then checking the trail weights at columns 4 and 3 so that gold stays neutral while the approaching enemies still register as danger.

I'm settling the trail weights so that the receding cases cancel out: a large negative value at column 5 handles the enemies at 4 moving left and at 6 moving right, and smaller negative values at columns 4 and 6 keep the approaching-enemy cases at distance one from being pushed too far. The gold trails then fall into negative values near the center, which is a mild pull toward those rows but never masks an enemy, since each row holds only one entity.

I'm assigning each cell a weight so that a row's danger reduces to two terms: the enemy's column and its trail column. Setting the trail weight at column 5 to the negative of the distance-one weight cancels the receding cases, and the remaining values give graded danger with the approaching enemies still registering. The one thing I'm still weighing is whether the timing of movement changes how fatal an enemy at column 4 moving right really is.

I'm now settling the danger readout so each row gets a single score from its enemy and trail cells. Staying put and moving into a row both face the same fatal cases, so I can compare all the actions with one function and pick the lowest danger. The next step is wiring up the danger value for each of the eight rows.

I'm laying out the network in layers: eight units for each row's danger score, plus eight units recording which row the player is in. The second layer then pairs those into 24 conjunction units, one for each combination of player row and danger in a nearby row. That fits within the unit budget at both layers.

I'm working out how to make the second layer graded rather than binary: the layer-two unit should take the danger value in a neighboring row together with the player's row, so that when the player isn't in that row the unit sits at a fixed value, and when they are, it passes through the graded danger.

I'm settling the constant offset from inactive conjunction units: with seven of them sitting at -1, each output logit picks up a fixed negative term, so I'll need to check whether that offset is the same for every action and can be ignored.

I'm making the layer-one units compute the conjunctions directly, so each one combines a row's player indicator with a linear sum of the raw inputs for the neighboring row, which would drop a whole layer.

I'm settling the first layer so that each of the 24 conjunction units combines a row's player indicator with a linear sum of the neighboring row's inputs, with a large negative push whenever the player isn't in that row. The second layer then just combines these into one danger value per action, aiming for a simple tanh readout that avoids saturation.

I'm settling on a simple plan: the remaining spare first-layer units could handle gold attraction or horizontal moves later, but the core network comes first. I'm assuming the player stays in column 5 with a large logit gap, so I'll skip any centering units for now.

I'm checking whether staying in column 5 holds up at high difficulty, where entities spawn every frame and rows are almost always full. Each row's entity passes the center column roughly once every 10 or 11 frames, so it occupies that spot about 10% of the time.

I'm settling on gold attraction through the same row score: a gold at column 5 in the target row would be collected on entry, and golds approaching at columns 4 or 6 could add a modest bonus, with survival still the main priority.

I'm noticing that receding gold at column 4 would get the same negative score as a fatal enemy, since the trail weight at column 5 is shared, so a row with a gold passing away looks safer than an empty one. That's a side effect I'll need to separate out before tuning gold attraction.

I'm finding that gold weights can't separate the two cases: a gold at column 4 moving right would be pulled by the same term that makes a gold at column 4 moving left look attractive, so one weight can't make the right-moving one attractive while leaving the left-moving one neutral.

I'm trying a different set of trail weights: zeroing the weight at column 4 and putting a positive value at column 3 so that a right-moving enemy at 4 registers while a left-moving one does not. But that positive weight would wrongly flag an enemy at column 2 moving left, and a gold at 4 moving right would look fatal too, so this trade-off isn't clean.

I'm now considering a second option: give layer one a row-danger unit and a separate gold-attraction unit for each row, which would free up room for the conjunctions in layer two. The extra spare units would then let me keep enemy and gold signals apart instead of sharing one trail weight.

I'm working out how the gold cells could cancel out the trail effect, so that a gold passing through a row doesn't register as danger. The idea is to choose the gold weights so the gold's contribution to the danger unit is zero in both movement directions.

I'm working out how to weight the gold cells so they don't trigger a false danger signal. Matching each gold's weight to the trail value on the adjacent cell gives inconsistent results across columns, so I'm considering clamping the gold contributions to non-positive values, which would keep them from registering as danger.

I'm now trying to set the danger score as a tanh of the row's weighted sum shifted by a threshold, so that the safe cases saturate at the bottom and the graded danger levels fall in between, scaling the weights so the strongest threat sits near the top of the range.

I'm trying to make the danger score saturate cleanly: I'll pass the row total through a tanh with a shift and scale, so the safe rows settle near the bottom while the graded levels land between.

I'm checking the danger score as a tanh of 0.8 times the row total minus 1, and working through the values: fully safe rows land near -0.76, a row with a gold passing away near -1, and the fatal case near 0.98. That spread separates a one-cell threat from a two-cell one, so the scaling looks workable.

I'm weighing whether to fold the gold-attraction and danger terms into one gated layer-one unit per row, which would use all 24 units with nothing left for gold. A two-layer layout looks more flexible: layer one gets a danger unit and a player-row unit for each of the eight rows, and layer two combines them.

Now I'm laying out the rest of the first layer: eight units that encode each row's player presence as a signed value, plus eight gold-attraction units, leaving a few spares. The second layer would then hold 24 conjunction units tied to each row and action, with the target row's danger and gold signals feeding into a pre-activation whose bias depends on whether the player is in that row.

I'm laying out the logits so that stay, up and down come out large and positive while left, right and fire are pushed far below them, with the saturated inactive units giving a constant offset that I'll account for.

I'm checking whether the first-layer row-danger units could also serve as the basis for the target-row choice, since the up action at row 1 just maps back to staying there, so its logit can match the no-op one.

I'm picking the logit scale K: with the layer-two units tanh-ing roughly the danger values, a scale near 10 gives a clear margin between the safe rows and the fatal one, and I'm checking the gap against the medium-danger case next.

I'm testing a larger logit scale, K = 20, to see whether it sharpens the gap between medium and fatal danger. That would cut the chance of picking the fatal row to about 0.5%, but it also makes receding-gold rows slightly preferred over empty ones.

I'm considering a simpler alternative: a no-op bonus so the agent doesn't move unnecessarily, though a medium-danger row should still be left, since an enemy two cells away will be fatal next frame. I also note that sticky actions could force a repeated move I'd rather avoid, which I can't control from the policy alone.

I'm now setting the gold-attraction signal for each row: gold on the target cell or a gold drifting toward the player's column pushes that row's score up, and I'm weighing that against the enemy trail contributions.

I'm now choosing the gold weights so the gold cells alone drive the attraction, while the enemy trail gets negative weights where it would otherwise pull toward danger. Gold at column 4 or 6 gets a full weight, gold in the middle column gets a bit more, and the trail weights are set so receding gold doesn't spill into the enemy-driven rows.

I'm assigning the gold weights by hand: gold at column 5 gets 1.5, the trail weights at columns 4 and 6 get -0.5, and the trail at column 5 gets -1, so that enemy trails never read as attraction. That leaves gold in column 5 at 1.0 in either direction, column 4 at 1 moving right, and column 6 at 1 moving left, with the outer cells weighted at 0.5. I'm also considering passing the gold sum through a tanh with a scale of 1.5.

I'm working out how to scale the gold attraction, clipping it at zero so enemy trails don't read as attraction, and I'm considering how gold should carry a positive pull without overriding the danger signal in layer two.

I'm now working through the gold rows: since each row holds only one entity, a gold row should look safe, and I'm checking the combined pre-activation of danger minus half the gold signal for an empty safe row, which comes out near -0.36.

I'm switching to a smaller layer-two scale, pre = 0.5·D − 0.25·G, to keep the medium-versus-fatal gap from being squeezed by tanh saturation. Under that, an empty safe row lands just under zero while the fatal row stays clearly higher.

I'm settling the layer-one danger scale now, using a pre-activation of 0.6 times the threat level minus 1.2, which puts an empty row near -0.83 and a mild threat near -0.54.

I'm settling the layer-two pre-activation as 0.6 times the danger minus 0.3 times the gold signal, plus a bias that depends on whether the player is in that row, and I'm checking the range of the gold term before fixing the scale.

I'm checking the logit gaps at K = 25: the fatal row sits about 9.75 above the medium one, medium about 12 above safe, and gold rows roughly 9 above safe ones, so the margins look comfortable.

I'm checking that a gold row is never dangerous, since its only entity is gold, and that staying on a gold cell just collects it. I'm also noting that a gold entity can't sit on the player's cell while they're alive, so that case never shows up in the danger calculation. Now I'm turning to the trapping situation.

I'm still weighing the sticky-action risk and considered adding a small no-op bias so ties resolve to staying put, which should keep repeated moves from walking the player into danger. I'm also noting that a gold-driven logit gap of about 9 at K = 25 is strong enough that it might dominate other rows.

I'm weighing whether to consider horizontal dodging when the current row's enemy is closing in and both adjacent rows are blocked, since stepping sideways could buy a frame. But moving off column 5 would break the danger calculation I've built around that column, so I'm leaning toward skipping it.

Now I'm checking the edge rows, where row 1 going up and row 8 going down just means staying put. I'm also confirming that when the player steps into a new row, the collision check runs against the entities' current positions before they move, so the fatal cases at column 5 and the trails at columns 4 and 6 are already accounted for.

Now I'm checking the edge cases for the trail and entity positions, and confirming the danger levels for each column against the entity-direction rules.

I'm checking the danger weights for the fatal and medium cases in each column, confirming that the enemy trails on columns 4 and 6 give a fatal value at column 4 from the left-moving side and the adjacent rows come out as expected.

I'm checking the trail contributions for the remaining entities, confirming that the gold positions and the rows near the edges all come out at zero or below, so they never read as danger. Next I'm starting the danger value for each level, working from the linear pre-activation.

I'm converting the danger levels into their final scaled values, which spread evenly from safe to fatal. Then I'm setting the input weights for each danger unit by column, with the enemy channel weighted heavily toward the center and the trail channel pushed negative.

Writing out the strided weight assignments for the danger units now, filling in each row's enemy and trail channels with the computed values, and starting on the player-row units.

Still writing the gold-row weights...

Still working out the gold-row weights and checking that the empty and gold-row pre-activations come out about the same.

I'm checking how the layer-two units map each row to its stay, up, and down targets, with the gold and danger terms scaled and the player bias applied.

Still setting the output weights, with the trailing terms of the layer-two sum and the logit offsets worked out.

Still tuning the output-layer offsets so the stay, up, and down logits stay close together while left, right, and fire sit well below them.

I'm setting the last output-layer offsets to -60 for left, right, and fire, so they stay far below the movement logits. I'm also asking whether the player's row could ever fall outside 1 through 8, and I'm settling that it can't, with the column always at 5. Then I'm weighing whether stay and move logits being nearly equal would cause needless sideways drift, which seems harmless since moves into safe rows are fine but the sticky-action repeats are worth keeping an eye on.

I'm weighing whether the medium-threat stay versus move comparison holds up with the tie-break, and I'm considering a two-step lookahead for cases where the current row and both neighbors are all fatal, perhaps a horizontal dodge to break the tie.

I'm checking the escape-by-running idea: if the enemy keeps pace with the player moving sideways, the player only stays ahead until the edge and eventually gets caught, so that isn't a real fix. I'm also weighing whether spare first-layer units could help anticipate danger at slower speeds, but that seems unnecessary here, and early on with the spawn timer there are few entities anyway.

Now I'm checking the danger and gold values for the neighbor rows, including the case where an enemy sits at column 5 in an adjacent row and is moving away from the player.

I'm working through the layer-two pre-activations for the safe, mild, and medium threat cases, showing that an empty safe row comes out around -0.26 while a mild one sits near -0.10. Then I'm checking the fatal case from an enemy on the right side.

Now I'm checking the gold-side values for the adjacent rows, where a gold piece two rows over at column 4 nudges the pre-activation down to about -0.36, a bit more attractive than an empty row.

Now I'm working out the logit values from the danger and gold terms: safe rows around 6.6, gold near 15.5, fatal near -15.5, and medium about -5.6. That leaves a gap of roughly ten between fatal and medium, so the network should steer clear of the fatal moves.

Next I'm checking how often a neighboring row is unsafe when I need to leave a medium row, and whether a two-step escape is worth it at high speed.

Next I'm weighing whether rows near the edges, like row 1 or row 8, deserve a different treatment since they only have one neighbor to escape into.

I'm considering a small penalty on the layer-two units that target rows 1 and 8, since those rows have only one neighbor to escape into. I'd add about 0.08 to their bias so the network leans slightly away from the edges, and I'll keep the inactive-case values nearly unchanged.

Still writing the layer-one weights for the danger units...

Still writing the layer-one weights for the danger units...

Still writing the layer-one weight rows for each board row...

Still writing the layer-two weights...

Still writing the layer-two weights for the remaining rows...

Still writing the layer-two weights for the stay, up, and down units...

Still writing the stay-row weights for the remaining danger units...

Still writing the output weights...

Still setting the bias offsets for the output-layer logits.

Checking the sign and magnitude of the remaining pre-activation terms, I see the danger contribution stays small enough that the tanh saturates near -1, and the active player unit comes out close to zero. Then I'm confirming that the player is always in column 5 and never moves sideways, so the column-centric weights hold.

Checking the last layer's weights and the direction convention for the trail, I'm confirming that the grid indexing and the column-5 player position line up with the earlier setup.

