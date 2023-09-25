import pandas as pd
import pydotplus


def create_dfa_graph(states, acceptance_states, transitions, symbols, start_state):
    # Convert sets to strings
    states = [str(state) for state in states]
    start_state = str(start_state.pop())
    acceptance_states = [str(state) for state in acceptance_states]

    # Create a DOT format representation of the DFA
    dot = pydotplus.Dot()
    dot.set_rankdir("LR")  # Use 'TB' for top to bottom layout
    dot.set_prog("neato")

    # Create nodes for each state
    state_nodes = {}
    for state in states:
        node = pydotplus.Node(state)
        node.set_shape("circle")
        for final_state in acceptance_states:
            if final_state in state:
                node.set_shape("doublecircle")

        if start_state in state:
            node.set_shape("circle")
            node.set_style("filled")

        node.set_fontsize(12)  # Set font size
        node.set_width(0.6)  # Set the desired width
        node.set_height(0.6)  # Set the desired height
        state_nodes[state] = node
        dot.add_node(node)

    # Add transitions as edges
    for (source, symbol, target) in transitions:
        edge = pydotplus.Edge(
            state_nodes[str(source)], state_nodes[str(target)], label=symbol)
        dot.add_edge(edge)

    return dot


def merge_equivalent_pairs(equivalent_pairs):
    merged_states = []

    for pair in equivalent_pairs:
        merged = False
        for i, merged_state in enumerate(merged_states):
            # Check if the pair intersects with the merged state
            if any(state in pair for state in merged_state):
                # Merge the pair into the existing merged state
                merged_states[i] = merged_state.union(set(pair))
                merged = True
                break

        if not merged:
            # If the pair didn't intersect with any existing merged states, add it as a new merged state
            merged_states.append(set(pair))

    return [''.join(sorted(list(merged_state))) for merged_state in merged_states]


def main(states, symbols, transitions, start_state, final_states):
    states = {'{0}', '{1}'}
    start_state = {'{0}'}
    final_states = {'{1}'}
    symbols = {'a'}
    transitions = {
        ('{0}', 'a', '{1}')
    }

    # Initialize the table with all pairs of states
    table = pd.DataFrame(index=list(states), columns=list(states), data='')

    # For each pair (p, q), mark it if p ∈ F and q ∉ F
    for p in states:
        for q in states:
            if p == q:
                table.at[p, q] = '0'
            if (p in final_states) ^ (q in final_states):
                table.at[p, q] = 'X'

    # Mark all distinguishable pairs
    # "If there is an unmarked pair (p, q), mark it if the pair {δ (p, A), δ (q, A)} is marked"
    changed = True
    while changed:
        changed = False
        for p in states:
            for q in states:
                if table.at[p, q] != '0':
                    if table.at[p, q] == '':
                        distinguishable = False
                        for symbol in symbols:
                            p_next = None
                            q_next = None
                            for transition in transitions:
                                if transition[0] == p and transition[1] == symbol:
                                    p_next = transition[2]
                                if transition[0] == q and transition[1] == symbol:
                                    q_next = transition[2]
                            if table.at[p_next, q_next] == 'X':
                                distinguishable = True
                                break
                        if distinguishable:
                            table.at[p, q] = 'X'
                            changed = True

    # Collect the undistinguishable pairs as sets
    equivalent_pairs = set()
    for p in states:
        for q in states:
            if table.at[p, q] == '':
                equivalent_pairs.add(frozenset([p, q]))

    # this whole part is to remove the original states and add the combined ones,
    # future me: i know it looks ugly but it works

    equivalent_pairs_list = []
    for set_tuple in equivalent_pairs:
        equivalent_pairs_list.append(list(set_tuple))

    sets_to_remove = set(
        [item for sublist in equivalent_pairs_list for item in sublist])

    merged_states = merge_equivalent_pairs(equivalent_pairs)

    # Reindex the DataFrame to ensure the order
    # Pandas likes to shuffle the table for some reason, its just to format
    table = table.reindex(sorted(table.columns), axis=1)
    table = table.reindex(sorted(table.index), axis=0)

    print(table)

    new_states = states.copy()
    for item in sets_to_remove:
        new_states.discard(item)

    new_states.update(merged_states)

    print(new_states)

    # Initialize a list to store the new transitions
    new_transitions = []

    # Replace the old states in transitions with the merged equivalents
    for transition in transitions:
        old_state, symbol, new_state = transition
        for merged_state in merged_states:
            if old_state in merged_state:
                old_state = merged_state
            if new_state in merged_state:
                new_state = merged_state
        new_transition = (old_state, symbol, new_state)
        new_transitions.append(new_transition)

    # Convert the list of new transitions to a set to remove duplicates
    new_transitions = list(set(new_transitions))

    # Print the new transitions
    print("New Transitions:", set(new_transitions))

    return new_states, symbols, new_transitions, list(start_state), list(final_states)
    # pydotplus.find_graphviz()
    #
    # graph = create_dfa_graph(new_states, final_states,
    #                          new_transitions, symbols, start_state)
    #
    # # Save or display the graph
    # dot_file_path = "dfa_graph_minimized.dot"
    # png_file_path = "dfa_graph_minimized.png"
    # graph.write(dot_file_path, format="dot")  # Save DOT file
    # graph.write_png(png_file_path)  # Save PNG file
    # graph.write_svg("dfa_graph_minimized.svg")  # Save SVG file

