INF = 2 ** 32

class DVNode:
    """
    initial_vector: vector of initial weights to this nodes neighbors
    """
    def __init__(self, id, initial_vector):
        self.id = id
        self.num_nodes = len(initial_vector)
        self.table = []

        for row in range(self.num_nodes):
            r = []
            for col in range(self.num_nodes):
                if row == col:
                    r.append(initial_vector[col])
                else:
                    r.append(INF)
            self.table.append(r)

    def update_table(self, id_from, distance_vector):
        updated = False
        cost_to_source = self.table[id_from][id_from]

        for to in range(self.num_nodes):
            if to == self.id:
                continue
            for via in range(self.num_nodes):
                if via == self.id:
                    continue
                source_cost = distance_vector[to][via]
                if cost_to_source + source_cost < self.table[to][id_from]:
                    self.table[to][id_from] = cost_to_source + source_cost
                    updated = True
                    print(f'node {self.id} updating cost to {i} via {id_from} = {cost_to_source + source_cost}')

        return updated

    def print_shortest_paths(self):
        paths = [[INF, 0] for _ in range(self.num_nodes)]
        for to in range(self.num_nodes):
            for via in range(self.num_nodes):
                if self.table[to][via] < paths[to][0]:
                    paths[to] = [self.table[to][via], via]
        print(f'i am node {self.id}')
        for n in range(len(paths)):
            print(f'my shortest path to {n} is via {paths[n][1]} with cost {paths[n][0]}')


    def print_table(self):
        print(f'i am node {self.id} and my table is:')
        for i in self.table:
            print(i)
        print('***************************************')

a = DVNode(0, [0, 3, 23, INF])
b = DVNode(1, [3, 0, 2, INF])
c = DVNode(2, [23, 2, 0, 5])
d = DVNode(3, [INF, INF, 5, 0])
nodes = [a,b,c,d]

neighbors = [
    [1,2],
    [0,2],
    [0,1,3],
    [2]
]

print('simulation start state')
a.print_table()
b.print_table()
c.print_table()
d.print_table()
print('*************************************')

queue = []
for i in range(len(neighbors)):
    for n in neighbors[i]:
        queue.append([i, n])

while len(queue) > 0:
    current = queue.pop(0)
    print(f'processing {current}')
    if nodes[current[0]].update_table(current[1], nodes[current[1]].table):
        for n in neighbors[current[0]]:
            if n is not current[1]:
                queue.append([n, current[0]])
                print(f'update ocurred, enqueuing {n}, {current[0]}')
    

print('*************************************')
print('simulation finish state')
a.print_table()
b.print_table()
c.print_table()
d.print_table()

print('******** shortest paths **********')
a.print_shortest_paths()
b.print_shortest_paths()
c.print_shortest_paths()
d.print_shortest_paths()