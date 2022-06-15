from enum import Enum

class VMState(Enum):
  FREE = "free"
  WARM = "warm"
  RUNNING = "running"
  PREWARMING = "prewarming"

class VirtualMachine:
  def __init__(self, id):
    self.name = f"VM{id}"
    self.state = "free"
    self.func = None
    self.usage_record = []