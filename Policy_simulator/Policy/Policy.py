class Policy:
  def __init__(self, name):
    self.name = name
    self.prewarm = False

  def perform_init_action(self, sim, f, schedule_item):
    raise Exception("Can't invoke this directly, must be extended by child")

  def perform_end_action(self, sim, vm):
    raise Exception("Can't invoke this directly, must be extended by child")