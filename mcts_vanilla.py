
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_faction = 2.


def calc_uct(node, identity):
    #determine UTC rating of given node
    if identity == 'red':
        wins = node.wins
    else:
        #reverse wins if blue because they are stored as wins for red
        wins = node.wins*-1
    return wins/node.visits + explore_faction*sqrt(log(node.parent.visits)/node.visits)


def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.
   
    """
    #UCT based selection
    current_node = node
    while current_node.child_nodes:
        next_node = (-1, None) #used to compare UCT ratings of nodes
        for child in current_node.child_nodes:
            child_uct = calc_uct(child, identity)
            if child_uct > next_node[0]:
                next_node = (child_uct, child)
        current_node = next_node[1]
    return current_node #leaf found by taking highest UCT actions


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    #choose first untried action
    new_action = node.untried_actions.pop(0)
    #add node based on that action
    new_state = board.next_state(state, new_action)
    new_node = MCTSNode(node, new_action, board.legal_actions(new_state))
    node.child_nodes[new_action] = new_node
    return new_node


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """
    pass


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    pass


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Do MCTS - This is all you!

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    return None
