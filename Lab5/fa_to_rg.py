from pathlib import Path

def read_automata(filename):
    """ Read multiple finite automata from a file"""

    automata = []
    current = None
    reading_transitions = False

    with open(filename, "r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()

            if not line:
                continue

            if line == "END":
                if current is not None:
                    automata.append(current)
                    current = None
                    reading_transitions = False
                continue

            #first line of each automaton is its name
            if current is None:
                current ={"name": line,
                          "states":set(),
                          "alphabet":set(),
                          "initial":None,
                          "final":set(),
                          "transitions":[]
                          }
                continue

            if line.startswith("states"):
                current["states"].update(line.split(":", 1)[1].split())

            elif line.startswith("alphabet"):
                current["alphabet"].update(line.split(":", 1)[1].split())

            elif line.startswith("initial"):
                current["initial"] = line.split(":", 1)[1].strip()

            elif line.startswith("final"):
                current["final"].update(line.split(":", 1)[1].split())

            elif line == "transitions:":
                reading_transitions = True

            elif reading_transitions:
                parts = line.split()

                if len(parts) !=3:
                    raise ValueError(f"Invalid transition line: {line}")

                source, symbol, destination = parts
                current["transitions"].append((source, symbol, destination))

        if current is not None:
            automata.append(current)

        return automata


def validate_automaton(automaton):
    states = automaton["states"]
    alphabet = automaton["alphabet"]

    if automaton["initial"] not in states:
        raise ValueError(
            f"{automaton['name']}: initial state is missing or invalid."
        )

    if not automaton["final"].issubset(states):
        raise ValueError(
            f"{automaton['name']}: a final state is not defined."
        )

    for source, symbol, destination in automaton["transitions"]:
        if source not in states or destination not in states:
            raise ValueError(
                f"{automaton['name']}: transition uses an unknown state."
            )

        if symbol not in alphabet:
            raise ValueError(
                f"{automaton['name']}: {symbol} is missing from the alphabet."
            )


def fa_to_rg(automaton):
    productions = {}

    for source, symbol,destination in automaton["transitions"]:
        production = f"{symbol} {destination.upper()}"

        productions.setdefault(source.upper(), []).append(production)

    for state in automaton["final"]:
        productions.setdefault(state.upper(), []).append("ε")

    return automaton["initial"].upper(), productions



def format_grammar(name, start_symbol, productions):
    lines = [
        f"{name} — Regular Grammar",
        f"Start symbol: {start_symbol}",
        ""
    ]

    for nonterminal, alternatives in productions.items():
        lines.append(f"{nonterminal} -> {' | '.join(alternatives)}")

    return "\n".join(lines)




def main():
    filename = Path(__file__).with_name("automata.txt")
    output_file = Path(__file__).with_name("regular_grammars.txt")

    automata = read_automata(filename)
    all_grammars = []

    for automaton in automata:
        validate_automaton(automaton)

        start_symbol, productions = fa_to_rg(automaton)

        grammar_text = format_grammar(
            automaton["name"],
            start_symbol,
            productions
        )

        print(grammar_text)
        all_grammars.append(grammar_text)

    output_file.write_text(
        "\n\n".join(all_grammars) + "\n",
        encoding="utf-8"
    )

    print(f"\nGrammars saved to: {output_file}")

if __name__ == "__main__":
    main()




