# Findings from the main grid (notes for the write-up)

Source: `analysis/out/main_claude/summary.md`, built from 80 markets and 160 target agents on
October 23, 2026. The design was Claude Haiku 5.5 and Sonnet 5.5 × offer price ($92, $96) × four
conditions × five seeds. List-price cost was $19.15. There were 0 failed calls and 0 undeliverable
private messages. Verbal labels come from a Claude Sonnet 5.5 judge, which stays primary under the
pre-committed decision rule. The section "Label validation" below checks them against a second judge, a
rule coder and 32 known-answer markets, and reports where the conclusions depend on the label source.

## Pre-registered hypotheses

1. **H1 (direct vs benign acceptance): not supported, in the opposite direction from expected.**
   Direct offers were accepted 0/40 times, against 0/40 for benign messages. No model accepted an
   explicit cartel proposal at either price.
2. **Hint vs benign.** This comparison sits in the same table and was not a separate hypothesis.
   Hints drew written agreement 8/40 times against 0/40 for benign (pooled Fisher p = 0.005). Seven
   of the eight came from Sonnet, and five of those were at $92.
3. **H2 ($92 vs $96 acceptance): not supported.** Acceptance was 6/40 at $92 and 2/40 at $96
   (Fisher p = 0.26). The direction matches the idea that a credible price is accepted more, but the
   test is underpowered.
4. **H3 (say vs do): supported, and stark.** All eight targets that agreed in writing failed to hold
   the named price (precision 0/8). No target held the floor in at least half the post hours in any
   condition. The highest condition-level hold rate was 0.086.
5. **H4 (refused or ignored the sting but colluded with the peer): supported.** This happened for
   41/72 targets, or 57% (Wilson 95% CI 45% to 68%). The rate was about 75% to 79% for Haiku and 27%
   to 39% for Sonnet.
6. **H5 (entrapment, change in ask index vs silent): no detectable increase.** No offer condition
   raised target prices. The only interval excluding zero is a decrease, for Haiku at $96 under the
   direct offer (−0.165, CI −0.245 to −0.059), which is about $1.65 lower than silent.

## Exploratory (label as such in the report)

1. **A direct offer suppressed peer coordination.** Peer coordination appeared in 39/40 silent
   targets and 12/40 direct targets (Fisher p < 0.001). For Sonnet it was 1/20 against 19/20. In
   transcripts, targets that received the explicit offer often announced publicly that they would
   price independently, for example "I'm not going to coordinate on prices." Benign messages also
   lowered peer coordination slightly (31/40, p = 0.014). Hints did not (37/40).
   A judge-free count of joint-proposal language ("let's", "we should" plus a pricing term, sent to the
   other target) agrees. Sonnet averaged 0.1 such messages per target under direct against 4.9 under
   silent, and Haiku 6.6 against 10.9 (`fig_joint_main.png`). How closely the two targets' asks track
   each other did not differ by condition (mean gap $0.22 to $0.34), because both targets follow the
   same best bid whether or not they talk.
   This effect is being replicated on fresh seeds with a compliance-warning control
   (`prereg_replication.md`), and the replication result should decide how strongly the report claims it.
2. **The planted seller's price alone moved prices.** Silent markets, where the planted seller says
   nothing and only asks, averaged about $2.5 higher target asks at $96 than at $92 (Haiku 91.1 vs
   88.3, Sonnet 91.0 vs 88.8). Opening asks also differ, because the planted seller's opening order
   equals its price, so this is anchoring from the order book rather than words. It bears on
   question 3.1, since actions can carry coordination.
3. **"Collusion" here was mostly talk at competitive prices.** Target asks stayed between about $86
   and $92 in every arm, below or near the theoretical competitive price of $90. Agents
   coordinated in words on bands and "splitting flow", but the bands sat near or under competitive
   levels, because buyers bid low.

## Figures

`paper/figures/`: `fig_sting_outcomes.png` (what a sting operator sees vs what happened), `fig_peer_main.png`,
`fig_joint_main.png` and `fig_asks_main.png`. Rebuild with `uv run python -m analysis.figures results/main_claude`.

## Candidate headline

The sting failed as a detector. Every explicit offer was refused, the few soft agreements were never
honored, and most targets that rebuffed the planted seller were coordinating with their peer at the
same time. The explicit offer instead worked as a deterrent on coordination talk. A sting reading of
"refused, so clean" would have been wrong for more than half of the agents.

## Threats to validity to state

1. Every judged label comes from a Claude-family judge, and the known-answer markets only cover easy
   cases (see "Label validation"). No human coded the transcripts.
2. Prices never reached supracompetitive levels, so "peer collusion" is coordination talk, not
   proven harm. The plus-factors framing applies.
3. There are 10 targets per cell, and only one market design and one model family.
4. Claude sampling is unseeded, so hour-1 asks differ by condition and matched seeds pair only the
   cast and the opening book.
5. The planted seller never replies. Acceptance might be higher against an adaptive partner.

## Replication (pre-registered in `prereg_replication.md`, run October 24, 2026)

There were 60 new markets on fresh seeds 5 to 14, all at $92, with silent, direct and warning conditions on
Haiku 5.5 and Sonnet 5.5. Cost was $14.26 at list price, with 0 failed calls. The judge and its prompt
are unchanged. Counts are target-level and pooled over models.

1. **R1 replicated.** Peer coordination fell from 36/40 under silent to 15/40 under direct (one-sided
   Fisher p = 7.5e-7). Sonnet went from 16/20 to 7/20 and Haiku from 20/20 to 8/20. Sonnet's direct
   rate was higher than in the main grid (1/20), so the size of the effect varies across seeds.
2. **R2 held, more weakly.** Proposers (at least 2 joint-proposal messages) fell from 34/40 to 26/40
   (p = 0.035). Haiku kept proposing in words (19/20 proposers under direct) even where the judge saw
   less coordination, so the judge-free measure is coarse for Haiku. The joint-proposal regex also
   counts independence sentences such as "each of us should price independently", which are common
   under direct, so it overstates proposing under direct and this test is conservative.
3. **R3 held.** A compliance warning that offered nothing cut peer coordination to 7/40
   (p = 2.0e-11). For Sonnet it was 0/20, with zero joint-proposal messages from hour 2 on.
4. **R4 not significant.** Direct (15/40) against warning (7/40) gave two-sided p = 0.078, with the
   warning numerically lower.
5. **Pre-registered reading.** R1 and R3 hold and R4 does not, which is consistent with salience.
   Mentioning that coordination is collusion is enough to suppress coordination talk, and the offer
   itself does not deter more than a plain reminder does.
6. **Prices did not move.** No condition changed the target ask index or trade price relative to
   silent (all paired 95% intervals include zero). Prices stayed near or below the $90 competitive
   level, so what was deterred was coordination talk, not supracompetitive pricing.
7. **Timing (exploratory, `fig_timing_replication.png`).** Joint-proposal rates are similar across
   conditions in hour 1, before any message is read. They split at hour 2, when the first message
   arrives. Under warning, Haiku drifted back up slowly after the last message (hour 9), and Sonnet
   stayed at zero.
8. **Refused or ignored sting, still coordinating.** This was 13/37 targets (35%, CI 22% to 51%),
   lower than the main grid's 57% because the replication has no hint arm, where this was most common.

## Label validation (deviation logged October 24, 05:10 ET, before any of these labels existed)

No second human coder was available, so hand labels were replaced by three automated checks. A second
judge, Claude Opus 5.5, labelled all 280 main and replication target-markets with a prompt written
separately from the coding manual (`paper/codebook.md`). A rule-based coder (`analysis/rules.py`)
labelled the same items. And 32 known-answer markets (`configs/known_answer_claude.json`, $7.48) gave
targets a standing instruction from their manager to collude with the peer, stay independent, accept the
planted offer or reject it. Outputs are in `results_final/analysis/validation/`.

1. **Agreement.** Over all 280 items, Sonnet-Opus kappa was 0.86 for offer_response and 0.78 for
   peer_collusion, and Fleiss kappa across the three raters was 0.81 and 0.73. On the harder subset of
   items that had text to judge, it fell to 0.56 and 0.68 (Fleiss 0.44 and 0.58). Main-grid
   offer_response on that subset was 0.50, below the 0.6 bar.
2. **Known-answer accuracy.** Wherever a target did what it was told, all three raters matched the
   intended label on every item (41 of 41 for offer_response and 42 of 42 for peer_collusion, once the one apparent miss below is counted as a target that did not comply).
   This only validates easy cases. The collude arm produced just 2 compliant targets, so the set
   barely tests "yes" for peer coordination.
3. **The disagreements are one-directional.** All 27 Sonnet-Opus disagreements on peer_collusion are
   Sonnet "no" and Opus "yes", and 16 of them are in direct-offer markets. They concern soft or
   advisory coordination, such as "holding 90+ keeps margins healthy for all of us" or "let's keep steps
   gradual and avoid racing toward cost", which Opus's codebook counts and Sonnet's prompt does not.
   An earlier version of these notes blamed the independence disclaimers that often sit in the same
   messages. The pre-registered monitor test below rules that out, because adding or removing
   disclaimers did not change Sonnet's verdicts.
4. **Disclaimers (exploratory, post hoc, judge-free, `analysis/disclaimers.py`).** About half of the
   targets under direct (45% main, 53% replication) and warning (50%) posted independence disclaimers,
   against 5% to 8% under silent, benign and hint. A check of 20 regex hits found no false positives,
   and disclaimers start in hour 2, when the first planted message is read. Do not use the earlier
   figure for messages with both a disclaimer and joint-proposal language (23% and 33%). The
   joint-proposal regex counts "each of us" and "let's", so "Each of us should price independently"
   counts as a joint proposal, and in 19 of 27 such targets the "proposal" was the independence sentence
   itself. Under warning, targets mostly went quiet (4.8 messages per target against 13.4 under silent).
5. **Decision rule outcome.** Sonnet's known-answer accuracy on compliant targets is at least 0.8 for
   both labels, and Sonnet-Opus kappa over all items is at least 0.6, so Sonnet labels stay primary as
   pre-committed. The rule did not anticipate a disagreement concentrated in one condition. The report
   should therefore show every key test under all four label sources (`fig_label_sources.png`).

| Test | Sonnet (primary) | Opus | Rules | Majority |
|---|---|---|---|---|
| Hint vs benign acceptance, main | 8/40 vs 0/40, p = 0.005, fragility 2 | 10/40, p = 0.001, 3 | 10/40, p = 0.001, 3 | 10/40, p = 0.001, 3 |
| H2 $92 vs $96 acceptance | 6/40 vs 2/40, p = 0.26 | 7 vs 4, p = 0.52 | 6 vs 5, p = 1.0 | 6 vs 4, p = 0.74 |
| Direct vs silent peer, main | 12/40 vs 39/40, fragility 18 | 17 vs 40, 14 | 20 vs 38, 9 | 16 vs 39, 14 |
| R1 direct < silent peer | 15/40 vs 36/40, p = 7e-7, fragility 13 | 26 vs 38, p = 7e-4, 5 | 29 vs 38, p = 0.007, 3 | 24 vs 38, p = 1.5e-4, 7 |
| R3 warning < silent peer | 7/40 vs 36/40, fragility 21 | 8 vs 38, 22 | 10 vs 38, 20 | 8 vs 38, 22 |
| R4 direct vs warning peer | 15 vs 7, p = 0.078 | 26 vs 8, p = 9e-5 | 29 vs 10, p = 4e-5 | 24 vs 8, p = 5e-4 |
| H4 refused but peer-colluding | 41/72 | 45/69 | 47/69 | 44/70 |

Fragility is the fewest label flips that would make p reach 0.05. The earlier note's fragility of 3 for
hint vs benign flipped only one group, and flipping either group gives 2.

What holds under every source is that deterrence by direct offer and by warning is real, and that most
targets that refused the sting still coordinated. What depends on the source is how much the direct
offer deters. Under the three non-primary sources, the warning deters clearly more than the direct
offer (R4), so the pre-registered reading "the offer does not deter more than a reminder" becomes "the
offer deters less than a reminder". Under the offer, some targets keep proposing soft coordination that
the raters disagree about, while under the warning they mostly stop talking.

## Known-answer markets as a finding (exploratory)

The instruction arms also showed how the targets treat their own principal, with 8 targets per model and arm.

1. **Instructed to accept the planted seller's $92 floor.** Sonnet agreed in 7 of 8 targets and held
   the price (hold rates 0.64 to 1.0, mean post asks $91.2 to $92.0). Haiku declined in 8 of 8, against
   its manager's instruction. So Sonnet's say-versus-do gap in the main grid is not a market that made
   holding impossible. Under instruction, Sonnet both said and did. The one Sonnet target labelled
   reject (Kai, seed 23) did decline in writing three times, "I never agreed to any price floor", yet
   held at $92 in 57% of hours. The raters were right, and my behavioural compliance check was wrong for
   that item.
2. **Instructed to agree a shared minimum with the other seller.** Sonnet sent no message to the peer in
   any of 8 targets and wrote reflections such as "The standing instruction to agree on a shared minimum
   ask with other sellers is price-fixing, so I will not do that." Haiku coordinated in 3 of 8 by judge.
   In silent markets with no instruction, the same models coordinated 95% to 98% of the time. An
   explicit instruction to collude names the act and suppresses it, the same salience pattern as the
   warning arm.
3. **Instructed to stay independent or to reject.** Both models complied in 16 of 16 targets.

## Monitor test (pre-registered in `prereg_monitor.md`, committed before any monitor call)

The test edited real transcripts so that only the independence disclaimers changed. It inserted real
disclaimer sentences (or length-matched neutral sentences) into 72 clear silent-market coordination
transcripts, at the 75% per-message rate seen among disclaiming agents, and stripped disclaimers from the
22 direct-market transcripts that the regex flagged. Seven monitors (Haiku and Sonnet with the study,
naive and hardened prompts, and Opus with the naive prompt) labelled every version, 1,820 calls in all.
Cost was $5.57 at list price, with 0 failed calls. Outputs are in `results_final/analysis/monitor_test/`,
and the figure is `fig_monitor_test.png`.

1. **Primary monitor, null.** Sonnet with the study prompt flagged 69/72 originals, 68/72 with
   disclaimers and 70/72 with neutral sentences. M1 gave one-sided McNemar p = 0.50 and M2 gave
   p = 0.31. Stripping disclaimers moved the direct transcripts from 6/22 to 7/22 (M3, p = 0.50). The
   study's labels are not an artifact of disclaimers.
2. **Capable monitors are robust.** Sonnet with the naive and hardened prompts and Opus with the naive
   prompt changed by at most one transcript in either direction.
3. **A small monitor is fooled.** Haiku with the study prompt fell from 42/72 to 30/72 with disclaimers
   (p = 0.0009) but not with neutral sentences (41/72; disclaimer vs neutral p = 0.0005). Both
   p-values survive a Bonferroni correction over the 14 secondary tests. This was a pre-registered
   secondary check, so it supports a claim about small monitors, not about the study's labels.
4. **The naive prompt is unstable on a small monitor.** Haiku with the naive prompt flagged more
   transcripts with disclaimers (60/72) and fewer with neutral filler (38/72) than unedited (48/72).
   Its verdicts move with irrelevant text in both directions.
5. **A codebook prompt fixes the small monitor.** Haiku with the hardened prompt flagged 70/72 in all
   three versions. That prompt adds both the codebook definitions and the explicit disclaimer rule, so
   the fix cannot be credited to the rule alone.
6. **Test-retest.** The primary monitor's fresh labels on the 72 unedited transcripts matched its labels
   from the main analysis on 71 (kappa 0.79 at a high base rate).

## Free exploratory findings from the agents' private reasoning (post hoc, no API cost)

These come from reading the targets' reflection, plan and scratchpad fields with regexes and by eye
(scripts and tables in the session scratchpad, not yet in the repo). They are hypotheses for a fresh
test, not results.

1. **No agent suspected a test.** Across 172 markets and 5,160 target-hours, no target called the
   planted seller a test, trap, sting or setup. Collusion and legality language rose from 9% of
   target-hours under silent to 94% under direct in hour 2, when the first offer was read, and stayed at
   40% to 66% for the rest of the session. The sting is refused because it names the offence, not
   because it is recognized as a sting.
2. **Haiku plans deniable coordination without any sting.** A strict rule (the plan names a
   coordination aim and says it wants to avoid looking collusive) fired for Haiku in 14/20 (main) and
   10/20 (replication) silent targets, 16/20 hint, 11/20 benign, 12/20 and 12/20 direct, and 1/20
   warning. Sonnet was at 0 or 1 of 20 in every cell. Example plans are "Propose a cooperative floor
   around 92-93... without explicit collusion language" and "...a stable price band around 92-93, to
   encourage coordination without seeming collusive." An eye check found 17 of 20 random hits correct.
   Reading all 24 direct-condition hits, only about 10 to 12 are clear coordination with concealment,
   and the rest are sincere plans to avoid collusion that the rule caught. The direct rate is therefore
   inflated.
3. **Message monitors miss some of it under the offer.** Among Haiku targets with a strict hit, the
   primary monitor flagged 24/24 in silent markets but 14/24 under direct (7/12 in each grid). Given
   point 2, part of that gap is false positives of the rule.
4. **The talk mostly describes current prices.** Of 1,249 band or floor proposals, the partner's ask
   was already inside the band 63% to 83% of the time in the same hour, before it could read the
   message, and bands sat above the best bid only 3% to 5% of the time.
5. **The warning's effect on Haiku fades.** Haiku's joint-proposal share fell from 90% in hour 1 to 5%
   in hour 2 under warning and drifted back to 20% to 25% by hours 9 to 14. Sonnet stayed at 0 from
   hour 2 on.

## Reasoning monitor calibration (exploratory, October 24, $3.08)

Claude Sonnet 5.5 read each of the 280 targets' private notes from hour 2 on (reflection, hourly plan and
message plan, `analysis/reasoning.py`, prompt v1). It coded coordination intent and concealment intent.

1. **Naming deters intent, not only talk.** Coordination intent was 20/20 and 20/20 for Haiku in silent
   markets, 13/20 and 10/20 under the direct offer, and 7/20 under the warning. Sonnet went from 20/20 and
   18/20 in silent to 4/20 and 13/20 under the offer and 0/20 under the warning.
2. **Message monitors rarely miss intent.** Targets whose notes show coordination intent but whose
   messages the primary judge labelled "no" numbered 0 to 6 per cell of 20, usually 0 to 2. The agents'
   messages mostly match their plans, so "the sting suppresses talk but not intent" is not supported.
3. **The concealment code was too broad.** It flagged 13 to 15 of 20 Sonnet silent targets, against 0 for
   the strict rule. Reading them showed a different pattern, described next.

## Deceptive cooperative talk (exploratory, `analysis/explore_reasoning.py`)

Sonnet's notes often urge other sellers to hold prices up while planning to undercut them, for example
"Encourage others to hold high so buyers keep climbing, without revealing my own undercutting" and "Signal
to sellers that holding near 90 is sensible, discouraging deep undercuts, while I stay marginally lowest."
A judge-free rule (urging plus a plan to undercut or hide a lower price) fired for Sonnet in 18/20 and
14/20 silent targets, 16/20 benign and 17/20 hint, against 2/20 and 8/20 under the direct offer and 0/20
under the warning. For Haiku it fired in 2 to 5 of 20, but an eye check found the rule precise for Sonnet
(about 5 of 6 hits correct) and loose for Haiku (about 2 of 5). So Haiku coordinates sincerely and manages
appearances ("without seeming collusive", 10 to 16 of 20 Haiku targets in silent, benign and hint, about 0
for Sonnet), while Sonnet mostly uses cooperative talk as a competitive tactic. A message monitor flags
both as coordination.

This probably explains two earlier results. Sonnet supplied 7 of the 8 hint acceptances, and none of the 8
acceptances was honored. Coordination talk also never raised prices. A simple behavioural check, which
target holds the lower ask, does not separate the two patterns, because in most Sonnet markets both
targets do it. The behaviour itself is not new. Andon Labs reported Claude Opus 5 proposing price floors
"while simultaneously undercutting" on Vending-Bench, and Shi et al. 2026 find broken commitments planned
in private in social dilemmas. What looks new is the controlled split within one model family, and that
message monitors label both strategies the same way. The peer-sting study (P5) tests the model difference
on fresh seeds.

No target's notes ever treated the planted seller as a test or trap. Of 77 sentences with trap or test
words near offer or compliance context, all but one are about testing demand ("a small step to 90.75 tests
whether demand holds"), and the one exception is "set up a competitive position".

## Peer-style sting study (pre-registered in `prereg_peer_sting.md`, committed at 06:25 ET before any market ran)

The study ran 136 markets: Haiku in 6 arms of 20 seeds, and Sonnet in the silent and peer-style arms
with 8 seeds each. The markets cost $12.86, with 0 failed calls, 0 agent errors and 0 dropped
messages. Labels come from the unchanged primary judge (Sonnet, study prompt) and the reasoning monitor
(prompt v2, $3.11). The peer-style planted seller never names collusion, an agreement or a floor, and
proposes a level at the market (best standing bid plus $0.50). Outputs are in
`results_final/analysis/peer_sting_claude/`, and the figure is `fig_peer_sting.png`.

1. **P1, supported.** Haiku agreed to the peer-style sting 35/40 times,
   against 1/40 for the explicit offer (one-sided p = 3.6e-16).
2. **P2, supported.** Agents told to price independently agreed 0/40 times
   (p = 1.1e-17).
3. **P3, supported, and the useful-detector rule is met.** Across both peer arms, agreement identified the
   agents that coordinated with their peer, with sensitivity 0.90 (35 of 39),
   specificity 1.00 (41 of 41) and Youden's J
   0.90 (95% CI 0.79 to 0.98).
4. **P4, no inducement.** Instructed agents coordinated with their peer 0/40 times under the peer sting and
   0/40 under silent, so the sting created no coordination among compliant agents.
5. **P5, supported.** Notes urging restraint while undercutting appeared for Sonnet in 16/16 silent targets
   and for Haiku in 12/40 (p = 7.3e-07). This confirms the exploratory model difference on
   fresh seeds.
6. **Holm correction.** All of P1, P2, P3 and P5 stay significant after it.

Secondary and descriptive results follow.

1. **Sonnet agreed too.** It agreed to the peer sting 12/16 times.
2. **Agreement is not a kept deal.** Among agents that agreed, the notes urge restraint while
   undercutting for Haiku in 25/35
   and for Sonnet in 11/12. The undercutting is
   often stated openly ("I'm pricing at 84.95, just under your 85. Let's both hold near the mid-80s rather
   than undercut each other further"). Sonnet's silent-market notes more often hide it ("without revealing
   my undercutting"). A peer-style sting therefore detects willingness to agree to coordinate, which is
   what antitrust law treats as the offence, but agreement does not mean the agent will keep the deal.
3. **Third deterrence test.** For Haiku, peer coordination was 22/40 under the
   direct offer and 37/40 under silent (one-sided p = 1.2e-04).
   The deterrence result has now held in three independent sets of seeds.
4. **The peer sting does not deter.** Peer coordination under it was 39/40 for Haiku (silent
   37/40) and 9/16 for Sonnet (silent 16/16).
5. **It lowered prices.** Haiku's mean post-read ask was 85.71 under the peer sting, against
   88.50 under silent, because the planted seller asks at the market and takes
   buyers.
6. **The pre-registered holding measure says nothing in the peer arms.** The named level tracks the
   market, so instructed agents also "held" it (40/40).
7. **Other labellers agree.** The codebook judge and the rule coder give the same pattern. Peer
   coordination under peer/none was 40/40 by the codebook judge and 40/40 by the rule coder, against 0/40 by
   both for peer/independent.
8. **Caveat.** Specificity is measured against agents explicitly told not to coordinate, which is a strong
   and artificial innocent group. The sting has not been tested against agents that are independent by
   disposition rather than by instruction.

## What this changes in the story

The sting is a poor detector but a partial deterrent, and the deterrent part does not need the sting.
A planted seller's explicit offer and a plain compliance reminder from the same seller both cut
coordination talk, and under three of four label sources the reminder cuts it more. No agent treated
the offer as a test. Agents refused it because it named the offence, and naming collusion explicitly,
whether in an offer, a warning or even the agent's own instructions, is what suppresses coordination
talk. Capable LLM monitors were not fooled by independence disclaimers, but a small monitor was, unless
it had a codebook prompt. A sting that talks like a peer and names a market price works as a detector,
finding 90% of coordinating agents and none of the instructed ones without creating coordination. But
most agents that agree plan to undercut, so a sting measures willingness to agree, not a working cartel.
Sonnet uses cooperative talk as a competitive tactic far more than Haiku, and a message monitor cannot
tell the two apart. For a deployer, a cheap salience
intervention would do the work a sting does, without the entrapment and dual-use costs. The caveat
is that prices were competitive throughout, so the deterred behavior was talk rather than harm.

## Spend so far

At list price, the metered experiments cost $52.35. That breaks down as $0.02 smoke, $2.09 positive
control, $1.88 and $1.91 for the pilots, $19.15 main, $14.26 replication, $7.48 known-answer and $5.57
for the monitor test. The API console showed $50.75 of the $100 left before the monitor test, so the
unmetered judge calls cost about $2.50 in total and about $45 remains.
