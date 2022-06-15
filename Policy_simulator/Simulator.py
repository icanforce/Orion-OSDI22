from DAG import DAG
from InvocationPattern import InvocationPattern
from LambdaFunction import LambdaFunction
from Policy.KeepAlivePolicy import KeepAlivePolicy
from Policy.PrewarmPolicy import PrewarmPolicy
from Policy.StateOfPracticePolicy import StateOfPracticePolicy
from VirtualMachine import VirtualMachine
from Policy.Policy import Policy
from Policy.NaivePolicy import NaivePolicy

from heapq import heappush, heappop
from collections import deque
from datetime import datetime

class Simulator:
  def __init__(self, ip: InvocationPattern, dag_json_base_path: str, policy: Policy, num_VMs):
    self.schedule = []
    self.t = 0
    self.ip = ip
    self.DAGs = {
      dag_name: DAG(f"{dag_json_base_path}/{dag_name}.json") for dag_name in self.ip.dags
    }
    self.policy = policy
    self.VMs = [VirtualMachine(i+1) for i in range(num_VMs)]
    self.queue = deque()

    self.build_schedule()

    # print("Initial Schedule")
    # for item in sorted(self.schedule):
    #   print(f"{item[0]} - {item[2]['type']}, {item[2]['func'].name}")
    # print()

  def schedule_at(self, t, f, schedule_type):
    heappush(self.schedule, (
      t, datetime.now(), {
        "func": f,
        "type": schedule_type
      }
    ))

  def empty_schedule(self):
    self.schedule = []

  def build_schedule(self):
    for _, invocation in self.ip.df.iterrows():
      curr_dag = self.DAGs[invocation["dag_name"]]

      for func_name in curr_dag.adjacency_list["START"]["next"]:
        curr_func = curr_dag.adjacency_list[func_name]["func"]
        self.schedule_at(invocation["timestamp"], curr_func, "init")

      # Only for policies that prewarm, set prewarm points for each invocation
      # Will probably change with a more complicated prewarming mechanism
      if self.policy.prewarm:
        self.policy.schedule_initial_prewarms(self, curr_dag, invocation["timestamp"])

      # Initial schedule
      # for s in self.schedule:
      #   print(s)

  def run_simulation(self):
    while len(self.schedule) != 0:
      schedule_item = heappop(self.schedule)

      self.t = schedule_item[0]
      func = schedule_item[2]["func"]

      if schedule_item[2]["type"] == "init":
        self.policy.perform_init_action(self, func, schedule_item)
      elif schedule_item[2]["type"] == "end":
        # set state to warm/cold based on policy, reset keep alive if necessary
        self.policy.perform_end_action(self, func)
        dag = self.DAGs[func.func.dag_name]
        for next_func_name in dag.adjacency_list[func.func.name]["next"]:
          next_func = dag.adjacency_list[next_func_name]["func"]
          self.schedule_at(
            self.t,
            next_func,
            "init"
          )

      elif schedule_item[2]["type"] == "free":
        self.policy.perform_free_action(self, func)
      elif schedule_item[2]["type"] == "prewarm":
        self.policy.perform_prewarm_action(self, func, schedule_item)

      # TODO: confirm with Ashraf to see if this needs to happen 
      for i in range(len(self.queue)):
        queue_item = self.queue.popleft()
        if queue_item[2]["type"] == "init":
          self.policy.perform_init_action(self, queue_item[2]["func"], queue_item)
        elif queue_item[2]["type"] == "prewarm":
          self.policy.perform_prewarm_action(self, func, schedule_item)

    if len(self.queue) > 0:
      raise Exception("Queue shouldn't have items...")
  
  def vm_with(self, state: str, f: LambdaFunction):
    for vm in self.VMs:
      if vm.state == state and vm.func == f:
        return vm
    return None

  def free_vm(self):
    for vm in self.VMs:
      if vm.state == "free":
        return vm
    return None

if __name__ == "__main__":
  ip_file = "test_invocation_pattern.csv"
  dag_base_path = "test_dags"
  num_VMs = 1

  ip = InvocationPattern(ip_file)
  policy = NaivePolicy()
  sim = Simulator(ip, dag_base_path, policy, num_VMs)

  sim.run_simulation()
  print(sim.t)
  for dag in sim.DAGs:
    print(f"=={dag}==")
    for f in sim.DAGs[dag].adjacency_list:
      print(f, sim.DAGs[dag].adjacency_list[f]["func"].execution_record)