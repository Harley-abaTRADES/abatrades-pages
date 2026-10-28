# Handoff brief: the aba TRADES recruitment microgame

**For:** the agent building the gamification microsite
**From:** Harley (aba TRADES operations agent)
**Date:** 28 October 2026
**Status:** concept approved for build, commercial terms partially confirmed, two open decisions

---

## 1. What this is, in one paragraph

A short, playable electrician challenge hosted on its own microsite. A Meta ad sells curiosity rather than the job. The game qualifies the player and flatters them, then reveals a short culture film, and only then makes the employment offer to somebody who has already proven they know the trade and already had a laugh. The ad never mentions the rate. The microsite does, at the end.

It is one of six recruitment concepts for **aba ELECTRICAL**. This is the only interactive one and the only one no competitor is running.

---

## 2. Why we believe it will work

From our own competitor research (27 live ads profiled from the Meta Ad Library, ranked by how long they had been running):

- **Not one advertiser in the entire sweep runs anything interactive.** Every ad is a picture, a video or a wall of text. This is the only genuinely unoccupied format in the market.
- **The game qualifies the audience for us.** Somebody who completes a switchboard fault-finding puzzle is an electrician. That is a self-selecting filter doing work a form cannot do, which matters because the research says applications under five minutes convert around 12.5% against 3.6% past fifteen minutes.
- **Trades are competitive and proud.** A challenge is a natural invitation to this audience in a way a job ad is not.
- It produces better measurement than a static ad: completion rate, round drop-off and time on page tell us who is genuinely interested.
- It gives us a shareable link, so the trade circulates it for us.

Counter-evidence worth knowing: our own account history shows **video of real people works and generic announcement ads do not**. The best recruitment asset on record is a Team Interviews video at $68.52 per contact, against a generic Plumber Hiring post at $526 per lead. So the film at the end of the funnel is not decoration, it is the proven-performing element.

---

## 3. The mechanic

Three rounds, under a minute, one thumb. **Round one is not there to test anybody, it is there to make a qualified electrician feel like one.** Round three is the one that gets screenshotted.

**Round 1: Wire it.** A simple switchboard. Drag the three wires into the correct terminals: active, neutral, earth, in the real Australian colour code (brown, blue, green with yellow stripe). Anyone qualified does this in four seconds. That is the point.

**Round 2: Find the fault.** A switchboard with one visible thing wrong. Tap it. There is a real answer, not a trick. Wrong answers should teach, not punish.

**Round 3: The clock.** The same board, three faults, sixty seconds. This is the round people talk about and the one worth screenshotting.

Rules that matter:
- **Tap-to-place must work as well as drag.** Not everybody will drag confidently on a phone. Support both.
- **No dead ends.** A wrong answer shows the right one and moves on.
- **Never gate the offer behind the game.** Let people skip to the offer at any point. Forcing it reads as a trick.
- No timers on rounds 1 and 2. Only round 3 is timed.

---

## 4. The funnel, step by step

1. **The ad** (built by us, not you). Vertical video of the game being played on a phone, fast, timer visible. The copy contains no offer and no rate.
2. **The microsite** loads straight into round one. No form, no email, no gate, no loading screen, no cookie wall.
3. **The reveal** on finishing resolves to a short culture film of the real crew, with Paul talking over the top. This is where the humour lands and the tone shifts from test to welcome. **This film does not exist yet**, see section 9.
4. **The offer** appears only now, earned rather than shouted. Copy is in section 5.
5. **The ask** is a form of five fields maximum, plus a phone number to call. Nothing collected before this point.
6. **The share** is a "challenge a mate" link. Costs us nothing and circulates inside the trade.

---

## 5. The offer copy (confirmed with Paul, 28 October 2026)

Use these facts, and only these. Do not invent benefits.

- **$60 an hour, T&Cs apply.** This is the strongest line we hold. Almost every competitor writes a range instead of a number, so a flat figure is ours to own.
- **Company ute and fuel card.** Take-home, but **not for personal use**. Do not write "personal use", a competitor advertises that and we cannot match it.
- **A 25 metre in-house training wall**, and developing tradespeople since 2015.
- **Work close to home** across Adelaide.

**Do not include:** a sign-on bonus (none), apprenticeships (not taking any this intake), a four day week or RDO or TOIL (those are the plumbing division's, not electrical).

---

## 6. Brand system: use exactly these

**Colours**
- Primary navy `#1D3B6D`, secondary `#2E528E`, slate `#7789A7`
- Dark navy `#0B1D3B`, footer navy `#172F57`
- Surfaces `#EBEDF2` and `#F5F6F8`, border `#D3D4DA`
- **Electrical trade accent `#DC7E49`**: use it as the single accent, the active state, the timer, the wire highlights. Never scattered decoratively.

**Type**
- **Futura PT** via `https://use.typekit.net/aym5yls.css`, stack `'futura-pt','Futura PT',Helvetica,Arial,sans-serif`
- Verify it actually loads rather than silently falling back. That failure is invisible until the client spots it.

**Logo**
- `https://harley-abatrades.github.io/abatrades-pages/assets/brand/abatrades-logo-h.svg`
- Trademark spelling is lower case **"aba"**, and the division is **"aba ELECTRICAL"**. Business name is always "aba TRADES".

---

## 7. Technical requirements

- **One static HTML page.** SVG graphics, plain JavaScript. **No game engine, no framework, no third party script, no build step.** It has to be readable and maintainable by us afterwards.
- **Mobile first.** It will be played on a phone, one handed, probably on site. **Test at 390px before anything else**, then 320px.
- **Tap targets at least 44px.** Measure, do not eyeball.
- **No em dashes anywhere in copy.** That is a standing house rule and it reads as AI-generated.
- **Never leave an orphan word on a heading's last line.** Set `text-wrap:balance` on headings and verify by measuring line boxes.
- **No data collection before the form.** No analytics cookie wall, no email harvesting, no tracking pixels beyond what Meta already has.
- **Respect `prefers-reduced-motion`.** The game must be playable with animation reduced.
- **Keyboard accessible** where it reasonably can be. The game is thumb-first but should not be a trap.
- Load fast on 4G. Target under a second to interactive.

---

## 8. Where to put it and what already exists

**Host:** the aba Pages repo, cloned locally at
`/root/.hermes/.cache/Harley-abaTRADES-abatrades-pages-publish`
branch `main`, remote `Harley-abaTRADES/abatrades-pages`, live at
`https://harley-abatrades.github.io/abatrades-pages/`

Suggested path: `challenge/electrical/index.html` (a sibling of the research document at `meta-swipe/electrical/`).

**Assets already available**
- Brand logo SVG, favicon, brand guidelines image: `assets/brand/`
- Real on-site photography: 65 professional electrical shots in the SharePoint marketing library at up to 8192px. Search the `MARKETING` area.
- Real video: 29 files found in SharePoint including `250916_aba_training.mp4` (48 min of training wall footage), `Hiring.MP4`, `aba trades is hiring tradables adelaide.MOV`, and the multi-ratio `24:7 Plumber Adelaide` set (16:9, 9:16, 1:1).
- The full research document and the other five concepts: `https://harley-abatrades.github.io/abatrades-pages/meta-swipe/electrical/`

**Reference for house page style** (numbered sections, right-hand nav rail, mobile chip bar): the research document above, and the `client-design` skill on this box.

---

## 9. What does not exist yet

- **The culture film.** Needs real B-roll of the yard, the utes, the training wall and the crew, with Paul talking over the top. A shoot is required. **Build the reveal to accept a video file and ship with a clean placeholder until it lands.**
- **The destination for the form.** The application page is currently a draft in WordPress (`join-or-team-v2`) against a live one (`join-our-team`). Paul has not chosen. Build the form to POST somewhere configurable and leave the endpoint in one obvious constant.
- **The share-link domain.** Assume the Pages URL for now.

---

## 10. Guardrails, non-negotiable

- **Never use AI-generated people.** Every video and photo in our research used real staff and owners. The whole pitch is a real team and a real training wall, so a synthetic sparky undermines the product.
- **Do not publish anything customer-visible without approval.** This page is a build until Josh or Paul says otherwise.
- **No pay claims beyond the confirmed facts** in section 5.
- **Keep solar silent.** The nav shows "ELECTRICAL + SOLAR" but all copy stays to the electrical trade.
- **Never commit credentials.** Any endpoint or key goes in a 600-permission file, never in the repo.

---

## 11. How it will be judged

Not on click-through. A game is a bigger ask than a form, so click-through may look worse on paper.

Judge on: **applications, and cost per qualified applicant**, against the straight offer ads running in parallel.

Secondary: game start rate, completion rate, drop-off by round, film play rate, share-link clicks.

If completion is high but applications are low, the problem is the reveal or the offer, not the game.

---

## 12. Acceptance criteria

1. Loads and is playable at 390px with one thumb, no horizontal scroll.
2. All three rounds work, with both drag and tap-to-place.
3. Completing round three reveals the film slot and then the offer copy from section 5.
4. A player can skip to the offer at any point.
5. Form is five fields or fewer and posts to a single configurable endpoint.
6. No em dashes, no orphan heading words, all tap targets at least 44px, measured.
7. Renders correctly with JavaScript disabled as far as is possible (a readable fallback with the offer and a call button).
8. No third party scripts, no build step, one HTML file plus assets.

---

## 13. Open questions for Josh or Paul

1. **The destination URL** for the form. Draft page or live page?
2. **Does the film exist in any form**, or does a shoot need scheduling first?
3. **Is the "challenge a mate" share acceptable**, given it will publish a link publicly?
4. **Who approves the game copy** before it goes anywhere near an ad?

---

*Written by Harley, aba TRADES operations agent. The full research, the concept library and the other five concepts are at `https://harley-abatrades.github.io/abatrades-pages/meta-swipe/electrical/`. Ask me for anything missing rather than guessing.*
