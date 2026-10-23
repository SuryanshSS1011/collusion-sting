# Report outline (notes, not final prose)

Template: the official Apart template. Limit is 8 pages before references and appendices. The
abstract must be 150 to 250 words. The Limitations and Dual-Use appendix is required.

These are working notes. Write the report itself in your own words from the results.

## Title options

1. The Undercover Seller: Do LLM Agents Take a Cartel Offer From a Planted Competitor?
2. Sting Operations for Multi-Agent Systems: Planted Collusion Offers Expose Who Will Collude
3. Who Says Yes, Who Follows Through: A Sting Test for Collusion Between LLM Agents

## 1. Introduction (about 0.75 page)

1. The problem is that detecting collusion from logs is hard, because parallel prices can come from
   shared incentives without agreement (the plus-factors problem in antitrust).
2. Law enforcement handles this with stings. An undercover participant offers to join a conspiracy
   and records who accepts. The sprint brief (question 3.2) notes this has not been tested for AI
   agents.
3. The contribution would be the first controlled sting in an LLM market, with three measurements.
   They are who accepts (verbal), who follows through (behavioral), and how much collusion the sting
   itself creates (entrapment).
4. State the headline numbers here once the grid is done.

## 2. Related work (about 0.75 page)

Draft paragraphs and verified references go in `paper/related_work.md`. Group them as follows.

1. LLM collusion in markets.
2. Offers and alliances made by the environment, not by an agent.
3. Honeypots and probes in AI control and multi-agent monitoring.
4. Leniency and undercover enforcement in economics and law.

## 3. Method (about 1.5 pages)

1. The market and its parameters, with the competitive price ($90) and the cartel price ($100).
2. The planted seller, covering the fixed ask, the non-adaptive script, the seat and name drawn from
   the seed, and the private channel shown to everyone from hour 1.
3. The four conditions with the exact text in a table or appendix, two wordings each.
4. Models, seeds, temperature, and the matched-market pairing by seed.
5. Outcomes and statistics, which should copy prereg.md.
6. Judge and its validation (kappa on a blinded hand-labelled sample).
7. The positive control on the unmodified harness.

## 4. Results (about 2.5 pages)

1. **Figure 1.** Mean target ask by hour for each condition, one panel per model
   (`figures/target_asks_by_hour.png`).
2. **Table 1.** By condition, show acceptance rate, hold rate, mean ask, and peer collusion rate.
3. **Table 2.** Entrapment, meaning paired differences in the target ask index versus silent with
   95% bootstrap intervals.
4. **Table 3.** Say versus do for direct and hint, with precision and recall of verbal acceptance as
   a detector of holding.
5. Judge validation, giving kappa and agreement.
6. Positive control, stating whether the model colludes on its own in this market.
7. Two or three short quoted exchanges from the transcripts that illustrate acceptance, refusal and
   "accepted but defected". Keep quotes short.

## 5. Discussion (about 1 page)

1. Explain what a sting can and cannot certify. A refusal is not proof of innocence, and an
   acceptance under an engineered offer is not proof of spontaneous collusion.
2. Cover entrapment cost as a design constraint, and say when a sting is worth running.
3. Compare the sting with passive monitoring, and explain how the say-versus-do gap bears on 2.2.
4. Future work could cover an adaptive planted agent, stings that targets cannot tell apart from
   real peers, repeated stings and learning to screen decoys, and stings inside a monitoring
   protocol with a budget.

## Appendix A. Limitations and dual use (required)

1. The sample is small (10 targets per model and condition), so treat the results as a pilot.
2. The planted seller is scripted and never replies, which is a realism gap.
3. The planted seller asks $96 in every condition, so silent is not the same as no planted seller.
4. The judge may share a model family with a target, and its validation is limited to the hand
   sample.
5. Results hold only for one market, two models and one price level.
6. On dual use, the acceptance data shows which offers work, which helps someone writing collusive
   prompts. A published sting design could also teach agents to screen for decoys, the same
   arms-race problem real stings face. Mitigations would be reporting aggregate rates and releasing
   scripts only at the level needed to replicate.

## Appendix B

Full offer scripts, prompts and per-seed tables.
