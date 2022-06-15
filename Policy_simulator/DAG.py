import json
import networkx as nx
import matplotlib.pyplot as plt

from LambdaFunction import LambdaFunction

class DAG:
  def __init__(self, dag_definition):
    self.adjacency_list = {}

    with open(dag_definition) as dag_file:
      dag_json = json.loads(dag_file.read())

    self.name = dag_json["Name"]

    self.adjacency_list["START"] = {
      "next": dag_json["StartAt"],
      "func": LambdaFunction("START", self.name)
    }


    for func_name in dag_json["Functions"]:
      func = dag_json["Functions"][func_name]
      self.adjacency_list[func_name] = {
        "next": func["Next"],
        "func": LambdaFunction(
          func_name, 
          self.name,
          func["InitialMemorySize"], 
          func["ExecDuration"],
          func["ExecDurationProb"], 
          func["InitDuration"],
          func["InitDurationProb"],
          func["NumContainers"]
        )
      }

  def print_DAG(self):
    graph = nx.DiGraph()
    edges = []

    for func in self.adjacency_list:
      for next_func in self.adjacency_list[func]["next"]:
        edges.append((func, next_func))

    graph.add_edges_from(edges)
    nx.draw(graph, with_labels=True, node_size=1500, node_color="skyblue", node_shape="s", alpha=0.5, linewidths=40)
    plt.show()

if __name__ == "__main__":
  dag_file = "test_dags/f1_only.json"
  dag = DAG(dag_file)
  dag.print_DAG()
