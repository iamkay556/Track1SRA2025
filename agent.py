import agentpy as ap
import numpy as np

class RationalBidder(ap.Agent):
    def setup(self):
        self.valuation_history = [self.p.common_value]  # All bidders start with common value
        self.active = True  # True = not yet dropped

    def update_valuation(self, current_price, dropout_prices, dropout_rounds, remaining_bidders, time_step):
        if not self.active:
            self.valuation_history.append(self.valuation_history[-1])
            return

        k = len(dropout_prices)
        m = self.p.n_bidders
        r = remaining_bidders
        v_last = self.valuation_history[-1]

        # Static weights
        a_t = 0.33
        b_t = 0.33
        c_t = 0.33

        # Dropout correction
        dropout_term = 0
        if k > 0:
            for n, d_n in enumerate(dropout_prices):  # use index to define w(n)
                w_n = (n + 1)**2  # earlier dropouts weigh more
                diff = v_last - d_n
                dropout_term += (diff**2) / w_n
            dropout_term = (b_t / k) * dropout_term

        # Group signal
        group_signal_term = c_t * (r / m) * current_price

        # New valuation
        new_val = a_t * v_last - dropout_term + group_signal_term
        self.valuation_history.append(new_val)

        # Drop out if new value < current price
        if new_val < current_price:
            self.active = False

        print(f"t={time_step}, price={current_price}, val={new_val:.2f}, active={self.active}")
