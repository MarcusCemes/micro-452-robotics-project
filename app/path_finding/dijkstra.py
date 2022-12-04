from app.path_finding.path_optimiser import PathOptimiser
from app.path_finding.types import Algorithm, Location, WeightedGraph
from app.path_finding.utils import PriorityQueue

Cost = dict[Location, tuple[Location | None, float]]


INF = float('inf')


class Dijkstra(Algorithm):

    def __init__(self, graph: WeightedGraph, optimise=True):
        self.graph = graph
        self.optimise = optimise

    def find_path(
        self,
        start: Location,
        end: Location
    ) -> list[Location] | None:
        frontier = PriorityQueue()
        cost: Cost = {}

        frontier.put(start, 0)
        cost[start] = (None, 0)

        while not frontier.empty():
            current = frontier.get()

            if current == end:
                break

            (_, current_cost) = cost[current]

            for next in self.graph.neighbors(current, end):
                new_cost = current_cost + self.graph.cost(current, next)

                (_, old_cost) = cost.get(next, (None, INF))
                if new_cost < old_cost:
                    cost[next] = (current, new_cost)
                    frontier.put(next, new_cost)

        path = self._reconstruct_path(cost, end)

        if path and self.optimise:
            path = PathOptimiser(self.graph.map).optimise(path)

        return path

    def _reconstruct_path(
        self,
        cost: Cost,
        end: Location
    ) -> list[Location] | None:
        if end not in cost:
            return None

        (parent, _) = cost[end]
        path = [end]

        while parent != None:
            path.append(parent)
            (parent, _) = cost[parent]

        path.reverse()
        return path
