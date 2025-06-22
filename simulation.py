import argparse
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import LineString

from simulation_class import TrafficSimulation


def main():
    ''' Main function to parse command-line arguments, then simulate a traffic dynamics

    Command-line settings:

    Parameters:
    file : str, path to the geojson file containint network features
    n_max : int, Maximum number of cars allowed in a node, default is 10
    tc : int, Transport capacity, i.e. maximum number of cars a node can move in an interation, default is 3
    n_steps : int, Number of simulation time steps, default is 100
    load : float, Average traffic load per node, default is 3
    dynamics : str, Simulation dynamics choice ['asy'/'sy'] for asincronous and synchronous dynamics

    '''

    parser = argparse.ArgumentParser(
        description = "Simulate a traffic dynamic")
    
    parser.add_argument(
        "--file",
        type=str,
        help="Path to geojson file containing the network features"
    )

    parser.add_argument(
        "--n_max",
        type=int,
        help="Maximum number of cars allowed in a node",
        default = 10
    )

    parser.add_argument(
        "--tc",
        type=int,
        help="Transport capacity, i.e. maximum number of cars a node can move in an interation",
        default = 3
    )

    parser.add_argument(
        "--n_steps",
        type=int,
        help="Number of simulation time steps",
        default = 100
    )

    parser.add_argument(
        "--load",
        type=float,
        help="Average traffic load per node",
        default = 3
    )

    parser.add_argument(
        "--dynamics",
        type=str,
        help="Simulation dynamics, [asy/sy] for asynchronous and synchronous",
        default = 'asy'
    )



    args = parser.parse_args()



    gdf = gpd.read_file(args.file)

    G = nx.Graph()

    def add_edges_with_length(geometry, length=None):
        # Check if the geometry is a LineString
        if isinstance(geometry, LineString):
            coords = list(geometry.coords)
            edge_length = length if length is not None else LineString([coords[0], coords[-1]]).length
            G.add_edge(coords[0], coords[-1], length = edge_length)
            G.nodes[coords[0]]['n'] = 0
            G.nodes[coords[-1]]['n'] = 0
            G.nodes[coords[0]]['n_max'] = args.n_max
            G.nodes[coords[-1]]['n_max'] = args.n_max
            G.edges[coords[0], coords[-1]]['flux'] = 0


    
    for idx, row in gdf.iterrows():
        geometry = row.geometry
       
        if 'poly_length' in gdf.columns:
            street_length = row['poly_length']  
            add_edges_with_length(geometry, street_length)
        else:
            
            add_edges_with_length(geometry)


    pos = {node: node for node in G.nodes()}  
    ax, fig = plt.subplots(1, figsize=(8,8))
    nx.draw(G, pos, node_size=0., linewidths = 0.1, edge_color='black', arrows = False)


    degrees=[]

    for u,data in G.nodes(data=True):
        degrees.append(G.degree(u))


    a = np.unique(degrees, return_counts=True)
    b = a[1]/np.sum(a[1])

    plt.bar(a[0],b, edgecolor='black')
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y,_:'{:.0f}'.format(y*100)))
    plt.title('Degree histogram')
    plt.ylabel('Frequency [%]')
    plt.xlabel('Degree')

    print('Degree mean: ', np.mean(degrees),'\n')


    


    sim = TrafficSimulation(G = G, tc = args.tc)

    G, node_population = sim.simulate(args.n_steps, args.load, args.dynamics)

    node_passage = np.array([G.nodes[u]['n'] for u in G.nodes()])
    counts, bins = np.histogram(node_passage) 

    p_i = []
    for i in range(np.max(node_passage)):
        p_i.append(np.count_nonzero(node_passage==i)/counts.sum())

    y_norm = p_i / np.sum(p_i)

    

    x = np.linspace(0,np.max(node_passage)-1,np.max(node_passage))

    mean = np.sum(x * y_norm)
    dev_std = np.sqrt(np.sum(((x - media)**2) * y_norm))

    plt.scatter(x, p_i, s=10)
    plt.plot(x, p_i)

    plt.xticks(ticks=x[::1])
    #plt.plot(x, exp_high(x, params[0]), c= 'orange', label = '1/4.20*exp(-n/4.20)')
    #plt.plot([], [], ' ', label=f'$R^2 = {r_squared:.2f}$')

    plt.plot([], [], ' ', label=f'Mean = {mean:.2f}')
    plt.plot([], [], ' ', label=f'Std = {dev_std:.2f}')
    if args.dynamics == 'sy':
        plt.title(r'$p(n)$ in Synchronous dynamic with $\bar{n}$ = ', args.load)
    else: 
        plt.title(r'$p(n)$ Asynchronous dynamic with $\bar{n}$ = ', args.load)

    plt.xlabel('Node state n')
    plt.ylabel('Marginal distribution p(n)')
    plt.legend()
    plt.grid(True)
    plt.show()




    nodes_mean = np.mean(node_population, axis=0)

    
    quadratic_deviations = (node_population - nodes_mean) ** 2

    
    std_per_node = np.sqrt(np.mean(quadratic_deviations, axis=0)) 

    plt.hist(std_per_node, edgecolor='black')
    plt.xlabel('Deviations')
    plt.ylabel('Occurence')
    if args.dynamics == 'sy':
        plt.title(r'Deviations occurrence in synchronous dynamic with $\bar{n}$ = ', args.load)
    else: 
        plt.title(r'Deviations occurrence in asynchronous dynamic with $\bar{n}$ = ', args.load)
    plt.xlim(0,5)
    plt.show()



if __name__ == '__main__':
    main()
    
