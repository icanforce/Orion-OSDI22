from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib import rc
import numpy as np

font = {'size': 14}

rc('font', **font)

WARM_EXEC_EDGECOLOR = (0,0,0,0)
COLD_EXEC_EDGECOLOR = "red"
ALMOST_WARM_EXEC_EDGECOLOR = "orange"
COLORS = [
  (46/255, 139/255, 87/255), # seagreen
  (70/255, 130/255, 180/255) # steelblue
]

HATCH_LEGEND = [
  Patch(facecolor="white", ec=COLD_EXEC_EDGECOLOR, label="Cold Exec", linewidth=3),
  # Patch(facecolor="white", ec=WARM_EXEC_EDGECOLOR, label="Warm Exec"),
  Patch(facecolor="white", ec=ALMOST_WARM_EXEC_EDGECOLOR, label="Almost Warm Exec", linewidth=3),
  # Patch(facecolor="black", alpha=0.35, label="Queued"),
]

def plot_function_gantt(funcs, policy):
  data = {
    "function": [],
    "exec_duration": [],
    "total_duration": [],
    "queuing_duration": [],
    "start_time": [],
    "invoke_time": [],
    "end_time": [],
    "color": [],
    "edge_color": []
  }
  func_legend = []
  total_durations = defaultdict(list)
  for fidx, func in enumerate(funcs):
    func_obj = funcs[func]
    func_legend.append(Patch(facecolor=COLORS[fidx], label=f"{func}"))

    for idx, record in enumerate(func_obj.execution_record):
      data["function"].append(f"{func_obj.name}:{idx+1}")
      data["exec_duration"].append(record["ended"] - record["started"])
      data["invoke_time"].append(record["invoked"])
      data["start_time"].append(record["started"])
      data["end_time"].append(record["ended"])
      data["queuing_duration"].append(record["started"] - record["invoked"])
      data["total_duration"].append(record["ended"] - record["invoked"])
      data["color"].append(COLORS[fidx])
      if record["exec_type"] == "warm":
        data["edge_color"].append(WARM_EXEC_EDGECOLOR)
      elif record["exec_type"] == "almost_warm":
        data["edge_color"].append(ALMOST_WARM_EXEC_EDGECOLOR)
      else:
        data["edge_color"].append(COLD_EXEC_EDGECOLOR)

      total_durations[func].append(record["ended"] - record["invoked"])

  df = pd.DataFrame.from_dict(data)
  df.sort_values("invoke_time", inplace=True, ascending=False)
  fig, ax = plt.subplots(1, figsize=(16,6))

  ax.barh(df.function, df.queuing_duration, left=df.invoke_time, color=df.color, alpha=0.5)
  bars = ax.barh(df.function, df.exec_duration, left=df.start_time, color=df.color, edgecolor=df.edge_color, linewidth=3.5)

  # Set total duration after each bar
  idx = 0
  for _, row in df.iterrows():
    ax.text(row.end_time + 1, idx, 
            f"{int(row.total_duration)}s", 
            va='center', alpha=0.8)
    idx += 1

  # Set titles
  ax.set_xlabel("Time (s)")
  ax.set_ylabel("Function Invocation")
  ax.set_title(f"Function Timeline ({policy.name})")
  ax.xaxis.grid(True)

  f_legend = plt.legend(handles=func_legend, loc='best')
  plt.gca().add_artist(f_legend)
  plt.legend(handles=HATCH_LEGEND, loc='upper center', ncol=2)
  

  # Print some stats
  # print("Average Latencies")
  # for func in total_durations:
  #   print(f"{func} - avg: {np.average(total_durations[func])}s")

  plt.show()
  return total_durations

def plot_provider_gantt(vms, funcs, policy):
  func_colors = {}
  func_legend = []
  for fidx, func in enumerate(funcs):
    func_colors[func] = COLORS[fidx]
    func_legend.append(Patch(facecolor=COLORS[fidx], label=f"{func}"))

  data = {
    "name": [],
    "function": [],
    "duration": [],
    "duration_type": [],
    "left_offset": [],
    "color": [],
    "edge_color": []
  }
  total_durations = defaultdict(list)

  for vm in vms:
    for record in vm.usage_record:
      # Append entire warm phase
      data["name"].append(vm.name)
      data["function"].append(record["func"].name)
      data["duration"].append(record["usage_end"] - record["init_start"])
      data["duration_type"].append("warm")
      data["left_offset"].append(record["init_start"])
      data["color"].append(func_colors[record["func"].name] + (0.5,))
      data["edge_color"].append("black")

      exec_durations = []
      for exec in record["exec_record"]:
        data["name"].append(vm.name)
        data["function"].append(record["func"].name)
        data["duration"].append(exec["exec_end"] - exec["exec_start"])
        data["duration_type"].append("exec")
        data["left_offset"].append(exec["exec_start"])
        data["color"].append(func_colors[record["func"].name] + (1,))
        data["edge_color"].append((0, 0, 0, 0))
        exec_durations.append(exec["exec_end"] - exec["exec_start"])

      total_durations[vm.name].append({
        "usage_duration": record["usage_end"] - record["init_start"],
        "exec_durations": exec_durations
      })

  df = pd.DataFrame.from_dict(data)
  fig, ax = plt.subplots(1, figsize=(16,6))

  ax.barh(df.name, df.duration, left=df.left_offset, color=df.color, height=0.25, edgecolor=df.edge_color)

  # Set titles
  ax.set_xlabel("Time (s)")
  ax.set_ylabel("VMs")
  ax.set_title(f"VM Timeline ({policy.name})")
  ax.xaxis.grid(True)
  ax.set_ybound(-1, 1)
  # ax.set_xlim(left=0)

  plt.legend(handles=func_legend, loc='best')

  # Print some stats
  print("Utilization Ratio")
  for vm in total_durations:
    total_usage = sum([dur["usage_duration"] for dur in total_durations[vm]])
    total_exec = sum([sum(dur["exec_durations"]) for dur in total_durations[vm]])
    print(f"{vm} - Productive Utilization: {total_exec/total_usage*100}%")

  plt.show()