
import ply.yacc as yacc

from lexer import tokens

start = "program"

productions = []
syntax_errors = []


def reset_parser_data():
    productions.clear()
    syntax_errors.clear()


def p_program(p):
    "program : statements"
    p[0] = p[1]
    productions.append("<program> ::= <statements>")


def p_statements_single(p):
    "statements : statement"
    p[0] = [p[1]]
    productions.append("<statements> ::= <statement>")


def p_statements_multiple(p):
    "statements : statements statement"
    p[0] = p[1] + [p[2]]
    productions.append("<statements> ::= <statements> <statement>")


def p_statement(p):
    """statement : declare
                 | open_statement
                 | add_statement
                 | assign_statement
                 | sort_statement
                 | show_statement
                 | when_statement
                 | for_statement"""
    p[0] = p[1]

    names = {
        "declare": "<declare>",
        "open_statement": "<open>",
        "add_statement": "<add>",
        "assign_statement": "<assign>",
        "sort_statement": "<sort>",
        "show_statement": "<show>",
        "when_statement": "<when>",
        "for_statement": "<for>"
    }

    productions.append(
        f"<statement> ::= {names[p.slice[1].type]}"
    )


def p_declare(p):
    "declare : LIST ID"
    p[0] = ("declare", p[2])
    productions.append('<declare> ::= "list" <id>')


def p_open_statement(p):
    "open_statement : OPEN ID"
    p[0] = ("open", p[2])
    productions.append('<open> ::= "open" <id>')


def p_add_statement(p):
    "add_statement : ADD ID piece"
    p[0] = ("add", p[2], p[3])
    productions.append('<add> ::= "add" <id> <piece>')


def p_piece(p):
    "piece : PIECE LEFT_PAREN piece_fields RIGHT_PAREN"
    p[0] = ("piece", p[3])
    productions.append('<piece> ::= "piece" "(" <piece_fields> ")"')


def p_piece_fields(p):
    "piece_fields : TYPE STRING_CONST COMMA COLOR STRING_CONST COMMA SEASON STRING_CONST COMMA OCCASION STRING_CONST COMMA PRICE NUMBER_CONST"
    p[0] = (
        ("type", p[2]),
        ("color", p[5]),
        ("season", p[8]),
        ("occasion", p[11]),
        ("price", p[14])
    )
    productions.append(
        '<piece_fields> ::= "type" <string> "," "color" <string> "," '
        '"season" <string> "," "occasion" <string> "," "price" <number>'
    )


def p_assign_statement(p):
    "assign_statement : ID ASSIGN expression"
    p[0] = ("assign", p[1], p[3])
    productions.append("<assign> ::= <id> '=' <expression>")


def p_expression_pick(p):
    "expression : pick"
    p[0] = p[1]
    productions.append("<expression> ::= <pick>")


def p_expression_arith(p):
    "expression : arith"
    p[0] = p[1]
    productions.append("<expression> ::= <arith>")


def p_pick(p):
    "pick : PICK ID WHERE condition"
    p[0] = ("pick", p[2], p[4])
    productions.append('<pick> ::= "pick" <id> "where" <condition>')


def p_sort_statement(p):
    "sort_statement : SORT ID BY field order"
    p[0] = ("sort", p[2], p[4], p[5])
    productions.append('<sort> ::= "sort" <id> "by" <field> <order>')


def p_show_expression(p):
    "show_statement : SHOW expression"
    p[0] = ("show", p[2])
    productions.append('<show> ::= "show" <expression>')


def p_show_string(p):
    "show_statement : SHOW STRING_CONST"
    p[0] = ("show", p[2])
    productions.append('<show> ::= "show" <string>')


def p_order(p):
    """order : ASC
             | DESC"""
    p[0] = p[1]

    if p.slice[1].type == "ASC":
        productions.append('<order> ::= "asc"')
    else:
        productions.append('<order> ::= "desc"')


def p_when_statement(p):
    """when_statement : WHEN condition statements END
                      | WHEN condition statements OTHERWISE statements END"""
    if len(p) == 5:
        p[0] = ("when", p[2], p[3], None)
        productions.append(
            '<when> ::= "when" <condition> <statements> "end"'
        )
    else:
        p[0] = ("when", p[2], p[3], p[5])
        productions.append(
            '<when> ::= "when" <condition> <statements> '
            '"otherwise" <statements> "end"'
        )


def p_for_statement(p):
    "for_statement : FOR EACH ID IN ID statements END"
    p[0] = ("for", p[3], p[5], p[6])
    productions.append(
        '<for> ::= "for" "each" <id> "in" <id> <statements> "end"'
    )


def p_condition_single(p):
    "condition : and_cond"
    p[0] = p[1]
    productions.append("<condition> ::= <and_cond>")


def p_condition_or(p):
    "condition : condition OR and_cond"
    p[0] = ("or", p[1], p[3])
    productions.append('<condition> ::= <condition> "or" <and_cond>')


def p_and_cond_single(p):
    "and_cond : comparison"
    p[0] = p[1]
    productions.append("<and_cond> ::= <comparison>")


def p_and_cond_multiple(p):
    "and_cond : and_cond AND comparison"
    p[0] = ("and", p[1], p[3])
    productions.append('<and_cond> ::= <and_cond> "and" <comparison>')


def p_comparison_values(p):
    "comparison : value comp_op value"
    p[0] = ("comparison", p[1], p[2], p[3])
    productions.append("<comparison> ::= <value> <comp_op> <value>")


def p_comparison_parentheses(p):
    "comparison : LEFT_PAREN condition RIGHT_PAREN"
    p[0] = p[2]
    productions.append(
        '<comparison> ::= "(" <condition> ")"'
    )


def p_comp_op(p):
    """comp_op : IS
               | IS NOT
               | LESS
               | LESS_EQUAL
               | GREATER
               | GREATER_EQUAL"""
    if len(p) == 3:
        p[0] = "is not"
        productions.append('<comp_op> ::= "is not"')
    else:
        p[0] = p[1]

        operators = {
            "IS": "is",
            "LESS": "<",
            "LESS_EQUAL": "<=",
            "GREATER": ">",
            "GREATER_EQUAL": ">="
        }

        productions.append(
            f'<comp_op> ::= "{operators[p.slice[1].type]}"'
        )


def p_value(p):
    """value : STRING_CONST
             | NUMBER_CONST
             | ID
             | field
             | field_access
             | count_call"""
    p[0] = p[1]

    names = {
        "STRING_CONST": "<string>",
        "NUMBER_CONST": "<number>",
        "ID": "<id>",
        "field": "<field>",
        "field_access": "<field_access>",
        "count_call": "<count_call>"
    }

    productions.append(
        f"<value> ::= {names[p.slice[1].type]}"
    )


def p_field_access(p):
    "field_access : ID DOT field"
    p[0] = ("field_access", p[1], p[3])
    productions.append('<field_access> ::= <id> "." <field>')


def p_count_call(p):
    "count_call : COUNT LEFT_PAREN ID RIGHT_PAREN"
    p[0] = ("count", p[3])
    productions.append('<count_call> ::= "count" "(" <id> ")"')


def p_field(p):
    """field : TYPE
             | COLOR
             | SEASON
             | OCCASION
             | PRICE"""
    p[0] = p[1]

    field_names = {
        "TYPE": "type",
        "COLOR": "color",
        "SEASON": "season",
        "OCCASION": "occasion",
        "PRICE": "price"
    }

    productions.append(
        f'<field> ::= "{field_names[p.slice[1].type]}"'
    )


def p_arith_term(p):
    "arith : term"
    p[0] = p[1]
    productions.append("<arith> ::= <term>")


def p_arith_add(p):
    "arith : arith PLUS term"
    p[0] = ("+", p[1], p[3])
    productions.append('<arith> ::= <arith> "+" <term>')


def p_arith_subtract(p):
    "arith : arith MINUS term"
    p[0] = ("-", p[1], p[3])
    productions.append('<arith> ::= <arith> "-" <term>')


def p_term_factor(p):
    "term : factor"
    p[0] = p[1]
    productions.append("<term> ::= <factor>")


def p_term_multiply(p):
    "term : term MULTIPLY factor"
    p[0] = ("*", p[1], p[3])
    productions.append('<term> ::= <term> "*" <factor>')


def p_term_divide(p):
    "term : term DIVIDE factor"
    p[0] = ("/", p[1], p[3])
    productions.append('<term> ::= <term> "/" <factor>')


def p_factor_operand(p):
    "factor : operand"
    p[0] = p[1]
    productions.append("<factor> ::= <operand>")


def p_factor_negative(p):
    "factor : MINUS factor"
    p[0] = ("negative", p[2])
    productions.append('<factor> ::= "-" <factor>')


def p_factor_parentheses(p):
    "factor : LEFT_PAREN arith RIGHT_PAREN"
    p[0] = p[2]
    productions.append('<factor> ::= "(" <arith> ")"')


def p_operand(p):
    """operand : NUMBER_CONST
               | ID
               | field_access
               | count_call"""
    p[0] = p[1]

    names = {
        "NUMBER_CONST": "<number>",
        "ID": "<id>",
        "field_access": "<field_access>",
        "count_call": "<count_call>"
    }

    productions.append(
        f"<operand> ::= {names[p.slice[1].type]}"
    )


def p_error(p):
    if p:
        message = (
            f"Line {p.lineno}: syntax error at "
            f"'{p.value}' (token {p.type})"
        )
    else:
        message = "Syntax error: unexpected end of input"

    syntax_errors.append(message)


parser = yacc.yacc(
    start=start,
    debug=False,
    write_tables=False
)
