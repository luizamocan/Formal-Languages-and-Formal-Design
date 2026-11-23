
from pathlib import Path


class FiniteAutomaton:
    def __init__(self, definition):
        self.name = definition["name"]
        self.states = definition["states"]
        self.alphabet = definition["alphabet"]
        self.initial_state = definition["initial"]
        self.final_states = definition["final"]

        # convert transitions into a lookup dictionary
        self.transitions = {}

        for source, symbol, destination in definition["transitions"]:
            self.transitions[(source, symbol)] = destination

    def classify_symbol(self, character):
        """Convert a character into an alphabet category."""

        if self.name == "IDENTIFIER":
            if character.isascii() and character.isalpha():
                return "LETTER"
            if character.isascii() and character.isdigit():
                return "DIGIT"
            if character == "_":
                return "UNDERSCORE"

        elif self.name == "NUMBER":
            if character == "0":
                return "ZERO"
            if character in "123456789":
                return "NONZERO_DIGIT"
            if character in "0123456789":
                return "DIGIT"
            if character == ".":
                return "DOT"


        elif self.name == "STRING":

            if character == '"':
                return "QUOTE"

            allowed_characters = (

                "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

                "abcdefghijklmnopqrstuvwxyz"

                "0123456789"

                " .,;:!?_()/'-&"

            )

            if character in allowed_characters:
                return "STRING_CHAR"

            return None

        return None

    def accepts(self, token):
        """Return True if the complete token is accepted by the FA."""

        state = self.initial_state

        for character in token:
            if self.name == "NUMBER":
                if state == "n0":
                    if character == "0":
                        symbol = "ZERO"
                    elif character in "123456789":
                        symbol = "NONZERO_DIGIT"
                    elif character == ".":
                        symbol = "DOT"
                    else:
                        return False
                else:
                    if character.isascii() and character.isdigit():
                        symbol = "DIGIT"
                    elif character == ".":
                        symbol = "DOT"
                    else:
                        return False
            else:
                symbol = self.classify_symbol(character)

            if symbol not in self.alphabet:
                return False

            next_state = self.transitions.get((state, symbol))

            if next_state is None:
                return False

            state = next_state

        return state in self.final_states


def load_automata(filename=None):
    """Load and validate the automata defined in automata.txt."""

    if filename is None:
        filename = Path(__file__).with_name("automata.txt")
    else:
        filename = Path(filename)

    from fa_to_rg import read_automata, validate_automaton

    definitions = read_automata(filename)
    automata = {}

    for definition in definitions:
        validate_automaton(definition)
        automata[definition["name"]] = FiniteAutomaton(definition)

    return automata
