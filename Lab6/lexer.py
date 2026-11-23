
import sys
import re
from pathlib import Path

import ply.lex as lex

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


# PLY token names
tokens = [
    "ID",
    "NUMBER_CONST",
    "STRING_CONST",

    "PLUS",
    "MINUS",
    "MULTIPLY",
    "DIVIDE",
    "ASSIGN",

    "LESS",
    "LESS_EQUAL",
    "GREATER",
    "GREATER_EQUAL",

    "LEFT_PAREN",
    "RIGHT_PAREN",
    "COMMA",
    "DOT",

    "LIST",
    "OPEN",
    "ADD",
    "PIECE",
    "PICK",
    "WHERE",
    "SORT",
    "BY",
    "SHOW",
    "WHEN",
    "OTHERWISE",
    "FOR",
    "EACH",
    "IN",
    "END",
    "AND",
    "OR",
    "IS",
    "NOT",
    "COUNT",
    "ASC",
    "DESC",

    "TYPE",
    "COLOR",
    "SEASON",
    "OCCASION",
    "PRICE"
]


# Map reserved words and fields to their token names
reserved = {
    word: word.upper()
    for word in KEYWORDS | FIELDS
}


# Operators and separators
t_PLUS = r"\+"
t_MINUS = r"-"
t_MULTIPLY = r"\*"
t_DIVIDE = r"/"
t_ASSIGN = r"="
t_LESS_EQUAL = r"<="
t_GREATER_EQUAL = r">="
t_LESS = r"<"
t_GREATER = r">"
t_LEFT_PAREN = r"\("
t_RIGHT_PAREN = r"\)"
t_COMMA = r","
t_DOT = r"\."


# Spaces and tabs are ignored
t_ignore = " \t\r"


# Global scanner information
symbol_table = SymbolTable()
automata = load_automata()

pif = []
lexical_errors = []


def reset_lexer_data():
    """Reset the PIF, symbol table and lexical errors."""
    global symbol_table, pif, lexical_errors

    symbol_table = SymbolTable()
    pif = []
    lexical_errors = []


def add_pif_entry(token_type, position, line, lexeme):
    """Add one entry to the Program Internal Form."""
    pif.append({
        "token": token_type,
        "position": position,
        "line": line,
        "lexeme": lexeme
    })


# String constants
def t_STRING_CONST(t):
    r'"[^"\n]*"'

    lexeme = t.value

    if not automata["STRING"].accepts(lexeme):
        lexical_errors.append(
            f"Line {t.lineno}: invalid string constant {lexeme}"
        )
        return None

    position = symbol_table.insert("STRING", lexeme)

    add_pif_entry(
        "STRING_CONST",
        position,
        t.lineno,
        lexeme
    )

    return t


# Number constants
def t_NUMBER_CONST(t):
    r'[0-9][A-Za-z0-9_.]*'

    lexeme = t.value

    if not automata["NUMBER"].accepts(lexeme):
        lexical_errors.append(
            f"Line {t.lineno}: invalid number constant {lexeme}"
        )
        return None

    position = symbol_table.insert("NUMBER", lexeme)

    add_pif_entry(
        "NUMBER_CONST",
        position,
        t.lineno,
        lexeme
    )

    return t


# Identifiers and reserved words
def t_ID(t):
    r'[A-Za-z][A-Za-z0-9_]*'

    lexeme = t.value
    lowercase_lexeme = lexeme.lower()

    if not automata["IDENTIFIER"].accepts(lexeme):
        lexical_errors.append(
            f"Line {t.lineno}: invalid identifier {lexeme}"
        )
        return None

    if lowercase_lexeme in reserved:
        t.type = reserved[lowercase_lexeme]

        add_pif_entry(
            t.type,
            -1,
            t.lineno,
            lexeme
        )

    else:
        position = symbol_table.insert("IDENTIFIER", lexeme)

        add_pif_entry(
            "ID",
            position,
            t.lineno,
            lexeme
        )

    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_unterminated_string(t):
    r'"[^"\n]*(?:\n|$)'

    lexical_errors.append(
        f"Line {t.lineno}: unterminated string constant"
    )

    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    lexical_errors.append(
        f"Line {t.lineno}: invalid character '{t.value[0]}'"
    )
    t.lexer.skip(1)


def build_lexer():
    """Build and return a PLY lexer."""
    return lex.lex(module=sys.modules[__name__])


def tokenize(source):
    """
    Perform lexical analysis.

    Returns:
        PIF
        Symbol table
        Lexical errors
    """
    reset_lexer_data()

    lexer = build_lexer()
    lexer.lineno = 1
    lexer.input(source)

    while lexer.token():
        pass

    return pif, symbol_table, lexical_errors


def write_output(pif_data, st, errors, output_dir):
    """Write PIF, symbol table and lexical errors."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "PIF.txt", "w", encoding="utf-8") as file:
        file.write("Index | Token | ST Position | Line | Lexeme\n")
        file.write("-" * 60 + "\n")

        for index, entry in enumerate(pif_data):
            file.write(
                f"{index} | {entry['token']} | "
                f"{entry['position']} | {entry['line']} | "
                f"{entry['lexeme']}\n"
            )

    with open(output_dir / "ST.txt", "w", encoding="utf-8") as file:
        file.write("Position | Kind | Value\n")
        file.write("-" * 40 + "\n")

        for entry in st.get_entries():
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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python lexer.py <source_file>")
        sys.exit(1)

    source_file = Path(sys.argv[1])

    if not source_file.is_file():
        print(f"Error: source file '{source_file}' not found.")
        sys.exit(1)

    source = source_file.read_text(encoding="utf-8")

    pif_data, st, errors = tokenize(source)

    write_output(pif_data, st, errors, "output")

    print(f"Source file: {source_file}")
    print(f"Tokens recognized: {len(pif_data)}")
    print(f"Unique symbols: {len(st)}")
    print(f"Lexical errors: {len(errors)}")

    for error in errors:
        print(error)
