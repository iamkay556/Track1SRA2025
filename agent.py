import agentpy as ap
import numpy as np

class RationalBidder(ap.Agent):
    def setup(self):
        self.signal = np.random.normal(self.p.common_value, self.p.signal_std)
        self.valuation_history = [self.signal]

    def update_valuation(self, current_price, dropout_prices, remaining_bidders, time_step):
        k = len(dropout_prices)
        m = self.p.n_bidders
        r = remaining_bidders

        a_t = 0.33
        b_t = 0.33
        c_t = 0.34

        dropout_term = 0
        if k > 0:
            for n, d_n in enumerate(dropout_prices, 1):
                w_n = 1 / n
                dropout_term += (1 / w_n) * (self.valuation_history[-1] - d_n)
            dropout_term = (b_t / k) * dropout_term

        previous_val = self.valuation_history[-1]
        group_signal_term = c_t * (r / m) * current_price
        new_val = a_t * previous_val - dropout_term + group_signal_term
        self.valuation_history.append(new_val)