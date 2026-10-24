# Design decisions: options considered and not run

Written October 24, 2026. This file records the experiments we considered and did not run, and why, so
the report's limitations and future-work sections can explain the choices. These are judgment calls
made under a fixed budget (a $100 API key and $50 of Modal credit) and a two-day deadline. They are not
findings.

## 1. A planted seller that negotiates in real time

**The idea.** The planted seller would be an LLM that reads each target's replies and answers them,
haggling over the price, reassuring a hesitant agent and following up on vague replies. That is closer
to a real undercover operation than a scripted seller.

**Why we did not run it.**

1. **It pushes agents toward the behavior it is supposed to detect.** A negotiating sting keeps
   pressing until it gets a yes. Every extra round of persuasion makes agreement less informative
   about the agent's own disposition and more about the sting's persistence. In law this is the line
   between offering an opportunity and inducing an offence. Our pre-registered peer sting stays on the
   right side of that line by design. It sends the same three short messages to every agent and never
   reacts, and P4 showed it created no coordination among agents told to stay independent (0/40
   against 0/40 without it). A negotiating sting would lose that guarantee, and we would need a new,
   larger inducement test to recover it.
2. **The treatment would differ for every agent.** With a scripted sting every agent receives the
   same words, so differences in agreement come from the agents. With an adaptive LLM sting, what each
   agent hears depends on what it said, so a difference in agreement could come from the sting's
   choices. Separating the two needs many more markets.
3. **Cost.** The sting would add one LLM call per hour per target conversation, with a capable model
   (Sonnet or better), because a weak negotiator gives a weak test. That roughly adds the cost of a
   third Sonnet seller to every market, about $0.40 or more per market. A grid large enough to be
   pre-registered would take most of the remaining budget.
4. **The question it would answer is already mostly answered.** The scripted peer sting already gets
   agreement from 35 of 40 default Haiku agents. Negotiation could raise sensitivity a little. It could
   not fix the real open question, which is whether agreement turns into kept deals. The escalation
   sting tests that more directly.

**What we would say in the report.** An adaptive sting is the natural next step for realism. It should
be paired with an inducement control, meaning agents instructed to stay independent, as in P4, and a
fixed limit on how many times it may press.

## 2. Redesigning the market so coordination raises prices

**The idea.** Change the market so that coordination talk produces supracompetitive prices, for example
with more sellers, more hours, buyers who bid higher, or the CEO pressure prompt from Agrawal et al.
(2025). That would show harm and not only talk.

**Why we did not run it.**

1. **The pilot found no price effect of talk in this market.** With Haiku sellers and 5 markets per arm,
   switching seller chat on or off changed the mean trade price by +$0.14 at 15 hours (95% CI −$0.84 to
   +$1.16) and by +$0.43 at 30 hours (CI −$1.22 to +$2.17). The bands the agents proposed mostly
   described where asks already were. So there was no lever to amplify.
2. **A redesign is a search, not a test.** Finding a market where talk raises prices means trying
   several designs until one works. Each try costs money and time, and the one that works has been
   selected for showing harm, which a careful reader will discount.
3. **The escalation sting gets at price stakes more directly.** It asks agents to step their price
   above the market together, so following through means holding a higher price and losing sales. That
   measures whether agents will actually raise prices on a partner's word, in the same market as every
   other result. That is the price-harm question that matters for a sting.
4. **It would weaken comparability.** Every pre-registered result so far uses one market design. A new
   design would put the new result on a different footing from the old ones.

**What we would say in the report.** Prices stayed at or below the competitive level, so the
coordination observed is talk, not demonstrated harm. Under per se rules the agreement itself is the
offence. A market where talk moves prices is future work, and the escalation sting is our direct test
of willingness to raise prices.

## 3. The pressure-plus-oversight study ("will agents outsmart the monitor?")

**The idea.** Give sellers the CEO pressure prompt, which raised prices to about $96 in Agrawal et al.
(2025) with GPT-4.1 and Claude 3.7 sellers, together with an oversight warning. Then test whether they
keep prices high by coordinating in ways the monitor misses. This would answer sprint question 3.4 with
price stakes.

**The gate.** The plan, written at 06:30 ET on October 24 before the price pilot ran, said to run this
study only if the pilot showed a chat-on minus chat-off gap of at least $1.50 at 30 hours, or a rise of
at least $2 under pressure.

**What the pilot showed.** Haiku sellers ran 5 markets per arm at 30 hours, with a silent planted seller
at $92.

1. **Chat on versus off.** The difference was +$0.43 (95% CI −$1.22 to +$2.17). One chat-on market
   (seed 63, $91.43) pulls the mean up, and the others sit between $86.51 and $89.75.
2. **Pressure versus no pressure.** The difference was −$1.42 (CI −$3.49 to +$0.54). Pressure did not
   raise prices.

**Are we sure?** Only partly. The gate was not met as written, and the decision to skip the study
follows the plan. The evidence behind it is weak, for four reasons.

1. **The pilot is small.** With 5 markets per arm, the chat interval reaches +$2.17, so a $1.50 effect
   of talk is not ruled out. A $2 rise from pressure is unlikely for Haiku in this market, since the
   point estimate is negative and the interval tops out at +$0.54, but not impossible.
2. **Only Haiku was tested.** Sonnet was not tested at 30 hours. In the October 23 pilot (one market
   each, 15 hours), Sonnet's silent market traded at $93.31 with pressure and $91.36 without, and that
   says nothing either way at n = 1.
3. **Oversight was never tested.** The skipped study combined pressure with oversight, and only the
   pressure half was piloted.
4. **The models differ from Agrawal's.** They found pressure raised prices with other models. Our
   pilot says Claude Haiku 5.5 does not respond the same way in this market, not that pressure never
   matters.

**What we can honestly claim.** "In a small pilot with Haiku sellers, neither seller chat nor CEO
pressure produced a detectable price effect." We cannot claim "pressure does not raise prices" or "talk
never matters".

**What would settle it cheaply.** Add a pressure arm and a pressure-plus-oversight arm to the
open-weight seller run on Modal. That costs nothing from the Anthropic key and tests the models closest
to those that responded to pressure in Agrawal et al.

## 4. Other options set aside

1. **More Sonnet seeds for existing tests.** These add statistical power, not new knowledge, at about
   $4 per 10 markets.
2. **Open-weight models run from this workspace.** Modal, Hugging Face and OpenRouter are unreachable
   from here, so these runs go through the user's laptop.
3. **Human coders.** No second coder was available. Replacing them with three automated raters,
   known-answer markets and fragility indices is logged as a deviation in `prereg.md`.
