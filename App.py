from MainUi import MainUi
from Player import Player

class App:
  def __init__(self, trellis):
    self.players = [
      Player('left'),
      Player('right'),
    ]

    self.main_ui = MainUi(trellis, self)
    self.current_ui = self.main_ui

  def render(self, t):
    self.current_ui.render(t)

  def handle_keys(self, t, keys):
    self.current_ui.handle_keys(t, keys)

  def switch_ui(self, ui, player = None):
    if ui == 'main':
      self.current_ui = self.main_ui
    elif ui == 'chains':
      self.current_ui = self.chain_ui
      self.chain_ui.set_player(player)
