from mcts_node import MCTSNode
from random import choice
from math import sqrt, log, inf
import time

num_nodes = 1000
explore_faction = 10.

id_coeff = [0, 1, -1]


def calc_uct(node, identity):
    #determine uct rating of given node
    wins = node.wins*id_coeff[identity]
    return wins/node.visits + explore_faction*sqrt(log(node.parent.visits)/node.visits)


def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 1 or 2.

    Returns:        A node from which the next stage of the search can proceed.
   
    """
    #UCT based selection
    current_node = node
    while not current_node.untried_actions and current_node.child_nodes:
        best_uct = -inf
        next_node = None
        for _, child in current_node.child_nodes.items():
            child.visits += 1
            child_uct = calc_uct(child, identity)
            if child_uct > best_uct:
                next_node = child
                best_uct = child_uct
        current_node = next_node
    return current_node #"leaf" found by taking highest UCT actions


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    new_action = node.untried_actions.pop(0)
    state = board.next_state(state, new_action)
    new_node = MCTSNode(node, new_action, board.legal_actions(state))
    node.child_nodes[new_action] = new_node
    return new_node


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """
    while not board.is_ended(state):
        #choice selects a legal action at random
        rand_action = choice(board.legal_actions(state))
        #we follow the ouctome of that action until the end
        state = board.next_state(state, rand_action)
    return state #remember all point values are for player 1

def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    node.visits += 1
    #Total score of the whole path to get to that node
    node.wins += won #won should be -1 for loss, 0 for draw, 1 for win
    while node.parent:
        node.parent.visits +=1
        node.parent.wins += won
        node = node.parent


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))
    start_time = time.time()
    #print(time())
    #print(start_time)
    for _ in range(num_nodes):
        #timer for extra credit, was not used in experiments 1 and 2
        elapsed_time = time.time() - start_time
        if elapsed_time == 1:
            break
        #print(elapsed_time)#test
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Do MCTS - This is all you!
        node = traverse_nodes(node, board, sampled_game, identity_of_bot)
        #update state with actions taken to select selected_node
        selected_node = node
        select_actions = []
        while selected_node.parent:
            select_actions.append(selected_node.parent_action)
            selected_node = selected_node.parent
        select_actions.reverse()
        for action in select_actions:
            sampled_game = board.next_state(sampled_game, action)
        #handle possible selection of terminal node
        if not node.untried_actions:
            won = board.points_values(sampled_game)[1]
        else:
            #expand from selection
            node = expand_leaf(node, board, sampled_game)
            #update simulated state
            sampled_game = board.next_state(sampled_game, node.parent_action)
            # simulate game from new node
            sampled_game = rollout(board, sampled_game)
            won = board.points_values(sampled_game)[1]
        # update tree
        backpropagate(node, won)

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    best_winrate = -inf
    if identity_of_bot == 1:
        sign = 1
    else:
        sign = -1
    for action, child in root_node.child_nodes.items():
        child_winrate = (child.wins/child.visits)*sign
        if child_winrate > best_winrate:
            best_action = action
            best_winrate = child_winrate

    #I think this is ok to leave in? rollout_bot does something similar
    #print("mcts modified #", identity_of_bot, "picking", best_action, "with winrate =", best_winrate)
    return best_action
