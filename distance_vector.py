INF = 2 ** 32

class DVNode:
    """
    id: id de este nodo
    initial_vector: vector que contiene los pesos de cada vecino, o
                    INF si no existe la coneccion.
    """
    def __init__(self, id, initial_vector):
        """
        Crear la tabla de ruteo (distance vector) de este nodo. Se inicia con los datos
        de los nodos vecinos, y el resto de casillas se llenan con un valor muy alto.
        """
        self.id = id
        self.num_nodes = len(initial_vector)
        self.table = []
        self.neighbors = []

        for row in range(self.num_nodes):
            r = []
            for col in range(self.num_nodes):
                if row == col:
                    r.append(initial_vector[col])
                    if col != id and initial_vector[col] != INF:
                        self.neighbors.append(col)
                else:
                    r.append(INF)
            self.table.append(r)

    def update_table(self, id_from, distance_vector):
        """
        Actualiza la tabla de ruteo de este nodo.
        Se especifica el nodo de donde viene la actualizacion (id_from) y
        su tabla de ruteo (distance_vector).
        """
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

        return updated

    def get_best_path_node_id(self, id_to):
        """
        Retorna el id del nodo a quien se debe enviar un mensaje
        para enviar un mensaje a nodo con id (id_to).
        """
        best_cost = INF
        best_node_id = 0
        for i in range(self.num_nodes):
            if self.table[id_to][i] < best_cost:
                best_cost = self.table[id_to][i]
                best_node_id = i
        
        return best_node_id, best_cost
        

    def get_shortest_paths(self):
        """
        Se utiliza para debug.
        Imprime un resumen de las rutas que debe tomar este nodo
        para llegar a otros nodos, y el costo de dichas rutas.
        """
        paths = [[0, INF] for _ in range(self.num_nodes)]
        for to in range(self.num_nodes):
            for via in range(self.num_nodes):
                if self.table[to][via] < paths[to][1]:
                    paths[to] = [via, self.table[to][via]]
        
        return paths