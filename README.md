# Random walk traffic simulation 🌇🚗🚙
Python implementation of a traffic simulation using a random walk over a graph. Scripts in this repository allow to perform a simulation with two dynamics: synchronous and asynchronous dynamics.


# Installation
To start using the repository, first clone it:

```
git clone https://github.com/MassimoMario/traffic_simulation.git
```

# Requirements
This project requires **Python &ge; 3.8** and the following libraries:
- `numpy`
- `matplotlib`
- `ipython`
- `tqdm`
- `networkx`
- `geopandas`

To install them you can run on the Bash:
```
pip install -r requirements.txt
```


# Usage and examples
The main script [`simulation.py`](simulation.py) can be runned from the command line providing different argument ending in different configuration.

As an example you can run:
```
python simulation.py --file my_file.geojson --n_max 10 --tc 3 --n_steps 100 --load 3 --dynamics sy
```

The `dynamics` argument is a string an allows only 'asy' and 'sy' values for asynchronous and synchronous dynamics.

⚠️ The output of the `simulation` script are plots of the input network, its degree histogram, the probability distribution of node state and the deviations occurrence.

⚠️⚠️⚠️Replace `my_file.geojson` with your actual file .geojson :) .

## :information_source: Help
For a complete list of parameters and their descriptions, run:

```
python simulation.py --help
```


# Repository structure
The repository contains the following folders and files:
- [`simulation.py`](simulation.py) is the main script for simulating and plotting the results
- [`simulation_class.py`](simulation_class.py) is the script containing the simulation class definition
- [`requirements.txt`](requirements.txt) txt file containing the required libraries to run the simulation

