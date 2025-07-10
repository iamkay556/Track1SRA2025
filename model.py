import agentpy as ap
import numpy as np
from agent import RationalBidder

class EnglishAuctionModel(ap.Model):
    def setup(self):
        self.bidders = ap.AgentList(self, self.p.n_bidders, RationalBidder)
        self.current_price = self.p.start_price
        self.dropout_prices = []
        self.remaining_ids = list(range(self.p.n_bidders))
        self.price_schedule = [self.p.start_price + i * self.p.price_increment for i in range(self.p.steps)]

    def step(self):
        t = self.t
        if t >= len(self.price_schedule) or len(self.remaining_ids) <= 1:
            self.stop()
            return

        self.current_price = self.price_schedule[t]

        for i in self.remaining_ids[:]:
            b = self.bidders[i]
            if self.current_price > b.valuation_history[-1]:
                self.dropout_prices.append(self.current_price)
                self.remaining_ids.remove(i)

        remaining_count = len(self.remaining_ids)

        for b in self.bidders:
            b.update_valuation(
                current_price=self.current_price,
                dropout_prices=self.dropout_prices,
                remaining_bidders=remaining_count,
                time_step=t
            )

    def end(self):
        print('running end()')
        valuation_matrix = np.array([b.valuation_history for b in self.bidders])
        self.report = ap.DataDict({'valuation_matrix': valuation_matrix})