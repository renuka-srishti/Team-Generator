#### This repository contains assignment given by Prof. David Crandall during the Elements of Artificial Intelligence Spring 2021 class.
# Team-Generator
----------
# Choosing teams
## Introduction
Given input file from the survey contains each student’s response to survey's questions on a single line, separated by spaces.
Goal is to write a program to find an assignment of students to teams that minimizes the total number of complaints.<br>
## How you formulated the search problem:
We are starting the search by first satisfying the most restrictive user (user that can raise most complaints). We apply best first search on generated successor states based on the number of compliants that has been raised so far on the solution and yield the solution with minimum number of complaints.
## How to calculate max complaints:
Max complaint is the maxinum number of complaints a particular user can raise. It will happen when we don't satisfy any of the user's wish.
## What is the set of valid states, the successor function, the cost function, the goal state definition, and the initial state?<br>
Set of valid states: set of all possible groups<br>
The successor function: group with minimal number of complains<br>
The cost function: number of complaints in forming the groups <br>
The goal state: assigned groups with minimum number of complains till the grading program exit the program<br>
Initial state: most restricted user (with the highest anticipated complaints).
## How generating the successor states?<br>
Generating successor states in following ways:<br>
  1. Student working alone.<br>
  2. Student with one more student.<br>
  3. Student with other two students.<br>
  4. Using randomization in case we stuck with condition like this:
    A student wants to work with B and C. But, B, C does not want to work with A. In this case, we need to assign some students to form a group for A, atleast with the number of students he wants to work with. So, atleast he wont be complaining for group size.
```
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
```
## Get number of complaints<br>
```
def get_complaints(self, graph):
```
## How to know, when one state is complete?<br>
Check if all the keys in groups that is all students are covered in group formation process
```
def is_complete(search_node, graph):
    values = [item for elem in search_node.solution.values() for item in elem]
    values.extend(list(search_node.solution.keys()))
    return len(values) == len(graph.keys()) and len(search_node.available_user_ids) == 0
```    

## Input:<br>
A input text file contains student’s response to survey's questions on a single line, separated by spaces.
## Output:<br>
Assigned-groups with Assignment cost that is minimum number of complaints for those assigned groups.
