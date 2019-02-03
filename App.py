from MainUi import MainUi
from Player import Player
from ChainsUi import ChainsUi

class App:
  def __init__(self, trellis):
    self.trellis = trellis

    self.players = [
      Player('left'),
      Player('right'),
    ]

    self.switch_ui('main')
    # self.switch_ui('chains', self.players[1])

  def render(self, t):
    self.current_ui.render(t)

  def handle_keys(self, t, pressed, down, up):
    self.current_ui.handle_keys(t, pressed, down, up)

  def switch_ui(self, ui, player = None):
    self.trellis.pixels.fill((0, 0, 0))

    if ui == 'main':
      self.current_ui = MainUi(self.trellis, self)
    elif ui == 'chains':
      self.current_ui = ChainsUi(self.trellis, self, player)
