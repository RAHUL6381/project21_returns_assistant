from datetime import date

def check_return_eligibility(
    category: str,
    delivery_date: str,
    request_date: str,
    unused: bool,
    tags_attached: bool
) -> dict:

    # Validate category
    if category not in ("clothing", "electronics", "personal_care"):
        raise ValueError("Invalid product category.")

    # Validate dates
    try:
        delivery = date.fromisoformat(delivery_date)
        request = date.fromisoformat(request_date)
    except (ValueError, TypeError):
        raise ValueError("Dates must be valid and in YYYY-MM-DD format.")

    if delivery.isoformat() != delivery_date or request.isoformat() != request_date:
        raise ValueError("Dates must use YYYY-MM-DD format.")

    # Reject requests before delivery
    if request < delivery:
        raise ValueError("Request date cannot be before delivery date.")

    # Calculate elapsed calendar days
    days_since_delivery = (request - delivery).days

    # Check eligibility
    reasons = []

    if category == "personal_care":
        reasons.append("Personal-care items are not returnable.")

    elif category == "clothing":
        if days_since_delivery > 15:
            reasons.append("Return window exceeded (15 days).")

        if not unused:
            reasons.append("Product must be unused.")

        if not tags_attached:
            reasons.append("Clothing tags must be attached.")

    elif category == "electronics":
        if days_since_delivery > 7:
            reasons.append("Return window exceeded (7 days).")

        if not unused:
            reasons.append("Product must be unused.")

    return {
        "eligible": len(reasons) == 0,
        "days_since_delivery": days_since_delivery,
        "reasons": reasons
    }


# Example usage
result = check_return_eligibility(
    category="clothing",
    delivery_date="2026-10-01",
    request_date="2026-10-15",
    unused=True,
    tags_attached=True
)

print(result)