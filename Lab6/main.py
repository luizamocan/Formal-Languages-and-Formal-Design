
import sys
from pathlib import Path

import lexer as lexer_module
import parser as parser_module


def write_productions(productions, output_dir):
    """Write the sequence of grammar productions."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(
        output_dir / "productions.txt",
        "w",
        encoding="utf-8"
    ) as file:
        for index, production in enumerate(productions, start=1):
            file.write(f"{index}. {production}\n")


def write_syntax_errors(errors, output_dir):
    """Write syntax errors."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(
        output_dir / "syntax_errors.txt",
        "w",
        encoding="utf-8"
    ) as file:
        if errors:
            for error in errors:
                file.write(error + "\n")
        else:
            file.write("No syntax errors found.\n")


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <source_file>")
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

    output_dir = Path("output")

    # Reset lexical and syntactical analysis data
    lexer_module.reset_lexer_data()
    parser_module.reset_parser_data()

    lexer = lexer_module.build_lexer()
    lexer.lineno = 1

    # Perform integrated lexical and syntactical analysis
    result = parser_module.parser.parse(
        source,
        lexer=lexer
    )

    pif = lexer_module.pif
    symbol_table = lexer_module.symbol_table
    lexical_errors = lexer_module.lexical_errors

    syntax_errors = parser_module.syntax_errors
    productions = parser_module.productions


    lexer_module.write_output(
        pif,
        symbol_table,
        lexical_errors,
        output_dir
    )

    write_productions(productions, output_dir)
    write_syntax_errors(syntax_errors, output_dir)

    print("\n========== ANALYSIS RESULTS ==========")

    print(f"Source file: {source_file}")
    print(f"Tokens recognized: {len(pif)}")
    print(f"Unique symbols: {len(symbol_table)}")
    print(f"Lexical errors: {len(lexical_errors)}")
    print(f"Syntax errors: {len(syntax_errors)}")
    print(f"Productions generated: {len(productions)}")

    if lexical_errors:
        print("\nLexical errors:")
        for error in lexical_errors:
            print(error)

    if syntax_errors:
        print("\nSyntax errors:")
        for error in syntax_errors:
            print(error)

    if not lexical_errors and not syntax_errors and result is not None:
        print("\nThe program is syntactically correct.")
    else:
        print("\nThe program contains errors.")

    print(f"\nOutput directory: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
