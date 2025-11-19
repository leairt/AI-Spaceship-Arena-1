import random
import config
import queue

class Algorithm:
    def get_path(self, state):
        pass


class ExampleAlgorithm(Algorithm):
    def get_path(self, state):
        path = []
        while not state.is_goal_state():
            possible_actions = state.get_legal_actions()
            action = possible_actions[random.randint(0, len(possible_actions) - 1)]
            path.append(action)
            state = state.generate_successor_state(action)
        return path


def news(item):
    x = item[1][0] - item[0][0]
    y = item[1][1] - item[0][1]
    if x < 0:
        return 1 # sever
    if x > 0:
        return 3 # jug
    if y > 0:
        return 2 # istok
    if y < 0:
        return 4 # zapad
    return 0


# Blue - DFS
class Blue(Algorithm):
    def get_path(self, state):
        stack = []
        possible_actions = state.get_legal_actions()
        # possible_actions.sort(key=lambda x:(x[0],news(x)), reverse=True)
        possible_actions.reverse()


        # possible_actions.sort(key=news, reverse=True)
        # possible_actions.sort(key=lambda x:(news(x),pos(x)), reverse=True)
        for next_action in possible_actions:
            stack.append((state, [], [], next_action))

        while stack:
            (s, visited, p, action) = stack.pop()
            s = s.generate_successor_state(action)
            if s in visited:
                continue
            visited.append(s)
            if s.is_goal_state():
                return p + [action]
            possible_actions = s.get_legal_actions()
            # possible_actions.sort(key=lambda x:(x[0],news(x)), reverse=True)
            # possible_actions.sort(key=news, reverse=True)
            # possible_actions.sort(key=lambda x: (news(x), x[0]), reverse=True)
            possible_actions.reverse()
            for next_action in possible_actions:
                stack.append((s, visited, p + [action], next_action))
        return []


# Red - BFS
class Red(Algorithm):
    def get_path(self, state):
        queue = []
        possible_actions = state.get_legal_actions()
        # possible_actions.sort(key=news, reverse=True)
        for next_action in possible_actions:
            queue.append((state, [], [], next_action))

        while queue:
            (s, visited, p, action) = queue.pop(0)
            s = s.generate_successor_state(action)
            if s in visited:
                continue
            visited.append(s)
            if s.is_goal_state():
                return p + [action]
            possible_actions = s.get_legal_actions()
            # possible_actions.sort(key=news, reverse=True)
            for next_action in possible_actions:
                queue.append((s, visited, p + [action], next_action))
        return []


# Black - Branch&Bound
class Black(Algorithm):
    def get_path(self, state):
        path = []
        stack = []
        min_cost = 0
        possible_actions = state.get_legal_actions()
        # possible_actions.sort(key=news, reverse=False)
        possible_actions.reverse()
        for next_action in possible_actions:
            stack.append((state, [], [], next_action, state.get_action_cost(next_action)))
        stack.sort(key=lambda x: x[4], reverse=True)
        while stack:
            (s, visited, p, action, c) = stack.pop()
            s = s.generate_successor_state(action)
            if 0 < min_cost < c:
                continue
            if s in visited:
                continue
            visited.append(s)
            if s.is_goal_state():
                min_cost = c
                path = p + [action]
            possible_actions = s.get_legal_actions()
            # possible_actions.sort(key=news, reverse=False)
            possible_actions.reverse()
            for next_action in possible_actions:
                stack.append((s, visited, p + [action], next_action, c + s.get_action_cost(next_action)))
            stack.sort(key=lambda x: x[4], reverse=True)
        return path


# White - A*
class White(Algorithm):
    def manhattan(self, state, action):
        h = 0
        pairs = []
        s = state.generate_successor_state(action)
        ships = self.get_spaceships(s)
        goals = self.get_goals(s)
        for ship in ships:
            for goal in goals:
                distance = abs(ship[0] - goal[0]) + abs(ship[1] - goal[1])
                pairs.append((ship, goal, distance))
        pairs.sort(key=lambda x: x[2], reverse=True)
        while ships:
            ship, goal, dist = pairs.pop()
            if ship in ships and goal in goals:
                h += dist
                ships.remove(ship)
                goals.remove(goal)
        return h

    def get_goals(self, state):
        result = []
        for i in range(0, config.M):
            for j in range(config.N):
                mask = 1 << (i * config.N + j)
                if (mask & state.goals) == mask:
                    result.append((i, j))
        return result

    def get_spaceships(self, state):
        result = []
        for i in range(0, config.M):
            for j in range(config.N):
                mask = 1 << (i * config.N + j)
                if (mask & state.spaceships) == mask:
                    result.append((i, j))
        return result

    def get_path(self, state):
        path = []
        stack = []
        min_cost = 0

        possible_actions = state.get_legal_actions()
        possible_actions.sort(key=news, reverse=False)
        possible_actions.reverse()
        for next_action in possible_actions:
            stack.append((state, [], [], next_action, state.get_action_cost(next_action), self.manhattan(state, next_action)))
        stack.sort(key=lambda x: x[4] + x[5], reverse=True)

        while stack:
            (s, visited, p, action, c, h) = stack.pop()
            s = s.generate_successor_state(action)
            if 0 < min_cost < c + h:
                continue
            if s in visited:
                continue
            visited.append(s)
            if s.is_goal_state():
                min_cost = c + h
                path = p + [action]
            possible_actions = s.get_legal_actions()
            possible_actions.sort(key=news, reverse=False)
            possible_actions.reverse()
            for next_action in possible_actions:
                stack.append((s, visited, p + [action], next_action, c + s.get_action_cost(next_action), self.manhattan(s, next_action)))
            stack.sort(key=lambda x: x[4] + x[5], reverse=True)
        return path