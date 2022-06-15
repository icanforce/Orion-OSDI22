import pandas as pd

class InvocationPattern:
  def __init__(self, pattern_file):
    self.df = pd.read_csv(pattern_file)
    self.t = 0
    self.dags = self.df.dag_name.unique()

  def next(self):
    if self.t >= len(self.df):
      return pd.DataFrame()
    result = self.df.iloc[self.t]
    self.t += 1
    return result

if __name__ == "__main__":
  ip = InvocationPattern("test_invocation_pattern.csv")
  while True:
    res = ip.next()
    if res.empty:
      break
    print(res)