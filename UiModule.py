from EventQueue import EventQueue

class UiModule:
    def __init__(self):
        self.events = EventQueue()
    
    def render(self, t):
        pass

    def handle_keys(self, t, pressed, down, up):
        pass

    def enter(self, t):
        pass

    def leave(self, t):
        return 0

    def process_events(self, t): 
        while 1:
            event = self.events.next_event(t)
            if event:
                self.dispatch_event(t, event)
            else:
                break

    def dispatch_event(self, t, event):
        pass
