import re
import sys
from pathlib import Path

from symbol_table import SymbolTable
from finite_automaton import load_automata


# Reserved words in the DSL
KEYWORDS = {
    "list", "open", "add", "piece", "pick", "where",
    "sort", "by", "show", "when", "otherwise", "for",
    "each", "in", "end", "and", "or", "is", "not",
    "count", "asc", "desc"
}

FIELDS = {
    "type", "color", "season", "occasion", "price"
}


IDENTIFIER_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
NUMBER_RE = re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?")
STRING_RE = re.compile(r'"[A-Za-z0-9 .,;:!?_()/&\'-]*"')

OPERATORS = [
    "<=", ">=",
    "+", "-", "*", "/", "=",
    "<", ">", "(", ")", ",", "."
]

OPERATOR_TOKEN_NAMES = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "MULTIPLY",
    "/": "DIVIDE",
    "=": "ASSIGN",
    "<": "LESS",
    "<=": "LESS_EQUAL",
    ">": "GREATER",
    ">=": "GREATER_EQUAL",
    "(": "LEFT_PAREN",
    ")": "RIGHT_PAREN",
    ",": "COMMA",
    ".": "DOT"
}


def add_symbol(kind, value):
    """Insert a symbol into the hash table."""
    return symbol_table.insert(kind, value)


def tokenize(source):
    """
    Perform lexical analysis using the integrated finite automata.

    Returns:
        pif: list of Program Internal Form entries
        symbol_table: the SymbolTable instance
        errors: list of lexical errors
    """
    global symbol_table

    symbol_table = SymbolTable()
    automata = load_automata()

    pif = []
    errors = []

    i = 0
    line = 1

    while i < len(source):
        char = source[i]

        if char.isspace():
            if char == "\n":
                line += 1
            i += 1
            continue

        current_line = line

        # String constants: use the STRING finite automaton.
        if char == '"':
            end = i + 1

            while end < len(source) and source[end] != '"':
                if source[end] == "\n":
                    break
                end += 1

            if end < len(source) and source[end] == '"':
                lexeme = source[i:end + 1]

                if automata["STRING"].accepts(lexeme):
                    position = add_symbol("STRING", lexeme)
                    pif.append({
                        "token": "STRING_CONST",
                        "position": position,
                        "line": current_line,
                        "lexeme": lexeme
                    })
                else:
                    errors.append(
                        f"Line {current_line}: invalid string constant {lexeme}"
                    )

                i = end + 1
                continue

            errors.append(
                f"Line {current_line}: unterminated string constant"
            )
            i = end
            continue

        # Number constants: collect the entire number-like lexeme,
        # then let the NUMBER finite automaton validate it.
        if char.isascii() and char.isdigit():
            end = i

            while end < len(source):
                c = source[end]
                if (c.isascii() and c.isalnum()) or c in "_.":
                    end += 1
                else:
                    break

            lexeme = source[i:end]

            if automata["NUMBER"].accepts(lexeme):
                position = add_symbol("NUMBER", lexeme)
                pif.append({
                    "token": "NUMBER_CONST",
                    "position": position,
                    "line": current_line,
                    "lexeme": lexeme
                })
            else:
                errors.append(
                    f"Line {current_line}: invalid number constant {lexeme}"
                )

            i = end
            continue

        # Identifiers and keywords: use the IDENTIFIER finite automaton.
        if char.isascii() and char.isalpha():
            end = i

            while end < len(source):
                c = source[end]
                if (c.isascii() and c.isalnum()) or c == "_":
                    end += 1
                else:
                    break

            lexeme = source[i:end]
            lowercase_lexeme = lexeme.lower()

            if not automata["IDENTIFIER"].accepts(lexeme):
                errors.append(
                    f"Line {current_line}: invalid identifier {lexeme}"
                )
            elif lowercase_lexeme in KEYWORDS:
                pif.append({
                    "token": lowercase_lexeme.upper(),
                    "position": -1,
                    "line": current_line,
                    "lexeme": lexeme
                })
            elif lowercase_lexeme in FIELDS:
                pif.append({
                    "token": lowercase_lexeme.upper(),
                    "position": -1,
                    "line": current_line,
                    "lexeme": lexeme
                })
            else:
                position = add_symbol("IDENTIFIER", lexeme)
                pif.append({
                    "token": "ID",
                    "position": position,
                    "line": current_line,
                    "lexeme": lexeme
                })

            i = end
            continue

        # Operators and separators.
        matched_operator = None

        for operator in OPERATORS:
            if source.startswith(operator, i):
                matched_operator = operator
                break

        if matched_operator is not None:
            pif.append({
                "token": OPERATOR_TOKEN_NAMES[matched_operator],
                "position": -1,
                "line": current_line,
                "lexeme": matched_operator
            })
            i += len(matched_operator)
            continue

        errors.append(
            f"Line {current_line}: invalid character '{char}'"
        )
        i += 1

    return pif, symbol_table, errors


def write_output(pif, symbol_table, errors, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "PIF.txt", "w", encoding="utf-8") as file:
        file.write("Index | Token | ST Position | Line | Lexeme\n")
        file.write("-" * 60 + "\n")

        for index, entry in enumerate(pif):
            file.write(
                f"{index} | {entry['token']} | "
                f"{entry['position']} | {entry['line']} | "
                f"{entry['lexeme']}\n"
            )


    with open(output_dir / "ST.txt", "w", encoding="utf-8") as file:
        file.write("Position | Kind | Value\n")
        file.write("-" * 40 + "\n")

        for entry in symbol_table.get_entries():
            file.write(
                f"{entry['position']} | {entry['kind']} | "
                f"{entry['value']}\n"
            )

    with open(
        output_dir / "lexical_errors.txt", "w", encoding="utf-8"
    ) as file:
        if errors:
            for error in errors:
                file.write(error + "\n")
        else:
            file.write("No lexical errors found.\n")


def main():
    if len(sys.argv) != 2:
        print("Usage: python lexer.py <source_file>")
        sys.exit(1)

    source_file = Path(sys.argv[1])

    if not source_file.is_file():
        print(f"Error: source file '{source_file}' not found.")
        sys.exit(1)

    try:
        source = source_file.read_text(encoding="utf-8")
    except OSError as error:
        print(f"Error reading source file: {error}")
        sys.exit(1)

    pif, st, errors = tokenize(source)

    output_dir = Path("output")
    write_output(pif, st, errors, output_dir)

    print(f"Source file: {source_file}")
    print(f"Tokens recognized: {len(pif)}")
    print(f"Unique symbols: {len(st)}")
    print(f"Lexical errors: {len(errors)}")
    print(f"Output directory: {output_dir.resolve()}")

    if errors:
        print("\nLexical errors:")
        for error in errors:
            print(error)
    else:
        print("No lexical errors found.")


symbol_table = SymbolTable()


if __name__ == "__main__":
    main()
