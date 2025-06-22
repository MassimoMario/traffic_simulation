import numpy as np
import random
from tqdm import tqdm



class TrafficSimulation:
    
    def __init__(self, G, tc = 3):
        ''' Class constructor

        Arguments:
        graph : nx.Graph, urban network
        tc : int, transport capacity, i.e. maximum number of cars a node can move at each time step
        
        '''
        self.G = G
        self.tc = tc


    def set_cars(self, load):
        ''' Function injecting cars in the network at time step = 0
        Arguments:

        load : float, average traffic load per node
        '''
        print('Setting cars')
        for _ in tqdm(range(int(load*len(self.G.nodes)))):

            while True:
                random_node = random.choice(list(self.G.nodes))
                if self.G.nodes[random_node]['n'] < self.G.nodes[random_node]['n_max']:
                    self.G.nodes[random_node]['n'] += 1
                    break


    
    def restart_graph(self):
        ''' Function resetting the graph quantities to 0 to start a new simulation
        '''
        for node, data in self.G.nodes(data=True):
            data['n'] = 0

        for _,_, data in self.G.edges(data=True):
            data['flux'] = 0




    def update_async(self):
        ''' Function updating the simulation in Asynchronous dynamics

        Return:
        node_population : list, list of loads for each node, shape: [# of nodes]
        '''
        node_population = []
        
        for node in self.G.nodes:

            node_population.append(self.G.nodes[node]['n'])

            if self.G.nodes[node]['n'] >= 1:
                list_successors = list(self.G.neighbors(node))
                num_successors = len(list_successors)
                
                random_node = random.randint(0, num_successors-1)
                next_node = list_successors[random_node]

                    
                if self.G.nodes[node]['n'] <= self.tc:
                    n_cars_passed = random.randint(0, self.G.nodes[node]['n'])
                else: 
                    n_cars_passed = random.randint(0, self.tc)

                if self.G.nodes[next_node]['n'] <= self.G.nodes[next_node]['n_max'] - n_cars_passed:
                    self.G.nodes[next_node]['n'] += n_cars_passed
                    self.G.nodes[node]['n'] -= n_cars_passed
                    self.G.edges[node, next_node]['flux'] += n_cars_passed


        return node_population




    def update_sync(self):
        ''' Function updating the simulation in Synchronous dynamics

        Return:
        node_population : list, list of loads for each node, shape: [# of nodes]
        '''

        node_population = []

        delta_n = {node: 0 for node in self.G.nodes}  
        edge_flux = {}

        for u, v in self.G.edges:
            key = tuple(sorted((u, v)))
            edge_flux[key] = 0

        for node in self.G.nodes:
            node_population.append(self.G.nodes[node]['n'])

            if self.G.nodes[node]['n'] >= 1:
                list_successors = list(self.G.neighbors(node))
                if not list_successors:
                    continue

                next_node = random.choice(list_successors)

                if self.G.nodes[node]['n'] <= self.tc:
                    n_cars_passed = random.randint(0, self.G.nodes[node]['n'])
                else:
                    n_cars_passed = random.randint(0, self.tc)


                if self.G.nodes[next_node]['n'] + delta_n[next_node] < self.G.nodes[next_node]['n_max']:
                    delta_n[node] -= n_cars_passed
                    delta_n[next_node] += n_cars_passed
                    
                    edge_key = tuple(sorted((node, next_node)))
                    edge_flux[edge_key] += n_cars_passed


        
        for node, delta in delta_n.items():
            self.G.nodes[node]['n'] += delta

        for (u, v), flux in edge_flux.items():
            self.G.edges[u, v]['flux'] += flux

        return node_population
    

        
    


    def simulate(self, n_time_steps = 100, load = 3, dynamics = 'asy'):
        ''' Simulation function

        Arguments:
        n_time_steps : int, number of simulation time steps
        load : float, average traffic load per node
        dynamics : string, 'asy' for asynchronous and 'sy' for synchronous dynamics

        Return:
        G : nx.Graph, the updated graph with relative values of node loads and edge fluxes
        node_population : np.ndarray, array of loads for each node at each time step, shape [# time steps, # nodes]
        '''

        node_populations = np.ndarray(shape=(n_time_steps, len(self.G.nodes)))

        self.restart_graph()

        self.set_cars(load)


        for i in tqdm(range(n_time_steps)):
            if dynamics == 'asy':
                node_pop = self.update_async()
                node_populations[i] = node_pop
            elif dynamics == 'sy': 
                node_pop = self.update_sync()
                node_populations[i] = node_pop

        return self.G, node_populations