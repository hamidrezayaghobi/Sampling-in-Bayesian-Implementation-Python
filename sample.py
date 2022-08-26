import copy
import itertools
import os
import re
import json
import random as rnd
from random import random
from collections import defaultdict
import matplotlib.pyplot as plt


class Node:
    node_list = []

    def __init__(self, name, p, parents_name=None):
        self.name = name
        self.p = p
        self.parents_name = parents_name
        self.node_list.append(self)

    def get_parents(self):
        parents = []
        if self.parents_name is None:
            return parents
        for node in self.node_list:
            if node.name in self.parents_name:
                parents.append(node)
        return parents

    @staticmethod
    def get_node_by_name(name):
        for node in Node.node_list:
            if node.name == name:
                return node

    @staticmethod
    def has_node(name):
        for node in Node.node_list:
            if name == node.name:
                return True
        return False

    visited = []
    stack = []

    @staticmethod
    def topological_sort_util(v, visited, stack, node_name_dict, name_node_dict):
        node = node_name_dict[v]
        Node.visited[v] = True

        for parent_node in node.get_parents():
            i = name_node_dict[parent_node]
            if not visited[i]:
                Node.topological_sort_util(i, visited, stack, node_name_dict, name_node_dict)

        stack.insert(0, node.name)

    @staticmethod
    def topo_sort():
        node_name_dict = {}
        name_node_dict = {}
        x = Node.node_list
        for index, node in enumerate(Node.node_list):
            node_name_dict[index] = node
            name_node_dict[node] = index

        Node.visited = [False] * len(Node.node_list)
        Node.stack = []

        for i in range(len(Node.node_list)):
            if not Node.visited[i]:
                Node.topological_sort_util(i, Node.visited, Node.stack, node_name_dict, name_node_dict)

        Node.stack.reverse()
        return Node.stack


# def get_input_from_file():


# def get_input():
#     node_number = int(input())
#     name_number_dcit = {}
#     for node in range(node_number):
#         i = node + 1
#         node_name = input()
#         name_number_dcit[node_name] = i
#         parent_or_probability = input()
#
#         if bool(re.match("([A-Z])+(\s[A-Z])*", parent_or_probability)):
#             parent_list = parent_or_probability.split()
#             probability = []
#             for ii in range(2 ** len(parent_list)):
#                 probability.append(input())
#             Node(node_name, probability, parent_list)
#
#         else:
#             probability = float(parent_or_probability)
#             Node(node_name, probability)
#
#     # for node_name, id in name_number_dcit.items():
#     #     node = Node.get_node_by_name(node_name)
#     #     if node.parents_name == None:
#     #         continue
#     #     parents = []
#     #     for parent in node.parents_name:
#     #         parents.append(name_number_dcit[parent])
#     #     prob = copy.copy(node.p)
#     #     prob.reverse()
#     #     cpt = []
#     #     for p in prob:
#     #         test = p.split()
#     #         test = test[-1]
#     #         test = float(test)
#     #         cpt.append(test)
#
#     return name_number_dcit


def prior_sampling(sorted_list, sample_count, query):
    prior_sample = []
    for count in range(sample_count):
        variable_dict = {}
        for node_name in sorted_list:
            node = Node.get_node_by_name(node_name)
            if node.parents_name is None:
                probability = random()
                if probability <= node.p:
                    variable_dict[node.name] = 1
                else:
                    variable_dict[node.name] = 0
                continue

            parent_list = node.parents_name
            parents_probability = node.p

            for parent in parent_list:
                parent_variable = variable_dict[parent]

                new_list = []
                for parent_probability in parents_probability:
                    if parent_probability.startswith(str(parent_variable)):
                        new_list.append(parent_probability[2:])

                parents_probability = copy.copy(new_list)

            probability = random()
            if probability <= float(parents_probability[0]):
                variable_dict[node.name] = 1
            else:
                variable_dict[node.name] = 0
            continue
        prior_sample.append(variable_dict)

    wanted = query[0]
    given = query[1]
    filtered_sample = []
    for sample in prior_sample:
        if given.items() <= sample.items():
            filtered_sample.append(sample)

    all_count = len(filtered_sample)
    if (all_count == 0):
        return 0
    count = 0

    for sample in filtered_sample:
        if wanted.items() <= sample.items():
            count += 1

    return count / all_count


def rejection_sampling(sorted_list, sample_count, query):
    count = 0
    wanted = query[0]
    given = query[1]
    rejection_sample = []
    while count < sample_count:
        variable_dict = {}
        for node_name in sorted_list:
            node = Node.get_node_by_name(node_name)
            if node.parents_name is None:
                probability = random()
                value = None
                if probability <= node.p:
                    value = 1
                else:
                    value = 0
                if node.name in given.keys():
                    if not {node.name: value}.items() <= given.items():
                        break
                variable_dict[node.name] = value
                continue

            parent_list = node.parents_name
            parents_probability = node.p

            for parent in parent_list:
                parent_variable = variable_dict[parent]

                new_list = []
                for parent_probability in parents_probability:
                    if parent_probability.startswith(str(parent_variable)):
                        new_list.append(parent_probability[2:])

                parents_probability = copy.copy(new_list)

            probability = random()
            value = None
            if probability <= float(parents_probability[0]):
                value = 1
            else:
                value = 0

            if node.name in given.keys():
                if not {node.name: value}.items() <= given.items():
                    break
            variable_dict[node.name] = value
            continue
        if len(variable_dict) != len(Node.node_list):
            continue
        rejection_sample.append(variable_dict)
        count += 1

    all_count = len(rejection_sample)
    count = 0
    for sample in rejection_sample:
        if wanted.items() <= sample.items():
            count += 1

    return count / all_count


def likelihood_sampling(sorted_list, sample_count, query):
    wanted = query[0]
    given = query[1]
    likelihood_sample = []
    likelihood_sample_w = []
    for count in range(sample_count):
        w = 1
        variable_dict = {}
        for node_name in sorted_list:
            node = Node.get_node_by_name(node_name)
            if node_name in given.keys():
                if node.parents_name is None:
                    w = w * node.p
                    variable_dict[node.name] = given[node.name]
                    continue

                parent_list = node.parents_name
                parents_probability = node.p

                for parent in parent_list:
                    parent_variable = variable_dict[parent]

                    new_list = []
                    for parent_probability in parents_probability:
                        if parent_probability.startswith(str(parent_variable)):
                            new_list.append(parent_probability[2:])

                    parents_probability = copy.copy(new_list)

                w = w * float(parents_probability[0])
                variable_dict[node.name] = given[node.name]
            else:
                if node.parents_name is None:
                    probability = random()
                    if probability <= node.p:
                        variable_dict[node.name] = 1
                    else:
                        variable_dict[node.name] = 0
                    continue

                parent_list = node.parents_name
                parents_probability = node.p

                for parent in parent_list:
                    parent_variable = variable_dict[parent]

                    new_list = []
                    for parent_probability in parents_probability:
                        if parent_probability.startswith(str(parent_variable)):
                            new_list.append(parent_probability[2:])

                    parents_probability = copy.copy(new_list)

                probability = random()
                if probability <= float(parents_probability[0]):
                    variable_dict[node.name] = 1
                else:
                    variable_dict[node.name] = 0
                continue

        likelihood_sample.append(variable_dict)
        likelihood_sample_w.append(w)

    all_sum = sum(likelihood_sample_w)
    w_sum = 0
    for sample, w in zip(likelihood_sample, likelihood_sample_w):
        if wanted.items() <= sample.items():
            w_sum += w

    return w_sum / all_sum


def gibbs_sampling(sorted_list, sample_count, query):
    wanted = query[0]
    given = query[1]
    not_given_node = list(sorted_list - given.keys())
    given_variable_dict = {}
    for given_node, given_p in given.items():
        given_variable_dict[given_node] = given_p

    variable_dict = copy.copy(given_variable_dict)
    for node_name in not_given_node:
        node = Node.get_node_by_name(node_name)
        random_value = rnd.randint(0, 1)
        variable_dict[node.name] = random_value

    gibbs_sample = []
    for count in range(sample_count):
        rnd.shuffle(not_given_node)
        variable_dict = copy.copy(variable_dict)
        for node_name in not_given_node:
            node = Node.get_node_by_name(node_name)
            new_given = copy.copy(variable_dict)
            del new_given[node.name]
            node_probability = None
            if not node.parents_name is None:
                parents_probability = node.p
                for parent in node.parents_name:
                    parent_variable = variable_dict[parent]
                    new_list = []
                    for probab in parents_probability:
                        if probab.startswith(str(parent_variable)):
                            new_list.append(probab[2:])

                    parents_probability = copy.copy(new_list)
                node_probability = float(parents_probability[0])
            else:
                node_probability = float(node.p)
            #True False
            test = [1 - node_probability, 1 * node_probability]
            for n in Node.node_list:
                if node.name == n.name:
                    return prior_sampling(sorted_list, 10000, query)
                    continue
                if n.parents_name is None:
                    continue
                if node.name in n.parents_name:
                    child_probability = n.p
                    index = 0
                    for parent in n.parents_name:
                        if parent == node.name:
                            index = 2
                            continue
                        parent_variable = variable_dict[parent]
                        new_list = []
                        for probab in child_probability:
                            if probab.startswith(str(parent_variable)):
                                new_list.append(probab[2:])

                        child_probability = copy.copy(new_list)
                    first = float(child_probability[0].split()[-1])
                    second = float(child_probability[1].split()[-1])
                    test[0] = test[0] * first
                    test[1] = test[1] * second

            probebility = test[1] / sum(test)
            rand = random()
            if rand <= probebility:
                variable_dict[node_name] = 1
            else:
                variable_dict[node_name] = 0
        gibbs_sample.append(variable_dict)


    all_count = len(gibbs_sample)
    count = 0

    for sample in gibbs_sample:
        if wanted.items() <= sample.items():
            count += 1

    return count / all_count



# name_number_dcit = get_input()
# sorted_list = Node.topo_sort()
#
# x = [[{"D": 1}, {"A": 1}], [{"A": 1 , "B" : 1}, {"C": 1 , "D" : 1}]]
#
#
# #tebgh ghanone adade bozorg
# real_value = rejection_sampling(sorted_list, 100000, x[0])
#
# print(real_value)
# print(prior_sampling(sorted_list, 1000, x[0]))
# print(rejection_sampling(sorted_list, 1000, x[0]))
# print(likelihood_sampling(sorted_list, 1000, x[0]))
# print(gibbs_sampling(sorted_list, 10000, x[0]))


def tet():
    node_number = int(input())
    for node in range(node_number):
        i = node + 1
        node_name = input()
        parent_or_probability = input()

        if bool(re.match("([A-Z])+(\s[A-Z])*", parent_or_probability)):
            parent_list = parent_or_probability.split()
            probability = []
            for ii in range(2 ** len(parent_list)):
                probability.append(input())
            Node(node_name, probability, parent_list)

        else:
            probability = float(parent_or_probability)
            Node(node_name, probability)


def write_output(input_path, query_path, graph_number):
    query_data = json.loads(open(query_path, 'r').readline())
    input_data = []
    with open(input_path) as file:
        while (line := file.readline().rstrip()):
            input_data.append(line)

    Node.node_list = []
    node_number = int(input_data[0])
    input_data = input_data[1:]
    for node in range(node_number):
        node_name = input_data[0]
        input_data = input_data[1:]
        parent_or_probability = input_data[0]
        input_data = input_data[1:]
        if bool(re.match("([A-Z])+(\s[A-Z])*", parent_or_probability)):
            parent_list = parent_or_probability.split()
            probability = []
            for ii in range(2 ** len(parent_list)):
                probability.append(input_data[0])
                input_data = input_data[1:]
            Node(node_name, probability, parent_list)

        else:
            probability = float(parent_or_probability)
            Node(node_name, probability)

    sorted_list = Node.topo_sort()
    file = open('./output/' + graph_number + '.txt', 'w+')
    prior_difs = []
    rejection_difs = []
    likelihood_difs = []
    gibbs_difs = []
    query_number = []
    for index, query in enumerate(query_data):
        # Law Of Large Numbers
        real_value = rejection_sampling(sorted_list, 100000, query)

        query_number.append(index + 1)
        prior_dif = round(abs(prior_sampling(sorted_list, 1000, query) - real_value), 5)
        prior_difs.append(prior_dif)
        rejection_dif = round(abs(rejection_sampling(sorted_list, 1000, query) - real_value), 5)
        rejection_difs.append(rejection_dif)
        likelihood_dif = round(abs(likelihood_sampling(sorted_list, 1000, query) - real_value), 5)
        likelihood_difs.append(likelihood_dif)
        gibbs_dif = round(abs(gibbs_sampling(sorted_list, 1000, query) - real_value), 5)
        gibbs_difs.append(gibbs_dif)
        file.write(f"{real_value} {prior_dif} {rejection_dif} {likelihood_dif} {gibbs_dif} \n")
        print(f"{real_value} {prior_dif} {rejection_dif} {likelihood_dif} {gibbs_dif}")

    plt.figure()
    plt.plot(query_number, prior_difs, marker='.', markersize=10, label="Prior")
    plt.plot(query_number, rejection_difs, marker='.', markersize=10, label="Rejection")
    plt.plot(query_number, likelihood_difs, marker='.', markersize=10, label="Likelihood Weighting")
    plt.plot(query_number, gibbs_difs, marker='.', markersize=10, label="Gibbs")
    plt.legend(loc="upper right")
    plt.savefig('./output/' + graph_number + '.png')
    file.close()


if __name__ == '__main__':
    os.makedirs("./output", exist_ok=True)
    for folder_name in os.listdir("./inputs"):
        input_path = "./inputs/" + folder_name + "/input.txt"
        query_path = "./inputs/" + folder_name + "/q_input.txt"
        write_output(input_path, query_path, folder_name)