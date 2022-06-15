from LambdaFunction import LambdaFunction
from Policy.Policy import Policy

class StateOfPracticePolicy(Policy):
  def __init__(self, ttl):
    Policy.__init__(self, f"StateOfPracticePolicy [TTL:{ttl}]")
    self.ttl = ttl

  def perform_init_action(self, sim, f: LambdaFunction, schedule_item):
    if sim.vm_with("warm", f): # TODO: check if we need to pick warm container with least ttl
      warm_vm = sim.vm_with("warm", f)
      warm_vm.state = "running"
      f_exec_dur = f.get_exec_duration()
      warm_vm.keep_alive_till = sim.t + f_exec_dur + self.ttl
      sim.schedule_at(sim.t + f_exec_dur, warm_vm, "end")
      sim.schedule_at(warm_vm.keep_alive_till, warm_vm, "free")
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
    elif sim.free_vm():
      free_vm = sim.free_vm()
      free_vm.state = "running"
      free_vm.func = f
      f_init_dur = f.get_init_duration()
      f_exec_dur = f.get_exec_duration()

      free_vm.keep_alive_till = sim.t + f_init_dur + f_exec_dur + self.ttl
      sim.schedule_at(sim.t + f_init_dur + f_exec_dur, free_vm, "end")
      sim.schedule_at(free_vm.keep_alive_till, free_vm, "free")
      f.execution_record.append({
        "invoked": schedule_item[0],
        "started": sim.t,
        "exec_type": "cold",
        "ended": sim.t + f_init_dur + f_exec_dur
      })
      free_vm.curr_usage = {
        "func": f,
        "init_start": sim.t,
        "init_end": sim.t + f_init_dur,
        "exec_record": [
          {
            "exec_start": sim.t + f_init_dur,
            "exec_end": sim.t + f_init_dur + f_exec_dur
          }
        ]
      }
    else:
      # if no warm for f and no free, kill an existing warm
      other_warm_vm = None
      for vm in sim.VMs:
        if vm.state == "warm":
          other_warm_vm = vm
          break
      if other_warm_vm:
        other_warm_vm.state = "running"
        other_warm_vm.func = f
        f_init_dur = f.get_init_duration()
        f_exec_dur = f.get_exec_duration()
        other_warm_vm.keep_alive_till = sim.t + f_init_dur + f_exec_dur + self.ttl
        sim.schedule_at(sim.t + f_init_dur + f_exec_dur, other_warm_vm, "end")
        sim.schedule_at(other_warm_vm.keep_alive_till, other_warm_vm, "free")
        f.execution_record.append({
          "invoked": schedule_item[0],
          "started": sim.t,
          "exec_type": "cold",
          "ended": sim.t + f_init_dur + f_exec_dur
        })
        other_warm_vm.curr_usage["usage_end"] = sim.t
        other_warm_vm.usage_record.append(vm.curr_usage)
        other_warm_vm.curr_usage = {
        "func": f,
        "init_start": sim.t,
        "init_end": sim.t + f_init_dur,
        "exec_record": [
          {
            "exec_start": sim.t + f_init_dur,
            "exec_end": sim.t + f_init_dur + f_exec_dur
          }
        ]
      }
      else:
        sim.queue.append(schedule_item)

  def perform_free_action(self, sim, vm):
    if sim.t >= vm.keep_alive_till:
      vm.state = "free"
      vm.curr_usage["usage_end"] = sim.t
      vm.usage_record.append(vm.curr_usage)
      vm.curr_usage = {}

  def perform_end_action(self, sim, vm):
    vm.state = "warm"