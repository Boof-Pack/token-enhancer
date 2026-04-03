# Writing Style Rules

Extracted from README.md. Apply to every external submission: docs, changelogs, marketplace listings, release notes.

---

## Sentence structure

- One idea per sentence. No compound sentences joined by "and" or "but" when each clause can stand alone.
- Lead with the noun, not the action. "Token Enhancer sits between your agent and the web." Not "What Token Enhancer does is sit between..."
- Imperative for instructions. Declarative for facts. No passive voice.
- Maximum ~15 words per sentence in body copy. Headers can be fragments.

---

## Numbers over adjectives

Always use the real number. Never substitute a vague adjective when a measurement exists.

| Never write | Write instead |
|---|---|
| significant reduction | 99.6% reduction |
| much faster | instant (served from cache) |
| fewer tokens | 704,760 → 2,625 tokens |
| multiple sources | three sources |
| large pages | 704K tokens of navigation bars, ads, scripts, and junk |

If you don't have the number, don't make the claim.

---

## Punctuation patterns

- Em dash for sharp interruptions or emphasis: "No API key. No LLM. No GPU. Just Python."
- Period-terminated fragments are allowed and preferred over run-ons: "No API key. No LLM. No GPU."
- Parentheses for inline clarification of a term, not for asides: "(served from cache)"
- No exclamation marks.
- No ellipsis.
- Oxford comma in lists.

---

## Banned words and phrases

Never use these. They are filler that signals the writer has no specifics.

- powerful
- seamless
- robust
- easy / easily
- simple / simply
- intuitive
- flexible
- cutting-edge / state-of-the-art
- leverage (as a verb)
- utilize (use "use")
- solution
- just works
- out of the box
- game-changer
- designed to / built to (lead with what it does, not what it was designed to do)

---

## What this style never does

- Never buries the number. The number is the headline.
- Never explains what a problem feels like before stating the fix. State the fix, then the problem.
- Never uses a rhetorical question.
- Never writes "you can" when the tool just does it. "It fetches the page" not "you can use it to fetch the page."
- Never hedges: no "up to X% in some cases", no "typically around", no "may help".

---

## Three examples pulled directly from the README

**1. Hard number as headline, no adjectives:**
> One fetch of Yahoo Finance: 704,760 tokens → 2,625 tokens. 99.6% reduction.

Single sentence. Two numbers. One ratio. Zero adjectives. The claim proves itself.

**2. Problem stated without hand-wringing:**
> AI agents waste most of their token budget loading raw HTML pages into context. A single Yahoo Finance page is 704K tokens of navigation bars, ads, scripts, and junk. Your agent pays for all of it before any reasoning happens.

Three sentences. Each one a fact. No "unfortunately" or "the challenge is". No sympathy padding.

**3. Feature list with zero fluff:**
> No API key. No LLM. No GPU. Just Python.

Four fragments. Each rules out a dependency the reader feared. "Just Python" is the payoff — one phrase, no elaboration.
