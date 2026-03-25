"""
Test suite for Agent Cost Proxy.
Tests Layer 1 (optimizer) and Layer 2 (data proxy).

Usage:
    python3 test_all.py          # Layer 1 only (offline)
    python3 test_all.py --live   # Layer 1 + Layer 2 (needs internet)
"""

import sys
from optimizer import optimize_prompt

LIVE = "--live" in sys.argv


def test_layer1():
    print("\n" + "=" * 56)
    print("  LAYER 1: Prompt Refiner")
    print("=" * 56)

    tests = [
        (
            "Verbose financial query",
            "Hey, so I was wondering if you could maybe look at Apple's "
            "latest earnings report and tell me how they did compared to "
            "last quarter, especially the services revenue part because "
            "I've been tracking that, and also what analysts are saying. "
            "Thanks in advance, I really appreciate it!",
            True  # should optimize
        ),
        (
            "Negations + context preserved",
            "Hi there, could you please analyze TSLA stock performance "
            "but don't include any crypto-related comparisons. Also, "
            "remember what we discussed last time about the $45 price "
            "target — I want to revisit that. Thank you so much!",
            True
        ),
        (
            "Short prompt (should skip)",
            "Compare AAPL and MSFT Q3 earnings.",
            False
        ),
        (
            "Code (should skip)",
            "def calculate_roi(investment, returns):\n"
            "    import numpy as np\n"
            "    return np.sum(returns) / investment\n"
            "Fix this function to handle edge cases.",
            False
        ),
        (
            "Heavy filler",
            "Okay so basically I was just thinking, honestly, could you "
            "kind of like help me understand what the PE ratio actually "
            "means for a company like NVDA? I mean, I know it's sort of "
            "important but I don't really get why it matters so much. "
            "If it's not too much trouble, that would be awesome. Cheers!",
            True
        ),
        (
            "Conversation refs preserved",
            "Hey, so going back to what we discussed earlier about my "
            "portfolio allocation, I think I want to shift more into "
            "bonds. Like I mentioned last time, I'm not comfortable with "
            "the 80/20 split anymore. Can you suggest a more conservative "
            "approach? Thanks!",
            True
        ),
        (
            "Multiple tickers + money",
            "Hi, I would really like you to compare the performance of "
            "AAPL, MSFT, GOOGL, and AMZN over the last year. Specifically, "
            "which one had the best return if I invested $10,000 in each? "
            "Also, what's the YTD performance? I'd appreciate it, thanks!",
            True
        ),
    ]

    passed = 0
    failed = 0
    total_orig = 0
    total_opt = 0

    for name, prompt, should_optimize in tests:
        result = optimize_prompt(prompt)
        total_orig += result.original_tokens
        total_opt += result.optimized_tokens

        correct = result.sent_optimized == should_optimize
        status = "PASS" if correct else "FAIL"
        if not correct:
            failed += 1
        else:
            passed += 1

        if result.sent_optimized:
            savings = (1 - result.optimized_tokens / result.original_tokens) * 100
            print(f"\n  [{status}] {name}")
            print(f"    {result.original_tokens} -> {result.optimized_tokens} tokens ({savings:.0f}% saved)")
            print(f"    Protected: {', '.join(result.protected_entities[:5])}")
        else:
            print(f"\n  [{status}] {name}")
            print(f"    Skipped: {result.skip_reason}")

    saved = total_orig - total_opt
    pct = (saved / total_orig * 100) if total_orig > 0 else 0
    print(f"\n  Layer 1 Results: {passed} passed, {failed} failed")
    print(f"  Total: {total_orig} -> {total_opt} tokens ({pct:.0f}% saved)")


def test_layer2():
    if not LIVE:
        print("\n" + "=" * 56)
        print("  LAYER 2: Data Proxy (skipped — run with --live)")
        print("=" * 56)
        return

    from data_proxy import fetch_and_clean, init_data_db
    init_data_db()

    print("\n" + "=" * 56)
    print("  LAYER 2: Data Proxy (live)")
    print("=" * 56)

    tests = [
        ("Yahoo Finance AAPL", "https://finance.yahoo.com/quote/AAPL/"),
        ("Wikipedia Python", "https://en.wikipedia.org/wiki/Python_(programming_language)"),
        ("Hacker News", "https://news.ycombinator.com/"),
    ]

    total_orig = 0
    total_clean = 0

    for name, url in tests:
        result = fetch_and_clean(url)

        if result.error:
            print(f"\n  [FAIL] {name}")
            print(f"    Error: {result.error[:60]}")
            continue

        total_orig += result.original_tokens
        total_clean += result.cleaned_tokens
        reduction = (1 - result.cleaned_tokens / result.original_tokens) * 100

        content_preview = result.content[:80].replace("\n", " ")
        print(f"\n  [PASS] {name}")
        print(f"    {result.original_tokens:,} -> {result.cleaned_tokens:,} tokens ({reduction:.1f}% reduced)")
        print(f"    Preview: {content_preview}...")

        # Test cache hit
        result2 = fetch_and_clean(url)
        cache_status = "PASS" if result2.from_cache else "FAIL"
        print(f"    Cache: [{cache_status}] {'hit' if result2.from_cache else 'miss'}")

    if total_orig > 0:
        saved = total_orig - total_clean
        pct = (saved / total_orig) * 100
        print(f"\n  Layer 2 Results:")
        print(f"  Total: {total_orig:,} -> {total_clean:,} tokens ({pct:.1f}% saved)")
        print(f"  Est. cost saved: ~${saved * 0.000015:.2f}")


if __name__ == "__main__":
    test_layer1()
    test_layer2()

    print("\n" + "=" * 56)
    if LIVE:
        print("  All tests complete.")
    else:
        print("  Layer 1 tests complete.")
        print("  Run with --live to test Layer 2 (needs internet)")
    print("=" * 56 + "\n")
