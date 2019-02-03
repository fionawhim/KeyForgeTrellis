import time
from uheapq import *

REMOVED = '<removed-task>'      # placeholder for a removed task

class EventQueue:
  pq = []                         # list of entries arranged in a heap
  entry_finder = {}               # mapping of tasks to entries

  def add_task(self, task, delay, t = time.monotonic()):
    if task in self.entry_finder:
      self.remove_task(task)
    entry = [delay + t, task]
    self.entry_finder[task] = entry
    heappush(self.pq, entry)

  def remove_task(self, task):
    entry = self.entry_finder.pop(task)
    entry[-1] = REMOVED

  def next_event(self, t = time.monotonic()):
    while self.pq and self.pq[0][0] <= t:
      delay, task = heappop(self.pq)
      if task is not REMOVED:
        del self.entry_finder[task]
        return task
    return None
