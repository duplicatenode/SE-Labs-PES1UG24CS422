"""Small, validated text and integer processing helpers."""


def normalize_text(text):
    """Trim text and collapse all Unicode whitespace to single spaces."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return " ".join(text.split())


def parse_integer_list(text):
    """Parse comma-separated integers; blank input represents an empty list."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not text.strip():
        return []

    tokens = [item.strip() for item in text.split(",")]
    if any(not item for item in tokens):
        raise ValueError("integer list contains an empty item")
    try:
        return [int(item) for item in tokens]
    except ValueError as exc:
        raise ValueError("integer list contains a non-integer item") from exc


def summarize_numbers(numbers):
    """Return count, extrema, total, and average for integer values."""
    if not isinstance(numbers, (list, tuple)):
        raise TypeError("numbers must be a list or tuple of integers")
    if any(not isinstance(number, int) or isinstance(number, bool) for number in numbers):
        raise TypeError("numbers must contain only integers")

    if not numbers:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "total": 0,
            "average": 0.0,
        }

    total = sum(numbers)
    average = total / len(numbers)
    return {
        "count": len(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "total": total,
        "average": average,
    }


if __name__ == "__main__":
    sample_text = "  Ada\tLovelace   "
    sample_numbers = parse_integer_list("12, -3, 9")
    print("Normalized text:", normalize_text(sample_text))
    print("Parsed integers:", sample_numbers)
    print("Summary:", summarize_numbers(sample_numbers))
