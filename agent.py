import agentpy as ap
import numpy as np

class RationalBidder(ap.Agent):
    def setup(self):
        self.signal = np.random.normal(self.p.common_value, self.p.signal_std)
        self.valuation_history = [self.signal]
        self.initial_signal = self.signal

    def a_t(self, t):
        return 0.8 * np.exp(-0.05 * t) + 0.2  # High trust at first, slowly decays

    def w_n(self, n):
        return n + 1  # Simple linear recency weight (1, 2, 3...)

    def update_valuation(self, current_price, dropout_prices, remaining_bidders, time_step):
        prev_val = self.valuation_history[-1]
        v_i = prev_val
        m = self.p.n_bidders
        r = remaining_bidders
        k = len(dropout_prices)
        p_t = current_price
        t = time_step

        # --- Dynamic weights ---
        a = self.a_t(t)
        delta = 1 - a
        b = delta * (k / m) if m > 0 else 0
        c = delta * (r / m) if m > 0 else 0

        # --- Dropout adjustment ---
        dropout_adjustment = 0
        if k > 0:
            for idx, d_n in enumerate(dropout_prices):
                if v_i > d_n and p_t <= v_i:
                    weight = 1 / self.w_n(idx)
                    dropout_adjustment += weight * (v_i - d_n)
            dropout_adjustment *= (b / k)

        # --- Survival signal ---
        survival_signal = c * p_t

        # --- Final valuation update ---
        new_val = a * v_i - dropout_adjustment + survival_signal

        # --- Bounded rationality ---
        max_upward = self.initial_signal + 2 * self.p.signal_std
        max_downward = self.initial_signal - 2 * self.p.signal_std
        new_val = np.clip(new_val, max_downward, max_upward)

        self.valuation_history.append(new_val)