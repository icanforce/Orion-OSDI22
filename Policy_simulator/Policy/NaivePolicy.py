from LambdaFunction import LambdaFunction
from Policy.Policy import Policy
from VirtualMachine import VirtualMachine

class NaivePolicy(Policy):
  def __init__(self):
    Policy.__init__(self, "NaivePolicy")

  def perform_init_action(self, sim, f: LambdaFunction, schedule_item):
    # check if there exists a free vm, if there is, schedule it
    # if not, send to queue
    if sim.free_vm():
      free_vm = sim.free_vm()
      free_vm.state = "running"
      free_vm.func = f
      f_init_time = f.get_init_duration()
      f_exec_time = f.get_exec_duration()
      sim.schedule_at(sim.t + f_init_time + f_exec_time, free_vm, "end")
      f.execution_record.append({
        "invoked": schedule_item[0],
        "started": sim.t,
        "exec_type": "cold",
        "ended": sim.t + f_init_time + f_exec_time
      })

      free_vm.curr_usage = {
        "func": f,
        "init_start": sim.t,
        "init_end": sim.t + f_init_time,
        "exec_record": [
          {
            "exec_start": sim.t + f_init_time,
            "exec_end": sim.t + f_init_time + f_exec_time
          }
        ]
      }
    else:
      sim.queue.append(schedule_item)

  def perform_end_action(self, sim, vm: VirtualMachine):
    # set state to free
    vm.state = "free"

    vm.curr_usage["usage_end"] = sim.t
    vm.usage_record.append(vm.curr_usage)
    vm.curr_usage = {}
