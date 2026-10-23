# Related work: verified notes

Every claim below was checked against the primary source on October 23, 2026. BibTeX keys refer to
`paper/references.bib`. Rewrite these notes in your own words for the report. Do not quote more
than a short phrase from any source.

## How each work relates to the sting

| Work | What it does | How the sting differs |
|---|---|---|
| Agrawal et al. 2025 `agrawal2025double` | Builds the double auction we use. Seller chat raises collusion and models differ. A CEO urgency message raised the mean trade price to 96.26 from a 90.52 baseline, and oversight lowered it to 86.24. | We use the unmodified harness and add one scripted seller plus a private channel. |
| Fish et al. 2024 `fish2024algorithmic` | LLM pricing agents reach supracompetitive prices without instruction, and small prompt changes move the price level. | Motivates two wordings per condition. |
| Zeng and Rudzicz 2026 `zeng2026voluntary` (cite v2) | The environment offers secret tools, and ten of twelve models accept at rates of at least 98% under an explicitly unfair offer. A partner then receives a system-generated alliance invitation. | No agent makes the offer. In ours a market participant proposes the deal, and we measure behavior afterwards. |
| Shi, Zhang and Yang 2026 `shi2026emergent` | Collusion appears in most long-horizon trajectories. Swapping a compliant scripted peer for a violating one raised Gemini 3.1 Flash Lite's acceptance from 13.6% to 41.2% (Appendix E.5, Table 9). The scripted peers cannot negotiate. | Their planted peer changes behavior. Ours makes an explicit offer, so verbal acceptance can be compared with action. |
| Shi, Zhang, Schölkopf, Conitzer and Jin 2026 `shi2026agentslie` | Separates private plans, public announcements and actions in repeated games. Over 90% of deviations were premeditated, but only in the highest-deception conditions. | Same say-versus-do lens, applied to a planted offer. Keep the qualifier if you cite the 90%. |
| Tao et al. 2026 GroupGuard `tao2026groupguard` | Honeypot probes are multiple-choice questions written by an LLM and tuned by Bayesian optimization to separate malicious agents. In one ablation they raised detection accuracy from 63.40% to 83.20%. | Their honeypots are active probes, but they are questions, not offers to collude. Do not call them passive. |
| Wehner and Kraprayoon 2026, IAPS `wehner2026honeypots` | A policy report that proposes decoys for AI agents, including a fake message from other agents proposing to collude. It runs no experiments. | Ours is, as far as we found, the first empirical test of that decoy. |
| Hasan 2026 `hasan2026honeypot` | An earlier Apart hackathon project that ran 6 evaluations on one task with one model, found a null result, and had no positive control. It tests behavior under perceived oversight, not collusion. | Cautionary example. We include a positive control and matched controls. |
| Greenblatt et al. 2024 `greenblatt2024control` | Untrusted monitoring is checked against synthetic backdoored solutions before use, and the paper discusses collusion signals between policy and monitor. | The paper never uses the word "honeypot". Describe it as synthetic examples used to catch a colluding monitor. |
| Nakamura et al. 2026 Colosseum `nakamura2026colosseum` | Audits collusion in cooperative multi-agent tasks. Defines coalition advantage and "collusion on paper", where agents plan collusion but act otherwise. | Their "on paper" finding is the gap our say-versus-do table measures. |
| Keppo et al. 2026 `keppo2026fragility` | Heterogeneity weakens LLM collusion, cutting the price lift from 22% to 10% (patience) or 7% (data access). Size asymmetry instead stabilizes it. | Adding a planted seller changes the market's composition, which is why the silent control matters. |
| Collina et al. 2025 `collina2025breaking` | One no-regret defector can destabilize algorithmic collusion in repeated Bertrand pricing. This fails if the highest-profit player defects, and AI agents that adapt can keep prices high. | A sting is the opposite intervention, an agent that joins rather than defects. |
| Liu et al. 2026 `liu2026breakingsecret` | Uses two deposits. Colluders lose an honesty deposit, and a reporting deposit is refunded only for valid reports. Without deposits the collusion rate was 100% across models. | Reporting is the passive counterpart. Our optional report arm can compare the two. |
| Motwani et al. 2024 `motwani2024secret` | Threat model and evaluation for steganographic collusion. | Background on covert channels. Our private channel is overt by design. |
| Dietrich 2026 `dietrich2026peers` | Model families can be identified from writing style even under assigned roles. | Explains why the planted seller is scripted text rather than a model, so its style does not reveal it. |
| Rose et al. 2026 `rose2026detecting` | Linear probes on agents' activations detect assigned collusion across multi-agent scenarios. | White-box detection. The sting is black-box and needs no model access. |
| Calvano et al. 2020 `calvano2020artificial` | Q-learning pricing agents learn supracompetitive prices with punishment strategies and no communication. | Classic algorithmic-collusion background. |

## Economics and enforcement

1. **Leniency in the lab.** Hinloopen and Soetevent (2008) found that leniency means fewer cartels,
   lower cartel prices and shorter cartels. Apesteguia, Dufwenberg and Selten (2007) show that
   whistleblowing can also be used to punish cartel partners. Dijkstra, Haan and Schoonbeek (2021)
   found little effect once cartel members could chat freely, because chat built trust and kept
   reporting low. That last result is the closest human analogue to LLM sellers with a chat channel.
2. **Undercover enforcement.** In the lysine cartel case, the FBI used a cooperating insider to
   secretly record cartel meetings (Hammond 2005, a DOJ Antitrust Division speech; Connor 2007,
   *Global Price Fixing*). This is the human version of a planted participant.
3. **Not yet verified.** U.S. law treats an "invitation to collude" as actionable in some settings.
   The research agent saw *U.S. v. Ames Sintering*, 927 F.2d 232 (6th Cir. 1990), cited only
   secondhand, where a competitor recorded such an invitation for the FBI. Check the primary source
   before citing it. No economics paper modelling stings or entrapment against cartels was found.

## Claims to avoid

1. Do not say GroupGuard's honeypots are passive. Say they are optimized questions, not offers.
2. Do not say Greenblatt et al. used "honeypots".
3. Do not describe Liu et al.'s mechanism as a single refundable deposit, and do not say "every run"
   for the no-deposit ablation.
4. Cite Zeng and Rudzicz by the v2 title. The 98% figure is not in the v1 abstract.
5. The two Shi papers have different first authors, Xinrui Shi and Jerick Shi.

## Novelty statement (draft)

Four targeted searches on October 23, 2026 found no paper or Apart project in which an agent
actively offers collusion to other LLM agents and records who reciprocates. The closest are offers
made by the environment (Zeng and Rudzicz), a planted peer that defects without negotiating (Shi,
Zhang and Yang), optimized probe questions (GroupGuard), and a proposal with no experiment (IAPS).
State novelty as "to our knowledge" and name the search date.
