class Player:
  def __init__(self, side):
    self.side = side
    self.keys = [ False, False, False ]
    self.chains = 0 if side == 'left' else 0

  def toggle_key(self, i):
    self.keys[i] = not self.keys[i]
  
  def increase_chains(self):
    self.chains = min(24, self.chains + 1)
  
  def decrease_chains(self):
    self.chains = max(0, self.chains - 1)
