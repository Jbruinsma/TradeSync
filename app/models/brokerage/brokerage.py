class Brokerage:

    def __init__(self):
        self.settings = None
        self.current_orders = {}
        self.current_positions = {}
        self.state = {}

    def set_settings(self, settings):
        self.settings = settings