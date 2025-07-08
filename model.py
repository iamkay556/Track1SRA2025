from agentpy import Model, AgentList
from agent import Bidder
from environment import AuctionEnvironment

class AuctionModel(Model):
    def setup(self):
        self.environment = AuctionEnvironment(self)
        self.bidders = AgentList(self, self.p.n_bidders, Bidder)

        for i, agent in enumerate(self.bidders):
            agent.p.valuation = self.p.valuations[i]
            agent.p.rat = self.p.rational_flags[i]
            agent.initialize()

    def step(self):
        self.environment.active_bidders = []
        for bidder in self.bidders:
            bidder.step()

        if len(self.environment.active_bidders) <=1:
            self.stop()
        else:
            self.environment.current_price += self.environment.price_step

    def end(self):
        winner = None
        for bidder in self.bidders:
            if not bidder.droppedout:
                winner = bidder
        self.report('winner_valuation', winner.value if winner else None)
        self.report('final_price', self.environment.current_price)