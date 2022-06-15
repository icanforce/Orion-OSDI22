import random
from collections import Counter

class LambdaFunction:
  def __init__(self,
               function_name,
               dag_name,
               initial_memory_size=0,
               exec_duration=[],
               exec_duration_prob=[],
               init_duration=[],
               init_duration_prob=[],
               num_containers=0):
    self.name = function_name
    self.dag_name = dag_name 
    self.next_functions = []
    self.memory_size = initial_memory_size
    self.exec_duration = exec_duration
    self.exec_duration_prob = exec_duration_prob
    self.init_duration = init_duration
    self.init_duration_prob = init_duration_prob
    self.num_containers_requried = num_containers

    self.init_set = None
    self.exec_set = None

    self.execution_record = []

  def print_function(self):
    print(f"{self.name} ({self.memory_size}MB)")

  def get_exec_duration(self):
    # if not self.exec_set:
    self.exec_set = random.choices(self.exec_duration, self.exec_duration_prob)[0]
    return self.exec_set 

  def get_init_duration(self):
    # if not self.init_set:
    self.init_set = random.choices(self.init_duration, self.init_duration_prob)[0]
    return self.init_set

  def get_mean_init_duration(self):
    mean_val = 0
    for i in range(len(self.init_duration)):
      mean_val += self.init_duration[i] * self.init_duration_prob[i]
    return mean_val
  
  def get_mean_exec_duration(self):
    mean_val = 0
    for i in range(len(self.exec_duration)):
      mean_val += self.exec_duration[i] * self.exec_duration_prob[i]
    return mean_val

  def get_median_init_duration(self):
    return self.init_duration[0]

  def get_median_exec_duration(self):
    return self.exec_duration[0]

if __name__ == "__main__":
  lf = LambdaFunction(
          "TEST_FN", 
          "TEST_DAG",
          1792, 
          [3, 8],
          [0.9, 0.1], 
          [7, 12],
          [0.9, 0.1],
          1
        )

  execs = []
  inits = []
  for _ in range(1000000):
    execs.append(lf.get_exec_duration())
    inits.append(lf.get_init_duration())
  print(Counter(inits))
  print(Counter(execs))
