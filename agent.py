import agentpy as ap
import numpy as np

class RationalBidder(ap.Agent):
    def setup(self):
        # Each agent gets an initial noisy signal about the common value
        self.signal = np.random.normal(self.p.common_value, self.p.signal_std)
        self.valuation_history = [self.signal]
        self.initial_signal = self.signal

    def update_valuation(self, current_price, dropout_prices, remaining_bidders, time_step):
        """
        Update valuation using:
        v_i(t) = a(t) * v_i(t-1) 
                - (b(t)/k) * sum_n( (1/w(n)) * (v_i(t-1) - d_n) )
                + c(t) * (r/m) * p(t)
        """

        prev_val = self.valuation_history[-1]
        total_bidders = self.p.n_bidders
        k = len(dropout_prices)
        r = remaining_bidders
        m = total_bidders
        t = time_step

        # Define weight functions for a(t), b(t), c(t)
        a_t = 0.6  # Trust own opinion
        b_t = 0.3  # Trust dropout signals
        c_t = 0.3  # Trust survival signal

        # ---- DROP-OUT SIGNAL TERM ----
        dropout_term = 0
        if k > 0:
            for idx, d_n in enumerate(dropout_prices):
                w_n = idx + 1  # w(n) = n+1 to avoid divide-by-zero
                dropout_term += (1 / w_n) * (prev_val - d_n)
            dropout_term *= (b_t / k)
        else:
            dropout_term = 0

        # ---- SURVIVAL SIGNAL TERM ----
        survival_rate = r / m
        survival_signal = c_t * survival_rate * current_price

        # ---- FINAL VALUATION ----
        new_val = a_t * prev_val - dropout_term + survival_signal

        # Optional: bounding (same as before)
        max_upward = self.initial_signal + 2 * self.p.signal_std
        max_downward = self.initial_signal - 2 * self.p.signal_std
        new_val = np.clip(new_val, max_downward, max_upward)

        self.valuation_history.append(new_val)
