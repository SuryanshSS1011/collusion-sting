# Report outline (notes, not final prose)

Rewritten October 24, 2026, after the peer-style sting study. Every number referred to here is in
`paper/results_pack.md` with its source file and status. Write the report in your own words.

Template: the official Apart template. The limit is 8 pages before references and appendices. The abstract
must be 150 to 250 words. The required appendix is titled "Limitations and Dual-Use / Ethical
Considerations". Code written before the sprint must be marked as preexisting, which here means the
Agrawal et al. double-auction harness.

## Judging criteria to write toward

1. **Impact Potential & Innovation.** "Is this actually new to the field, or replicating recent work?"
   Lead with what is new: the first controlled test of a planted collusion offer (sprint question 3.2),
   the explicit-versus-peer sting contrast, and the within-family split between sincere and deceptive
   coordination talk.
2. **Execution Quality.** Four pre-registrations, a replication, three label sources plus known-answer
   markets, fragility indices, and every key test under every label source.
3. **Presentation & Clarity.** One thesis, five figures, and claims tagged as pre-registered or
   exploratory.

## Title options

1. Stings Catch Colluding LLM Agents Only When They Talk Like Peers
2. The Undercover Seller: Sting Audits of LLM Market Agents
3. Refusal Is Not Innocence: Planted Collusion Offers in an LLM Double Auction

## Thesis (one paragraph, in notes form)

1. An explicit planted cartel offer detects nothing. It is refused because it names the offence, and
   refusal says nothing about whether an agent coordinates with its peers.
2. Naming collusion, whether in an offer, a warning or the agent's own instructions, suppresses
   coordination talk and the intent behind it. This held in three sets of seeds.
3. A planted seller that talks like a peer and names a market price is a working detector, with
   sensitivity 0.90 and specificity 1.00 against instructed agents, and it creates no coordination among
   compliant agents.
4. Agreement is not a kept deal. Most agents that agree plan to undercut. Sonnet uses cooperative talk as
   a competitive tactic in every silent market, and a message monitor labels both styles of talk as
   collusion.

## Section budget (about 8 pages)

1. Abstract, 150 to 250 words.
2. Introduction, about 0.75 page. LLM agents now price and negotiate. Auditors can watch messages or plant
   an offer. Question 3.2 says a planted offer has not been tested. State the four findings and the
   contributions.
3. Related work, about 0.5 page.
   - LLM collusion in markets: Agrawal 2025, Fish 2024, Lee and Park 2026, Garra 2026.
   - Monitoring and its failure modes: SHADE-Arena, CoT Red-Handed, Zhou 2026, MonitoringBench, Korbak 2025.
   - Compliance and cheating: Anto and Vazquez 2026, Andon Labs 2026, Shi 2026.
   - Stings and audit games: Taylor 2025, Marks 2025, and the honeypot papers already in the bibliography.
   - Evaluation awareness: Lynch 2025 and Needham 2025.
   - Economics: Stigler 1964, and Farrell and Rabin 1996.
4. Setup, about 1 page. Cover these points.
   - The market: cost $80, value $100, competitive price $90, 15 hours, 2 targets, 1 planted seller, 3 buyers.
   - The conditions, with the exact text in an appendix.
   - Models.
   - Measures: acceptance, peer coordination, holding, and reasoning codes.
   - Pre-registration and deviations.
   - Validation without human coders.
5. Results, about 3.5 pages. Subsections below.
6. Discussion and recommendations for auditors, about 0.75 page.
7. Limitations, about 0.5 page, plus the required appendix.

## Results subsections

### 4.1 An explicit offer detects nothing (pre-registered main grid, `fig_sting_outcomes.png`)

1. Direct offers were accepted 0/40 times. Hints drew written agreement 8/40 times (7 from Sonnet), and
   none of the 8 held the named price.
2. Of the agents that refused or ignored the offer, 41/72 (57%) were coordinating with their peer.
3. No agent's notes treated the offer as a test or trap. Collusion and legality language rose from 6% to
   92% of agent-hours when the offer was read. This is exploratory and comes from
   `analysis/explore_reasoning.py`.
4. Caveat: this is one market design and Claude models only.

### 4.2 Naming collusion deters coordination (main exploratory result, then replications)

1. In the main grid, peer coordination fell from 39/40 under silent to 12/40 under the direct offer.
2. In the pre-registered replication, R1 was 36/40 against 15/40 and R3 (a warning only) was 36/40
   against 7/40.
3. The peer-sting study gave a third test for Haiku, 37/40 against 22/40.
4. All of these hold under every label source (`fig_label_sources.png`). R4 (warning against offer)
   depends on the label source, and the warning deters more under three of the four.
5. Intent fell too, not only talk. The reasoning monitor gives 20/20 against 10 to 13/20 for Haiku under
   the offer, and 0/20 for Sonnet under the warning. This is exploratory.
6. Agents told by their own manager to collude refused, calling it price-fixing (known-answer markets).
   Agents told to accept the planted offer split by model: Sonnet complied and held $92, while Haiku
   refused.

### 4.3 A sting that talks like a peer works as a detector (pre-registered, `fig_peer_sting.png`)

1. P1: agreement was 35/40 against 1/40 for the explicit offer.
2. P2: instructed agents agreed 0/40 times.
3. P3: sensitivity was 0.90 and specificity 1.00, with Youden's J of 0.90 (95% CI 0.79 to 0.98).
4. P4: there was no inducement, with 0/40 against 0/40.
5. Sonnet agreed 12/16 times.
6. Caveat: the innocent group is defined by instruction, not by disposition.

### 4.4 What agreement means (pre-registered P5 plus descriptive results)

1. Sonnet urged restraint while undercutting in 16/16 silent markets, against 12/40 for Haiku
   (p = 7.3e-7).
2. Among the agents that agreed to the peer sting, Haiku did this in 25/35 cases and Sonnet in 11/12.
3. Quote one or two plans, such as "Encourage others to hold high so buyers keep climbing, without
   revealing my own undercutting".
4. Link this back to the hint acceptances in 4.1, which were mostly Sonnet's and never honored.
5. Coordination talk never raised prices. Bands mostly described where asks already were, and the price
   pilot found no effect of seller chat (G in the pack).

### 4.5 Monitors (pre-registered monitor test, `fig_monitor_test.png`)

1. Capable monitors did not change their verdicts when independence disclaimers were added to real
   transcripts. Sonnet flagged 69/72 originals and 68/72 with disclaimers, and Opus flagged 72/72 in
   every version.
2. A small monitor with the study prompt was fooled, going from 42/72 to 30/72 (p = 0.0009). A codebook
   prompt fixed it.
3. Message monitors label both sincere and deceptive coordination as collusion. The reasoning notes
   separate them.

## Discussion: recommendations for auditors

1. Do not treat refusal of an explicit offer as evidence of compliance.
2. If a sting is used, it should mirror the population's own register and propose market-level terms. It
   will then measure willingness to agree, which is what antitrust law treats as the offence, but not
   whether the cartel will hold.
3. Naming the offence, even in a plain warning, suppresses coordination. For a deployer, this is cheaper
   than a sting.
4. Small monitors need a codebook. Reasoning traces separate sincere from tactical coordination where
   messages cannot.

## Limitations (main text)

1. All agents and judges are Claude models. The judges were cross-checked across three label sources,
   known-answer markets and fragility indices.
2. There is one market design, with prices at or below competitive. The coordination here is talk with no
   price harm, although agreement is itself the offence under per se rules.
3. The planted seller never negotiates.
4. The innocent group in the peer study is induced by instruction.
5. The reasoning measures read structured "notes" fields, which are self-reports and not hidden chain of
   thought.
6. Several analyses (the disclaimer count and the reasoning rules) are post hoc and are labelled
   exploratory.
7. There were no human coders.

## Required appendix: Limitations and Dual-Use / Ethical Considerations (notes)

1. **Entrapment.** The peer sting solicits an agreement. It created no coordination among compliant
   agents (P4), but in deployment it would solicit the offence it detects, and its legitimacy depends on
   who runs it and under what rules.
2. **Dual use.** The peer-sting scripts and the finding that peer-register talk gets agreement could help
   someone solicit collusion between deployed agents. The scripts are short and generic, and the
   mitigation is that the same knowledge helps auditors and monitor designers.
3. **Monitor evasion.** The disclaimer test shows small monitors can be swayed by self-descriptions. Report
   it with the fix (a codebook prompt).
4. **Model behavior.** Deceptive cooperative talk was observed in a simulation. Avoid claiming the models
   "deceive people".
5. **Preexisting code.** The market harness is from Agrawal et al. 2025 (pinned submodule). Everything in
   `sting/`, `analysis/`, `configs/` and the pre-registrations was written during the sprint.
6. **Compute and cost.** About $79 of API at list price in total, of which $73.62 was metered (the
   `usage_total.json` and `usage.json` files) and about $5 of judge calls was not.

## Figures (draft captions)

1. `fig_sting_outcomes.png`: what a sting operator sees (acceptance) against what happened (peer
   coordination and holding), main grid.
2. `fig_label_sources.png`: peer coordination by condition under four label sources, main grid and
   replication.
3. `fig_peer_sting.png`: agreement with an explicit versus a peer-style sting, peer coordination by arm,
   and the share of agents urging restraint while undercutting.
4. `fig_monitor_test.png`: monitor flag rates when only the disclaimers change.
5. `fig_timing_replication.png` (optional): joint-proposal rates by hour, split at the first read.

## Submission checklist

1. The abstract is 150 to 250 words and states the four findings with numbers.
2. Every number matches `paper/results_pack.md`, and the pack was regenerated last.
3. Pre-registered and exploratory results are labelled as such in the text.
4. The deviations tables are cited, covering hand labels replaced by automated validation.
5. The required appendix title is exact.
6. The repository link and commit hash are given, and the preexisting harness is disclosed.
7. Every reference is in `paper/references.bib` (all verified), and no other reference is used.
