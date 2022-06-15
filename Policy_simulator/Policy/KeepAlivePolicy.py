from LambdaFunction import LambdaFunction
from Policy.Policy import Policy

class KeepAlivePolicy(Policy):
  def __init__(self, ttl):
    Policy.__init__(self, f"KeepAlivePolicy [TTL:{ttl}]")
    self.ttl = ttl

  def perform_init_action(self, sim, f: LambdaFunction, schedule_item):
    # if warm container exists, set state to running and schedule end and set
    #   keep_alive_till of vm to sim.t + warm_time + self.ttl
    # if free container, set state to running and schedule end and set keep_alive_till
    #   of vm to sim.t + cold_time + self.ttl 
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
      sim.queue.append(schedule_item)

  def perform_free_action(self, sim, vm):
    if sim.t >= vm.keep_alive_till:
      vm.state = "free"
      vm.curr_usage["usage_end"] = sim.t
      vm.usage_record.append(vm.curr_usage)
      vm.curr_usage = {}

  def perform_end_action(self, sim, vm):
    vm.state = "warm"