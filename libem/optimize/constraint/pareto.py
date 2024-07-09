"""
Given a list of objectives, pareto.py will return
the pareto front configurations of the objectives.

The pareto front is the set of configurations that
are not dominated by any other configuration.

The pareto front is calculated using the following
algorithm:

1. Sort the objectives in ascending order.
2. Initialize the pareto front as the first configuration.
3. For each configuration, check if it is dominated by
   any configuration in the pareto front. If it is not,
   add it to the pareto front.

The pareto front is returned as a list of values.
"""


def pareto(objectives):
    front = [objectives[0]]

    for objective in objectives[1:]:
        is_dominated = False

        for i, front in enumerate(front):
            if all(front[i] <= objective[i] for i in range(len(objective))):
                is_dominated = True
                break

        if not is_dominated:
            front.append(objective)

    return front
