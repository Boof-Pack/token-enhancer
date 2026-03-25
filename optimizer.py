"""
Agent Cost Proxy - Layer 1: Prompt Optimizer
Strips filler, protects entities/intent, checks confidence.
Rule-based engine. No GPU required.
"""

import re
from dataclasses import dataclass


@dataclass
class OptimizationResult:
    original: str
    optimized: str
    original_tokens: int
    optimized_tokens: int
    confidence: float
    protected_entities: list
    sent_optimized: bool
    skip_reason: str = ""


# ============================================================
#  PROTECTED PATTERNS — these are never removed
# ============================================================

TICKER_PATTERN = re.compile(r'\b[A-Z]{2,5}\b(?=\s|,|\.|\)|$)')

MONEY_PATTERN = re.compile(r'\$[\d,.]+[BMKbmk]?|\d+\.?\d*\s*%|\d+[xX]\b')

TIME_REFS = re.compile(
    r'\b(today|yesterday|tomorrow|'
    r'last\s+(?:week|month|quarter|year)|'
    r'next\s+(?:week|month|quarter|year)|'
    r'this\s+(?:week|month|quarter|year)|'
    r'Q[1-4]\s*\d{2,4}|FY\s*\d{2,4}|\d{4}|'
    r'\d{1,2}/\d{1,2}/\d{2,4}|'
    r'since\s+\w+|before\s+\w+|after\s+\w+|'
    r'YTD|MTD|QTD)\b',
    re.IGNORECASE
)

CONVO_REFS = re.compile(
    r'\b(what we discussed|as I said|like I mentioned|'
    r'my portfolio|we talked about|you said|you mentioned|'
    r'earlier|previously|last time|before this|'
    r'our conversation|what you told me|remember when|'
    r'as we agreed|my account|my positions?)\b',
    re.IGNORECASE
)

NEGATIONS = re.compile(
    r"\b(don'?t|do not|not|never|no|exclude|ignore|without|"
    r"isn'?t|aren'?t|won'?t|can'?t|shouldn'?t|wouldn'?t|"
    r"doesn'?t|haven'?t|hasn'?t|avoid|skip|except)\b",
    re.IGNORECASE
)

QUESTION_ANCHORS = re.compile(
    r'\b(who|what|when|where|why|how|which|compare|'
    r'difference|versus|vs\.?|better|worse|rank|list|'
    r'explain|summarize|analyze|recommend|suggest|'
    r'should I|is it)\b',
    re.IGNORECASE
)


# ============================================================
#  FILLER PATTERNS — safe to remove
# ============================================================

FILLER_PATTERNS = [
    # Hedging openers
    (re.compile(r'\bI was wondering if (?:you could |maybe )?', re.I), ''),
    (re.compile(r'\bcould you (?:please |maybe |possibly )?', re.I), ''),
    (re.compile(r'\bwould you (?:be able to |mind )?', re.I), ''),
    (re.compile(r'\bI would (?:really )?like (?:you )?to ', re.I), ''),
    (re.compile(r'\bcan you (?:please )?', re.I), ''),
    (re.compile(r'\bdo you think you could ', re.I), ''),
    (re.compile(r'\bif (?:it\'?s )?(?:not too much trouble|possible),?\s*', re.I), ''),

    # Politeness padding
    (re.compile(r'\b(?:please|thanks|thank you|thx|pls)\b[,.]?\s*', re.I), ''),
    (re.compile(r'^(?:hey|hi|hello|yo|sup)(?:\s+there)?[,.\s]+', re.I), ''),
    (re.compile(r'^(?:so|ok so|okay so|alright so|okay)\s+', re.I), ''),

    # Filler words
    (re.compile(
        r'\b(?:basically|actually|honestly|really|just|very|quite|'
        r'pretty much|kind of|sort of|literally|obviously|clearly|'
        r'simply|definitely|certainly|absolutely|essentially|'
        r'fundamentally|in my opinion|I think that|I believe that|'
        r'it seems like|to be honest|as you know|you know|I mean|'
        r'if you know what I mean|at the end of the day|'
        r'needless to say)\b,?\s*', re.I), ''),

    # Redundant closers
    (re.compile(
        r'\s*(?:thanks in advance|thank you so much|'
        r'I really appreciate it|that would be great|'
        r'that would be awesome|I\'d appreciate it|'
        r'much appreciated|cheers)\.?\s*$', re.I), ''),

    # Whitespace cleanup
    (re.compile(r'  +'), ' '),
    (re.compile(r'\n\s*\n\s*\n+'), '\n\n'),
]


# ============================================================
#  CORE FUNCTIONS
# ============================================================

def estimate_tokens(text: str) -> int:
    """Rough estimate: ~4 chars per token."""
    return max(1, len(text) // 4)


# Filler phrases that contain negations — don't count these as real negations
FILLER_NEGATION_PHRASES = re.compile(
    r"(?:not too much trouble|not a problem|no worries|not at all|"
    r"no rush|not urgent|if it's not)",
    re.IGNORECASE
)


def extract_protected(text: str) -> list:
    """Find all tokens that must be preserved."""
    protected = []

    # Find negations inside filler phrases so we can exclude them
    filler_neg_spans = set()
    for match in FILLER_NEGATION_PHRASES.finditer(text):
        filler_neg_spans.add((match.start(), match.end()))

    patterns = [
        (TICKER_PATTERN, "ticker"),
        (MONEY_PATTERN, "money"),
        (TIME_REFS, "time_ref"),
        (CONVO_REFS, "convo_ref"),
        (NEGATIONS, "negation"),
        (QUESTION_ANCHORS, "question"),
    ]
    for pattern, label in patterns:
        for match in pattern.finditer(text):
            # Skip negations that are inside filler phrases
            if label == "negation":
                in_filler = any(
                    s <= match.start() and match.end() <= e
                    for s, e in filler_neg_spans
                )
                if in_filler:
                    continue
            protected.append({"text": match.group(), "type": label})
    return protected


def is_code_or_json(text: str) -> bool:
    """Detect code/JSON prompts — skip optimization."""
    indicators = ['{', '}', 'def ', 'class ', 'import ', 'function ',
                  'const ', 'var ', 'let ', '```', '===', '!==']
    return sum(1 for i in indicators if i in text) >= 3


def calculate_confidence(original_protected, optimized_protected) -> float:
    """Check that protected entities survived optimization."""

    def match_rate(orig, opt, label):
        orig_set = {e["text"].lower() for e in orig if e["type"] == label}
        opt_set = {e["text"].lower() for e in opt if e["type"] == label}
        if not orig_set:
            return 1.0
        return len(orig_set & opt_set) / len(orig_set)

    # High-value entities — these matter most
    critical_types = ["ticker", "money", "time_ref", "convo_ref"]
    critical_scores = [match_rate(original_protected, optimized_protected, t)
                       for t in critical_types]
    # Only count types that actually existed in the original
    active_critical = [s for s, t in zip(critical_scores, critical_types)
                       if any(e["type"] == t for e in original_protected)]
    entity_score = min(active_critical) if active_critical else 1.0

    intent_score = match_rate(original_protected, optimized_protected, "question")
    negation_score = match_rate(original_protected, optimized_protected, "negation")

    return (entity_score * 0.4) + (intent_score * 0.3) + (negation_score * 0.3)


def optimize_prompt(text: str,
                    confidence_threshold: float = 0.90,
                    min_tokens: int = 50) -> OptimizationResult:
    """
    Main entry point.
    Returns OptimizationResult — either optimized or original with reason.
    """
    original_tokens = estimate_tokens(text)

    # --- Skip conditions ---
    if original_tokens < min_tokens:
        return OptimizationResult(
            original=text, optimized=text,
            original_tokens=original_tokens,
            optimized_tokens=original_tokens,
            confidence=1.0, protected_entities=[],
            sent_optimized=False, skip_reason="below_min_tokens"
        )

    if is_code_or_json(text):
        return OptimizationResult(
            original=text, optimized=text,
            original_tokens=original_tokens,
            optimized_tokens=original_tokens,
            confidence=1.0, protected_entities=[],
            sent_optimized=False, skip_reason="code_or_json"
        )

    # --- Step 1: Extract protected entities ---
    protected_before = extract_protected(text)

    # --- Step 2: Remove filler ---
    optimized = text
    for pattern, replacement in FILLER_PATTERNS:
        optimized = pattern.sub(replacement, optimized)

    # Clean up edges
    optimized = optimized.strip()
    optimized = re.sub(r'^[,.\s]+', '', optimized)
    if optimized and optimized[0].islower():
        optimized = optimized[0].upper() + optimized[1:]

    optimized_tokens = estimate_tokens(optimized)

    # --- Step 3: Confidence check ---
    protected_after = extract_protected(optimized)
    confidence = calculate_confidence(protected_before, protected_after)

    # --- Step 4: Decision ---
    ratio = optimized_tokens / original_tokens if original_tokens > 0 else 1.0
    not_worth_it = ratio > 0.95
    confident_enough = confidence >= confidence_threshold

    sent_optimized = confident_enough and not not_worth_it

    skip_reason = ""
    if not confident_enough:
        skip_reason = f"low_confidence ({confidence:.2f})"
    elif not_worth_it:
        skip_reason = f"negligible_savings ({ratio:.2f})"

    return OptimizationResult(
        original=text,
        optimized=optimized if sent_optimized else text,
        original_tokens=original_tokens,
        optimized_tokens=optimized_tokens if sent_optimized else original_tokens,
        confidence=confidence,
        protected_entities=[e["text"] for e in protected_before],
        sent_optimized=sent_optimized,
        skip_reason=skip_reason
    )
