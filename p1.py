def epsilon(state, transitions):
    epsilon_closure_set = set(state)
    stack = list(state)

    while stack:
        current_state = stack.pop()
        epsilon_transitions = [
            t[2] for t in transitions if t[0] == current_state and t[1] == "lamda"
        ]
        for new_state in epsilon_transitions:
            if new_state not in epsilon_closure_set:
                epsilon_closure_set.add(new_state)
                stack.append(new_state)

    return epsilon_closure_set  # Convert to frozenset for set equality.


def move(state, symbol, transitions):
    move_set = set()

    for t in transitions:
        if t[0] in state and t[1] == symbol:
            move_set.add(t[2])

    return move_set


def dfa_nfa(states, symbols, start_state, final_states, transitions):
    dfa_states = [epsilon(start_state, transitions)]
    marked_states = []
    current_state = []
    dfa_transition = []

    while len(dfa_states) != len(marked_states):
        # basically, we keep track of any new states found
        current_state = dfa_states[len(marked_states)]
        marked_states.append(current_state)

        for x in symbols:
            # remember, new_state is one singular state in the context of a DFA, but composed of multiple NFA states.
            new_state = epsilon(move(current_state, x, transitions), transitions)
            if new_state not in dfa_states:
                dfa_states.append(new_state)
            if new_state == set():
                new_state = "∅"
            # stored in a key value manner, where the key is the current state and input combination, and the value is the new state
            dfa_transition.append((current_state, x, new_state))

    print(dfa_transition)


def main():
    dfa_nfa(
        {1, 2, 3, 4, 5},
        {"a", "b"},
        {1},
        {5},
        {
            (1, "lamda", 2),
            (1, "a", 3),
            (2, "a", 4),
            (2, "a", 5),
            (3, "b", 4),
            (4, "a", 5),
            (4, "b", 5),
        },
    )


if __name__ == "__main__":
    main()
