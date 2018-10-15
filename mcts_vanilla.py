
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log, inf

num_nodes = 100
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
        next_utc_node = (-10000, None) #used to compare UCT ratings of nodes
        for _, child in current_node.child_nodes.items():
            child_uct = calc_uct(child, identity)
            if child_uct > next_utc_node[0]:
                next_utc_node = (child_uct, child)
        current_node = next_utc_node[1]
        state = board.next_state(state, next_utc_node[1].parent_action) #incrememnt state of sim
    #the description does not mention the state, but it is necessary
    return (current_node, state) #leaf found by taking highest UCT actions


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    #choose first untried action
    if node.untried_actions:
        new_action = node.untried_actions.pop(0)
        #add node based on that action
        new_state = board.next_state(state, new_action)
        new_node = MCTSNode(node, new_action, board.legal_actions(new_state))
        #the description does not mention the state, but it is necessary
        return (new_node, new_state)
    else:
        return (None, None)


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """
    while not board.is_ended(state):
        #choice selects a legal action at random
        rand_action = choice(board.legal_actions(state))
        #we follow the outcome of that action until the end
        state = board.next_state(state, rand_action)
    #i feel like we should return whether the state is a win or not, otherwise it doesn't make much sense
    return board.points_values(state)[1] #remember all point values are for 'red' or, player 1

def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    node.visits += 1
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

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Do MCTS - This is all you!
        node, sampled_game = traverse_nodes(node, board, sampled_game, identity_of_bot)
        #note that we need to append the child when we call expand_leaf
        new_node, new_game = expand_leaf(node, board, sampled_game)
        if new_node:
            sampled_game = new_game
            node.child_nodes[new_node.parent_action] = new_node
            #update sampled_game state for rollout
            #simulate game from new node
            won = rollout(board, sampled_game)
            #update tree
        else:
            new_node = node
            won = board.points_values(sampled_game)[1]
        backpropagate(new_node, won)
    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    if identity_of_bot == 'red':
        best_winrate = -inf
        for action in board.legal_actions(state):
            if action in root_node.child_nodes:
                child = root_node.child_nodes[action]
                if (child.wins/child.visits) > best_winrate:
                    best_action = action
    #branch to account for negative blue winrates
    else:
        best_winrate = inf
        for action in board.legal_actions(state):
            if action in root_node.child_nodes:
                child = root_node.child_nodes[action]
                if (child.wins/child.visits) < best_winrate:
                    best_action = action

    return best_action
