
import re
import sys
from pathlib import Path

from symbol_table import SymbolTable


# reserved words in the DSL
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

NUMBER_RE = re.compile(
    r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?"
)

STRING_RE = re.compile(
    r'"[A-Za-z0-9 .,;:!?_()/&\'-]*"'
)


OPERATORS = [
    "<=", ">=",
    "+", "-", "*", "/", "=",
    "<", ">", "(", ")", ",", "."
]


def add_symbol(kind, value):
    """
    Insert a symbol into the hash table.
    Return its existing position if it is already present.
    """
    return symbol_table.insert(kind, value)


def tokenize(source):
    """
    Perform lexical analysis.

    Returns:
        pif: list of Program Internal Form entries
        symbol_table: the SymbolTable instance
        errors: list of lexical errors
    """
    global symbol_table

    symbol_table = SymbolTable()

    pif = []
    errors = []

    i = 0
    line = 1
    token_index = 0

    while i < len(source):
        char = source[i]

        if char.isspace():
            if char == "\n":
                line += 1
            i += 1
            continue

        current_line = line

        if char == '"':
            end = i + 1

            while end < len(source) and source[end] != '"':
                if source[end] == "\n":
                    break
                end += 1

            if end < len(source) and source[end] == '"':
                lexeme = source[i:end + 1]

                if STRING_RE.fullmatch(lexeme):
                    position = add_symbol("STRING", lexeme)

                    pif.append({
                        "token": "STRING_CONST",
                        "position": position,
                        "line": current_line,
                        "lexeme": lexeme
                    })

                    token_index += 1
                    i = end + 1
                    continue

                errors.append(
                    f"Line {current_line}: invalid string constant "
                    f"{lexeme}"
                )

                i = end + 1
                continue

            errors.append(
                f"Line {current_line}: unterminated string constant"
            )

            # Skip to the next line or end of input
            i = end
            continue


        number_match = NUMBER_RE.match(source, i)

        if number_match:
            lexeme = number_match.group()
            position = add_symbol("NUMBER", lexeme)

            pif.append({
                "token": "NUMBER_CONST",
                "position": position,
                "line": current_line,
                "lexeme": lexeme
            })

            token_index += 1
            i = number_match.end()
            continue

        identifier_match = IDENTIFIER_RE.match(source, i)

        if identifier_match:
            lexeme = identifier_match.group()
            lowercase_lexeme = lexeme.lower()

            if lowercase_lexeme in KEYWORDS:
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

            token_index += 1
            i = identifier_match.end()
            continue

        matched_operator = None

        for operator in OPERATORS:
            if source.startswith(operator, i):
                matched_operator = operator
                break

        if matched_operator is not None:
            operator_token_names = {
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

            pif.append({
                "token": operator_token_names[matched_operator],
                "position": -1,
                "line": current_line,
                "lexeme": matched_operator
            })

            token_index += 1
            i += len(matched_operator)
            continue

        #any unrecognized character is a lexical error
        errors.append(
            f"Line {current_line}: invalid character '{char}'"
        )

        i += 1

    return pif, symbol_table, errors


def write_output(pif, symbol_table, errors, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # writing program internal form
    with open(output_dir / "PIF.txt", "w", encoding="utf-8") as file:
        file.write("Index | Token | ST Position | Line | Lexeme\n")
        file.write("-" * 60 + "\n")

        for index, entry in enumerate(pif):
            file.write(
                f"{index} | {entry['token']} | "
                f"{entry['position']} | {entry['line']} | "
                f"{entry['lexeme']}\n"
            )

    # writing symbol table
    with open(output_dir / "ST.txt", "w", encoding="utf-8") as file:
        file.write("Position | Kind | Value\n")
        file.write("-" * 40 + "\n")

        for entry in symbol_table.get_entries():
            file.write(
                f"{entry['position']} | {entry['kind']} | "
                f"{entry['value']}\n"
            )

    # write lexical errors
    with open(
        output_dir / "lexical_errors.txt",
        "w",
        encoding="utf-8"
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
