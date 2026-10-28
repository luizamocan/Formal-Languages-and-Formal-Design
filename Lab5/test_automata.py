
from finite_automaton import load_automata

automata = load_automata()

tests = {
    "IDENTIFIER": [
        ("closet", True),
        ("item1", True),
        ("item_name", True),
        ("1item", False),
        ("", False),
    ],
    "NUMBER": [
        ("0", True),
        ("150", True),
        ("12.50", True),
        ("012", False),
        ("12.", False),
        ("", False),
    ],
    "STRING": [
        ('"dress"', True),
        ('""', True),
        ('"pink summer"', True),
        ('"unfinished', False),
    ],
}

for name, cases in tests.items():
    automaton = automata[name]
    print(f"\n{name}")

    for token, expected in cases:
        actual = automaton.accepts(token)
        status = "PASS" if actual == expected else "FAIL"
        print(f"{status}: {token!r} -> {actual}")
