#!/usr/local/bin/python3
# assign.py : Assign people to teams
#
# Code by: Renuka Srishti rsrishti
#
# Based on skeleton code by R. Shah and D. Crandall, January 2021
#

import sys
import time
from collections import defaultdict
import random
import copy
import heapq


class SearchNode:
    def __init__(self, user_id):
        self.user_id = user_id
        self.complaint = 0
        self.available_user_ids = []
        self.graph = None
        self.solution = defaultdict(list)
        self.is_complete = False

    def __str__(self) -> str:
        return f'Node: {self.node}\nParent: {self.parent}\nPosition: {self.position}'

    def __repr__(self) -> str:
        return f'Node: {self.user_id}\nf: {self.complaint}'

    def __lt__(self, other):
        return self.complaint < other.complaint

    # Calculating the number of complaints
    def get_complaints(self, graph):
        current_solution = self.solution
        self.complaint = 0
        for key, value in current_solution.items():
            # If size failing
            if graph[key]['requested_size'] != len(value):
                self.complaint = self.complaint + 1
            # If not assigned to want_to_work_with
            self.complaint = self.complaint + sum([1 for v in graph[key]['want_to_work_with'] if v not in value])
            # If assigned to dont want to work with
            self.complaint = self.complaint + sum([2 for v in graph[key]['does_not_want_to_work_with'] if v in value])

            for v in value:
                values = value.copy()
                values.remove(v)
                values.append(key)
                if graph[v]['requested_size'] != len(values):
                    self.complaint = self.complaint + 1

                # If not assigned to want_to_work_with
                self.complaint = self.complaint + sum(
                    [1 for v1 in graph[v]['want_to_work_with'] if v1 not in values])
                # If assigned to dont want to work with
                self.complaint = self.complaint + sum(
                    [2 for v1 in graph[v]['does_not_want_to_work_with'] if v1 in values])

# Creating a graph from input_file
def create_graph(input_file):
    graph = {}
    with open(input_file, "r") as file:
        for line in file:
            line_split = line.strip().split()

            user_id = line_split[0]

            want_to_work_with = line_split[1].split('-')
            requested_size = len(want_to_work_with) - 1
            want_to_work_with = [key for key in want_to_work_with if key != user_id and key != 'zzz']

            does_not_want_to_work_with = line_split[2].split(',')
            does_not_want_to_work_with = [key for key in does_not_want_to_work_with if key != '_']

            max_complaint = 1 + len(does_not_want_to_work_with) * 2 + len(want_to_work_with)

            graph[user_id] = {'want_to_work_with': want_to_work_with,
                              'does_not_want_to_work_with': does_not_want_to_work_with,
                              'requested_size': requested_size,
                              'max_complaint': max_complaint}

    return graph


def generate_groups(search_node):
    solution = {'assigned-groups': [], 'total-cost': 0}
    solution['total-cost'] = search_node.complaint
    for key, value in search_node.solution.items():
        if len(value) > 0:
            solution['assigned-groups'].append(f"{key}-{'-'.join(list(value))}")
        else:
            solution['assigned-groups'].append(key)
    return solution


def is_complete(search_node, graph):
    values = [item for elem in search_node.solution.values() for item in elem]
    values.extend(list(search_node.solution.keys()))
    return len(values) == len(graph.keys()) and len(search_node.available_user_ids) == 0

# Working alone
def create_successor_with_no_partners(search_node, graph):
    c = copy.deepcopy(search_node)
    c_user_id = c.user_id[0]
    c.solution[c_user_id]
    c.get_complaints(graph)
    # update next user_id for this state
    next_user = get_next_user(c, graph)
    if next_user is not None:
        c.available_user_ids.remove(next_user)
        c.user_id = (next_user, graph[next_user])
    # is_complete
    c.is_complete = is_complete(c, graph)  # len(c.solution.keys()) == len(graph.keys()) and len(c.available_user_ids) == 0
    return c

# Working with one people from list or random
def create_successor_with_one_partner(search_node, graph):
    successors = []
    for work_with_user_id in graph[search_node.user_id[0]]['want_to_work_with']:
        if work_with_user_id in search_node.available_user_ids:
            c = copy.deepcopy(search_node)
            c_user_id = c.user_id[0]
            c_user_id_dict = c.user_id[1]
            c.solution[c_user_id].append(work_with_user_id)
            # update available nodes
            c.available_user_ids.remove(work_with_user_id)
            c.get_complaints(graph)
            # update next user_id for this state
            next_user = get_next_user(c, graph)
            if next_user is not None:
                c.available_user_ids.remove(next_user)
                c.user_id = (next_user, graph[next_user])
            # is_complete
            c.is_complete = is_complete(c, graph)
            successors.append(c)

    if len(search_node.available_user_ids) >= 1:
        # random
        c = copy.deepcopy(search_node)
        c_user_id = c.user_id[0]
        c_user_id_dict = c.user_id[1]
        work_with_user_id = random.choice(list(c.available_user_ids))
        c.solution[c_user_id].append(work_with_user_id)
        # update available nodes
        c.available_user_ids.remove(work_with_user_id)
        c.get_complaints(graph)
        # update next user_id for this state
        next_user = get_next_user(c, graph)
        if next_user is not None:
            c.available_user_ids.remove(next_user)
            c.user_id = (next_user, graph[next_user])
        # is_complete
        c.is_complete = is_complete(c, graph)
        successors.append(c)

    return successors

# Working with two people: one from list and one random, two from list and both random
def create_successor_with_two_partner(search_node, graph):
    successors = []

    if len(graph[search_node.user_id[0]]['want_to_work_with']) == 2 and sum(
            [1 for v in graph[search_node.user_id[0]]['want_to_work_with'] if
             v in search_node.available_user_ids]) == 2:
        # both from want to work with
        c = copy.deepcopy(search_node)
        c_user_id = c.user_id[0]
        c_user_id_dict = c.user_id[1]
        c.solution[c_user_id].extend(graph[search_node.user_id[0]]['want_to_work_with'])
        # update available nodes
        c.available_user_ids = c.available_user_ids - set(graph[search_node.user_id[0]]['want_to_work_with'])
        c.get_complaints(graph)
        # update next user_id for this state
        next_user = get_next_user(c, graph)
        if next_user is not None:
            c.available_user_ids.remove(next_user)
            c.user_id = (next_user, graph[next_user])
        # is_complete
        c.is_complete = is_complete(c, graph)
        successors.append(c)

        # one from want to work with and one random
        for work_with_user_id in graph[search_node.user_id[0]]['want_to_work_with']:
            c = copy.deepcopy(search_node)
            c_user_id = c.user_id[0]
            c.solution[c_user_id].append(work_with_user_id)
            random_user_id = random.choice(list(c.available_user_ids))
            c.solution[c_user_id].append(random_user_id)
            # update available nodes
            c.available_user_ids = c.available_user_ids - {work_with_user_id, random_user_id}
            c.get_complaints(graph)
            # update next user_id for this state
            next_user = get_next_user(c, graph)
            if next_user is not None:
                c.available_user_ids.remove(next_user)
                c.user_id = (next_user, graph[next_user])
            # is_complete
            c.is_complete = is_complete(c, graph)
            successors.append(c)

    if len(graph[search_node.user_id[0]]['want_to_work_with']) == 2 and sum(
            [1 for v in graph[search_node.user_id[0]]['want_to_work_with'] if
             v in search_node.available_user_ids]) == 1:
        for work_with_user_id in graph[search_node.user_id[0]]['want_to_work_with']:
            if work_with_user_id in search_node.available_user_ids:
                c = copy.deepcopy(search_node)
                c_user_id = c.user_id[0]
                c.solution[c_user_id].append(work_with_user_id)
                random_user_id = random.choice(list(c.available_user_ids))
                c.solution[c_user_id].append(random_user_id)
                # update available nodes
                c.available_user_ids = c.available_user_ids - {work_with_user_id, random_user_id}
                c.get_complaints(graph)
                # update next user_id for this state
                next_user = get_next_user(c, graph)
                if next_user is not None:
                    c.available_user_ids.remove(next_user)
                    c.user_id = (next_user, graph[next_user])
                # is_complete
                c.is_complete = is_complete(c, graph)
                successors.append(c)

    # both random
    if len(search_node.available_user_ids) >= 2:
        # random
        c = copy.deepcopy(search_node)
        c_user_id = c.user_id[0]
        work_with_user_id = random.sample(list(c.available_user_ids), 2)
        c.solution[c_user_id].extend(work_with_user_id)
        # update available nodes
        c.available_user_ids = c.available_user_ids - set(work_with_user_id)
        c.get_complaints(graph)
        # update next user_id for this state
        next_user = get_next_user(c, graph)
        if next_user is not None:
            c.available_user_ids.remove(next_user)
            c.user_id = (next_user, graph[next_user])
        # is_complete
        c.is_complete = is_complete(c, graph)
        successors.append(c)
    return successors

# Generating the successors states
def generate_successors(graph, current_node):
    successors = []

    # Working alone
    successors.append(create_successor_with_no_partners(current_node, graph))

    # Working with one people from list or random
    successors.extend(create_successor_with_one_partner(current_node, graph))

    # Working with two people: one from list and one random, two from list and both random
    successors.extend(create_successor_with_two_partner(current_node, graph))

    # If you can not give all -> give partial
    # If you can not give anything -> do random
    return successors


def get_next_user(search_node, graph):
    next_user = None
    next_users_complaint = float('-inf')
    for k in search_node.available_user_ids:
        if graph[k]['max_complaint'] > next_users_complaint:
            next_user = k
            next_users_complaint = graph[k]['max_complaint']
    return next_user


def solver(input_file):
    graph = create_graph(input_file)
    best_combination = [None, float('inf')]
    source = list(sorted(graph.items(), key=lambda item: item[1]['max_complaint'], reverse=True))[0]
    source_node = SearchNode(source)
    source_node.available_user_ids = set(graph.keys()) - set([source_node.user_id[0]])     # Number of available user_ids to create groups
    source_node.complaint = 0
    source_node.is_complete = len(source_node.available_user_ids) == 0 and len(source_node.solution.keys()) == len(
        graph.keys())
    while True:
        fringe = []
        heapq.heappush(fringe, (-1, source_node))

        while len(fringe) > 0:
            current_node = heapq.heappop(fringe)[1]
            for successor in generate_successors(graph, current_node):
                if successor.is_complete and successor.complaint < best_combination[1]:
                    best_combination = [successor, successor.complaint]
                    yield generate_groups(best_combination[0])

                elif not successor.is_complete and successor.complaint < best_combination[1]:
                    heapq.heappush(fringe, (successor.complaint, successor))


if __name__ == "__main__":
    if(len(sys.argv) != 2):
        raise(Exception("Error: expected an input filename"))

    for result in solver(sys.argv[1]):
        print("----- Latest solution:\n" + "\n".join(result["assigned-groups"]))
        print("\nAssignment cost: %d \n" % result["total-cost"])
