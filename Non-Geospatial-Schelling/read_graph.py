import networkx as nx

def get_fred_network(
        filepath,
        is_directed: bool = True,
    ) -> nx.Graph:
        """
        Return a network as a Graph.

        Parameters
        ----------
        network : str
            a FRED network name

        is_directed : bool
            indicates whether the network to be loaded is directed. By default, a directed graph (nx.DiGraph) will be returned.

        sim_day : int
            the simulation day.

        Returns
        -------
        G : nx.Graph
            a NetworkX Graph (or DiGraph) object whose nodes (with associate attributes) and edges (with associated weights) are defined by FRED in a .vna output file.
        """

        fname = f"{network}-{sim_day}.vna"
        fname = os.path.join(self.path_to_run, fname)

        if not os.path.isfile(fname):
            msg = (
                f"The requested output for the network `{network}` on day {sim_day} was not found in "
                f"{self.path_to_run}\n"
                f"You may need to either pass a different sim_day or adjust the value of `output_interval` for the network `{network}` in your FRED model."
            )
            raise FileNotFoundError(msg)

        # create a Graph or DiGraph object
        if is_directed:
            G = nx.DiGraph(name=network)
        else:
            G = nx.Graph(name=network)

        # read in data from file
        with open(fname, "r") as f:
            lines = f.readlines()

        tie_data_index = lines.index("*tie data\n")
        node_data = lines[:tie_data_index]
        tie_data = lines[tie_data_index:]

        # construct a list of nodes
        node_count = 0
        nodes = []
        node_attr_keys = node_data[1].strip().split(" ")[1:]
        for line in node_data[2:]:
            line_list = line.strip().split(" ")
            node_id = line_list[0]
            node_attrs = line_list[1:]
            nodes.append((node_id, dict(zip(node_attr_keys, node_attrs))))
            node_count += 1

        # construct a list of ties
        tie_count = 0
        ties = []
        tie_attr_keys = tie_data[1].strip().split(" ")[2:]
        for line in tie_data[2:]:
            line_list = line.strip().split(" ")
            from_id = line_list[0]
            to_id = line_list[1]
            tie_attrs = line_list[2:]
            ties.append((from_id, to_id, dict(zip(tie_attr_keys, tie_attrs))))
            tie_count += 1

        G.add_nodes_from(nodes)
        G.add_edges_from(ties)

        return G