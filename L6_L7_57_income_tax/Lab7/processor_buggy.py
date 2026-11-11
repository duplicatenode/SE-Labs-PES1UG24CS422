"""Pre-fix baseline kept to reproduce the fuzzing failures."""


def normalize_text(text):
    return " ".join(text.strip().split(" "))


def parse_integer_list(text):
    return [int(item) for item in text.split(",")]


def summarize_numbers(numbers):
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
