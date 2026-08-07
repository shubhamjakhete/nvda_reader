TIER_VERIFIED = "verified"
TIER_PARTIAL = "partial"
TIER_UNVERIFIED = "unverified"


def compose(label: str, category_human: str, tier: str) -> str:
    """
    verified   -> "{category_human}, likely {label}"
    partial    -> "{category_human}, unverified guess: {label}"
    unverified -> "unrecognized control, possibly {label}"
    """
    if tier == TIER_VERIFIED:
        if category_human:
            return f"{category_human}, likely {label}"
        return f"likely {label}"
    elif tier == TIER_PARTIAL:
        if category_human:
            return f"{category_human}, unverified guess: {label}"
        return f"unverified guess: {label}"
    else:
        return f"unrecognized control, possibly {label}"
