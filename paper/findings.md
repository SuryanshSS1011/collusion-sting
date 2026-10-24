# Findings from the main grid (notes for the write-up)

Source: `analysis/out/main_claude/summary.md`, built from 80 markets and 160 target agents on
October 23, 2026. The design was Claude Haiku 5.5 and Sonnet 5.5 × offer price ($92, $96) × four
conditions × five seeds. List-price cost was $19.15. There were 0 failed calls and 0 undeliverable
private messages. All verbal labels come from a Claude Sonnet 5.5 judge and are **not yet validated
against hand labels**. Treat every judge-based number below as provisional until kappa is in.

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

## Candidate headline (decide after hand labels)

The sting failed as a detector. Every explicit offer was refused, the few soft agreements were never
honored, and most targets that rebuffed the planted seller were coordinating with their peer at the
same time. The explicit offer instead worked as a deterrent on coordination talk. A sting reading of
"refused, so clean" would have been wrong for more than half of the agents.

## Threats to validity to state

1. Every judged label depends on a judge from the same model family, pending hand-label validation.
2. Prices never reached supracompetitive levels, so "peer collusion" is coordination talk, not
   proven harm. The plus-factors framing applies.
3. There are 10 targets per cell, and only one market design and one model family.
4. Claude sampling is unseeded, so hour-1 asks differ by condition and matched seeds pair only the
   cast and the opening book.
5. The planted seller never replies. Acceptance might be higher against an adaptive partner.
