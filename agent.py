from agentpy import Agent
import numpy as np

class Bidder(Agent):

    def setup(self):
        self.droppedout = False

    def initialize(self):
        self.value = self.p.valuation
        self.is_rat = self.p.rat
        # self.p in agentpy is special object given to each agnet/model access to parameters passed i simulation when created

    def step(self):
        if self.droppedout:
            return
            
        current_price = self.model.environment.current_price

        if self.is_rat:
            if current_price < self.value:
                self.model.environment.active_bidders.append(self)
            else:
                self.droppedout = True

        else:
            dropout_chance = np.random.rand()
            noise_margin = self.value * np.random.uniform(.8,1)

            if dropout_chance < .2 or current_price >= noise_margin:
                self.droppedout = True
            else:
                self.model.environment.active_bidders.append(self)
