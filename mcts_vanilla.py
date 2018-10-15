
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log, inf

num_nodes = 1000
explore_faction = 2.


def calc_uct(node, identity):
    node.visits += 1
    #determine UTC rating of given node
    if identity == 1:
        wins = node.wins
    else:
        #reverse wins if blue because they are stored as wins for P1
        wins = node.wins*-1
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
    while current_node.child_nodes:
        best_utc = -inf
        next_node = None
        for _, child in current_node.child_nodes.items():
            child_uct = calc_uct(child, identity)
            if child_uct > best_utc:
                next_node = child
        current_node = next_node
        state = board.next_state(state, next_node.parent_action) #incrememnt state of sim
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
    if node.untried_actions:
        #print("avalible actions")#test
        new_nodes = []
        for action in board.legal_actions(state):
            new_state = board.next_state(state, action)
            new_nodes.append(MCTSNode(node, action, board.legal_actions(new_state)))
        next_node = choice(new_nodes) #select one of the new leaves at random to use
        return next_node, new_nodes
    else:
        #print("no untried actions")#test
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
    return board.points_values(state)[1] #remember all point values are for player 1

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
        next_node, new_nodes = expand_leaf(node, board, sampled_game)
        if next_node:
            sampled_game = board.next_state(sampled_game, next_node.parent_action)
            for new_node in new_nodes:
                node.child_nodes[new_node.parent_action] = new_node
            node.child_nodes[next_node.parent_action] = next_node
            node = next_node
            #update sampled_game state for rollout
            #simulate game from new node
            won = rollout(board, sampled_game)
            #update tree
        else:
            won = board.points_values(sampled_game)[1]
        backpropagate(node, won)

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    best_winrate = -inf
    if identity_of_bot == 1:
        for action in board.legal_actions(state):
            if action in root_node.child_nodes:
                #print("considering")#test of how many actions are considered
                child = root_node.child_nodes[action]
                child_winrate = child.wins/child.visits
                if child_winrate > best_winrate:
                    best_action = action
                    best_winrate = child_winrate
    #branch to account for negative blue winrates
    else:
        for action in board.legal_actions(state):
            if action in root_node.child_nodes:
                child = root_node.child_nodes[action]
                child_winrate = (child.wins/child.visits)*-1
                if child_winrate > best_winrate:
                    best_action = action
                    best_winrate = child_winrate

    #I think this is ok to leave in? rollout_bot does something similar
    print("mcts vanilla #", identity_of_bot, "picking", best_action, "with winrate =", best_winrate)
    return best_action
