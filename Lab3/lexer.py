import re
import sys
from pathlib import Path


#keywords defined by DSL
KEYWORDS = {
    "list", "open", "add", "piece",
    "pick", "where","sort","by","show",
    "when","otherwise","for","each",
    "in", "end", "and","or", "is", "not",
    "count", "asc", "desc"
}

FIELDS = {
    "type", "color", "season","occasion", "price"
}

IDENTIFIER_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]*")

NUMBER_RE = re.compile(
    r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?"
)

STRING_RE = re.compile(
    r'"[A-Za-z0-9 .,;:!?_()/&\'-]*"'
)

OPERATORS = [
    ("<=", "LESS_EQUAL"),
    (">=", "GREATER_EQUAL"),
    ("+", "PLUS"),
    ("-", "MINUS"),
    ("*", "MULTIPLY"),
    ("/", "DIVIDE"),
    ("=","ASSIGN"),
    ("<", "LESS"),
    (">", "GREATER"),
    ("(", "LEFT_PAREN"),
    (")", "RIGHT_PAREN"),
    (",", "COMMA"),
    (".","DOT")
]


def tokenize(source):
    pif = []
    symbol_table = []
    symbol_positions = {}
    errors = []

    i = 0
    line=1

    def add_symbol(kind,value):
        key= (kind, value)
        if key not in symbol_positions:
            position = len(symbol_table)
            symbol_positions[key] = position
            symbol_table.append({
                "position":position,
                "kind":kind,
                "value":value
            })

        return symbol_positions[key]

    while i < len(source):
        char = source[i]

        if char.isspace():
            if char == "\n":
                line+=1
            i+=1
            continue

        #strings
        if char == '"':
            match = STRING_RE.match(source, i)

            if match:
                value = match.group()
                position = add_symbol("STRING",value)


                pif.append({
                    "token": "STRING_CONST",
                    "position":position,
                    "line":line,
                    "lexeme":value
                })

                i=match.end()
                continue

            #reportan invalid or unterminated string
            end = i+1

            while end < len(source) and source[end] not in '\n"':
                end += 1

            if end < len(source) and source[end] == '"':
                end += 1

            errors.append(
                f"Line {line}: invalid or unterminated string"
                f"{source[i:end]!r}"
            )

            i=end
            continue

        #numbers
        if char.isdigit():
            match = NUMBER_RE.match(source, i)

            if match:
                value = match.group()
                end = match.end()

                if(
                    end < len(source)
                    and source[end] == "."
                    and end+1 < len(source)
                    and source[end+1].isdigit()
                ):
                    bad_end = end +1

                    while(
                        bad_end < len(source)
                        and (
                        source[bad_end].isdigit()
                        or source[bad_end] == "."
                        )
                    ):
                        bad_end += 1

                    errors.append(
                        f"Line {line}: malformed number"
                        f"{source[i:bad_end]!r}"
                    )

                    i = bad_end
                    continue

                position = add_symbol("NUMBER",value)

                pif.append({
                    "token" : "NUMBER_CONST",
                    "position":position,
                    "line":line,
                    "lexeme":value
                })

                i=end
                continue

            errors.append(
                f"Line {line}: invalid number starting at {source[i:]!r}"
            )
            i +=1
            continue

        match = IDENTIFIER_RE.match(source, i)

        if match:
            value = match.group()
            end = match.end()

            if value in KEYWORDS:
                pif.append({
                    "token" : value.upper(),
                    "position":-1,
                    "line":line,
                    "lexeme":value
                })

            elif value in FIELDS:
                pif.append({
                    "token" : "FIELD",
                    "position": -1,
                    "line":line,
                    "lexeme":value
                })

            else:
                position = add_symbol("IDENTIFIER",value)

                pif.append({
                    "token" : "ID",
                    "position":position,
                    "line":line,
                    "lexeme":value
                })

            i=end
            continue

         #operators and delimiters
        matched = False


        for operator , token_name  in OPERATORS:
            if source.startswith(operator,i):
                pif.append({
                    "token" : token_name,
                    "position":-1,
                    "line":line,
                    "lexeme":operator
                })

                i+=len(operator)
                matched = True
                break

        if matched:
            continue


        #anything else is lexical error

        errors.append(
            f"Line {line} : unrecognized character {char !r}"
        )

        i+=1

    return pif, symbol_table, errors


def write_output(pif,symbol_table,errors,output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)

    with(output_dir / "PIF.txt").open(
        "w", encoding="utf-8"
    ) as file:
        file.write("Index | Token | ST Position | Line | Lexeme\n")

        for index,entry in enumerate(pif):
            file.write(
                f"{index} | {entry['token']} | "
                f" {entry['position']} | {entry['line']} | "
                f"{entry['lexeme']}\n"
            )

    with (output_dir / "ST.txt").open(
        "w", encoding="utf-8"
    ) as file:
        file.write("Position | Kind | Value\n")

        for entry in symbol_table:
            file.write(
                f"{entry['position']} | {entry['kind']} | "
                f"{entry['value']}\n"
            )

    with(output_dir / "lexical_errors.txt").open(
        "w", encoding="utf-8"
    ) as file:
        if errors:
            file.write("\n".join(errors) + "\n")
        else:
            file.write("No lexical errors found.\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python lexer.py Program1.txt")
        print("  or: python lexer.py Program2.txt")
        return

    source_path = Path(sys.argv[1])
    output_dir = Path("output")

    try:
        source = source_path.read_text(encoding="utf-8")

    except OSError as error:
        print(f"Could not read source file: {error}")
        return

    pif, symbol_table, errors = tokenize(source)

    write_output(pif,symbol_table,errors,output_dir)

    print(f"Source file: {source_path}")
    print(f"Tokens found: {len(pif)}")
    print(f"Symbol table entries: {len(symbol_table)}")
    print(f"Lexical errors: {len(errors)}")
    print(f"Output directory: {output_dir.resolve()}")

if __name__ == "__main__":
    main()




























