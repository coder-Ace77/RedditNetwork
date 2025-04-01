import networkx as nx
import csv

# Read the GraphML file names from graphml_files.csv
graphml_files = []
with open('utils/graphml_files.csv', newline='') as file:
    reader = csv.reader(file)
    for row in reader:
        graphml_files.append(row[0].strip())  # Assuming the filenames are in the first column

# Initialize an empty graph
merged_graph = nx.Graph()

# Iterate through each file and load the graph
for graphml_file in graphml_files:
    print(f"Loading {graphml_file}...")
    try:
        graph = nx.read_graphml(f'utils/{graphml_file}')
        # Merge the current graph into the merged_graph
        merged_graph.update(graph)
        print(f"Successfully merged {graphml_file}")
    except Exception as e:
        print(f"Error loading {graphml_file}: {e}")

# Save the merged graph to a new GraphML file
nx.write_graphml(merged_graph, "utils/merged_graph.graphml")
print("All graphs merged and saved to 'merged_graph.graphml'")
