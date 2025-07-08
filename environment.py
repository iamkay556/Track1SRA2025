#from agentpy import Environment

class AuctionEnvironment():
    def __init__(self, model):
        #super().__init__(model)
        self.model = model
        self.current_price = 1
        self.price_step = 1
        self.active_bidders = []