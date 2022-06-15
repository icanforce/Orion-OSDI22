from collections import defaultdict
from InvocationPattern import InvocationPattern
from Policy.KeepAlivePolicy import KeepAlivePolicy
from Policy.NaivePolicy import NaivePolicy
from Policy.PrewarmMeanPolicy import PrewarmMeanPolicy
from Policy.PrewarmPolicy import PrewarmPolicy
from Policy.StateOfPracticePolicy import StateOfPracticePolicy
from Simulator import Simulator

import sys
import numpy as np
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt

from plotter import plot_function_gantt, plot_provider_gantt

def delay_vs_skew():
  runtime = 5
  f2_init_time = 2
  fanout = 30
  f2_runtimes = [runtime - f2_init_time for _ in range(fanout)]

  delay_variances = np.arange(0, 3.1, 0.05)
  skews = np.arange(1, 5.1, 0.05)

  res = {
    "e2e": [],
    "util": []
  }
  for delay_variance in delay_variances:
    e2e_for_dv = []
    util_for_dv = []
    for skew in skews:
      e2es = []
      utils = []
      for _ in range(100):
        # F1 Runtimes (all static except 1 which is 5X)
        # f1_runtimes = [runtime for _ in range(fanout)]
        # straggler_idx = np.random.randint(0, fanout)
        # f1_runtimes[straggler_idx] *= skew

        # F1 Runtimes (pull from distribution)
        if skew == 1:
          f1_runtimes = [runtime for _ in range(fanout)]
        else:
          f1_runtimes = np.random.uniform(runtime, high=skew*runtime, size=fanout)
          straggler_idx = np.random.randint(0, fanout)
          f1_runtimes[straggler_idx] = runtime*skew

        # Delays (uniformly picking in variance range)
        f2_delays = np.random.uniform(runtime-f2_init_time-delay_variance, runtime-f2_init_time+delay_variance, fanout)

        # Delays (picking optimally in range but according to runtime)
        # f2_delays = [
        #   max(min(r-f2_init_time, runtime-f2_init_time+delay_variance), runtime-f2_init_time-delay_variance)
        #   for r in f1_runtimes
        # ]
        latencies = []
        total_time = 0
        idle_time = 0
        for i in range(fanout):
          f1r = f1_runtimes[i]
          f2d = f2_delays[i]
          f2i = f2_init_time
          f2r = f2_runtimes[i]

          idle = 0
          if f1r > f2d + f2i:
            idle = f1r - (f2d+f2i)

          idle_time += idle
          latencies.append(max(f1r, f2d+f2i)+f2r)
          total_time += f1r + f2i + f2r + idle

        e2e = max(latencies)
        util = (1 - (idle_time/total_time)) * 100

        e2es.append(e2e)
        utils.append(util)

      # print(f"{delay_variance} - {skew}X - {np.average(e2es)}, {np.average(utils)}%")
      # sys.exit()
      e2e_for_dv.append(np.average(e2es))
      util_for_dv.append(np.average(utils))
    res["e2e"].append(e2e_for_dv)
    res["util"].append(util_for_dv)

  # Util fig
  df = pd.DataFrame(res["util"], index=delay_variances, columns=skews)
  print(max(res["util"]), min(res["util"]))
  fig, ax = plt.subplots(1,1)
  img = ax.imshow(df, cmap='jet', interpolation='nearest')
  ax.set_title("Utilization")
  ax.set_xticks([0, len(res["util"][0])//2, len(res["util"][0])])
  ax.set_xticklabels(["1.0X", "2.5X", "5.0X"])
  ax.set_xlabel("Skew on F1")
  ax.set_ylabel("Delay Variance for F2 (%)")
  ax.set_yticks([0, len(res["util"])//2, len(res["util"])])
  ax.set_yticklabels(["0%", "50%", "100%"])
  ax.invert_yaxis()
  fig.colorbar(img)
  fig.tight_layout(pad=0)

  # E2E Fig
  df = pd.DataFrame(res["e2e"], index=delay_variances, columns=skews)
  fig, ax = plt.subplots(1,1)
  img = ax.imshow(df, cmap='jet_r', interpolation='nearest')
  ax.set_title("E2E Latency")
  ax.set_xticks([0, len(res["e2e"][0])//2, len(res["e2e"][0])])
  ax.set_xticklabels(["1.0X", "2.5X", "5.0X"])
  ax.set_xlabel("Skew on F1")
  ax.set_ylabel("Delay Variance for F2 (s)")
  ax.set_yticks([0, len(res["e2e"])//2, len(res["e2e"])])
  ax.set_yticklabels(["0%", "[-50%, 50%]", "[-100%, 100%]"])
  ax.invert_yaxis()
  fig.colorbar(img)
  fig.tight_layout(pad=0)
  plt.show()

def main():
  ip_file = "test_invocation_pattern.csv"
  dag_base_path = "test_dags"
  num_VMs = 2

  ip = InvocationPattern(ip_file)
  policy = NaivePolicy()

  e2es = []
  func_durs = defaultdict(list)
  print(policy.name)
  for _ in range(100000):
    sim = Simulator(ip, dag_base_path, policy, num_VMs)
    sim.run_simulation()

    all_functions = {}
    for dag in sim.DAGs:
      for f in sim.DAGs[dag].adjacency_list:
        func_obj = sim.DAGs[dag].adjacency_list[f]["func"]
        if len(func_obj.execution_record) > 0:
          all_functions[f] = func_obj
        
          func_durations = []
          for idx, record in enumerate(func_obj.execution_record):
            func_durations.append(record["ended"] - record["invoked"])
          func_durs[f].append(np.average(func_durations))

      e2es.append(sim.t)

  print("E2E", np.average(e2es))
  for f, durs in func_durs.items():
    print(f, np.average(durs))

  # count, bins_count = np.histogram(e2es, bins=10)
  # pdf = count / sum(count)
  # cdf = np.cumsum(pdf)
  # plt.plot(bins_count[1:], cdf, label="CDF")
  # plt.legend()
  # plt.show()
  # plot_function_gantt(all_functions, policy)
  # plot_provider_gantt(sim.VMs, all_functions, policy)

if __name__ == "__main__":
  delay_vs_skew()