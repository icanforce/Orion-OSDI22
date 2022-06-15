from LambdaFunction import LambdaFunction
from Policy.Policy import Policy

class PrewarmPolicy(Policy):
  def __init__(self, prewarm_delay):
    Policy.__init__(self, "PrewarmPolicy")
    if prewarm_delay > 0:
      self.name = f"{self.name} [Late: +{prewarm_delay}s]"
    elif prewarm_delay == 0:
      self.name = f"{self.name} [Oracle]"
    else:
      self.name = f"{self.name} [Early: {prewarm_delay}s]"

    self.prewarm = True
    self.prewarm_delay = prewarm_delay

  def schedule_initial_prewarms(self, sim, dag, ts):
    # Sticking to simple serial function for now
    for func_name in dag.adjacency_list["START"]["next"]:
      curr_func = dag.adjacency_list[func_name]["func"]
      predicted_exec_duration = curr_func.get_median_exec_duration()

      sim.schedule_at(
        ts - self.prewarm_delay,
        curr_func,
        "prewarm"
      )

      for next_func_name in dag.adjacency_list[func_name]["next"]:
        next_func = dag.adjacency_list[next_func_name]["func"]
        sim.schedule_at(
          ts + predicted_exec_duration - self.prewarm_delay,
          next_func,
          "prewarm"
        )
  
  def perform_init_action(self, sim, f, schedule_item):
    # if vm is warm already, schedule end
    # if vm is prewarming, schedule end of fn
    # below cases shouldn't happen
    # if free or if nothing exists
    if sim.vm_with("prewarming", f):
      init_vm = sim.vm_with("prewarming", f)
      init_vm.state = "scheduled"

      f_exec_dur = f.get_exec_duration()

      if init_vm.init_end_time <= sim.t:
        sim.schedule_at(sim.t + f_exec_dur, init_vm, "end")
        f.execution_record.append({
          "invoked": schedule_item[0],
          "started": sim.t,
          "exec_type": "warm",
          "ended": sim.t + f_exec_dur
        })
        init_vm.curr_usage["exec_record"].append({
          "exec_start": sim.t,
          "exec_end": sim.t + f_exec_dur
        })
      else:
        sim.schedule_at(init_vm.init_end_time + f_exec_dur, init_vm, "end")
        f.execution_record.append({
          "invoked": schedule_item[0],
          "started": sim.t,
          "exec_type": "almost_warm",
          "ended": init_vm.init_end_time + f_exec_dur
        })
        init_vm.curr_usage["exec_record"].append({
          "exec_start": init_vm.init_end_time,
          "exec_end": init_vm.init_end_time + f_exec_dur
        })
    elif sim.vm_with("warm", f):
      warm_vm = sim.vm_with("warm", f)
      warm_vm.state = "running"
      f_exec_dur = f.get_exec_duration()

      sim.schedule_at(sim.t + f_exec_dur, warm_vm, "end")
      f.execution_record.append({
          "invoked": schedule_item[0],
          "started": sim.t,
          "exec_type": "warm",
          "ended": sim.t + f_exec_dur
        })
      warm_vm.curr_usage["exec_record"].append({
        "exec_start": sim.t,
        "exec_end": sim.t + f_exec_dur
      })
    elif not sim.free_vm():
      sim.queue.append(schedule_item)
    else:
      raise Exception("SHOULDNT HAPPEN IN PREWARM POLICY")

  def perform_prewarm_action(self, sim, f, schedule_item):
    # loop through vms
    #   if vm is already warm with fn, do nothing
    #   if vm is free, set state to prewarming
    #   if no sim is free, push to deque
    if not sim.vm_with("warm", f):
      if sim.free_vm():
        free_vm = sim.free_vm()
        free_vm.state = "prewarming"

        pred_init_dur = f.get_init_duration()
        free_vm.init_end_time = sim.t + pred_init_dur
        free_vm.func = f

        free_vm.curr_usage = {
          "func": f,
          "init_start": sim.t,
          "init_end": sim.t + pred_init_dur,
          "exec_record": []
        }
      else:
        sim.queue.append(schedule_item)

  def perform_end_action(self, sim, vm):
    vm.state = "free"
    vm.curr_usage["usage_end"] = sim.t
    vm.usage_record.append(vm.curr_usage)
    vm.curr_usage = {}