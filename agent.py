import agentpy as ap
import numpy as np

class RationalBidder(ap.Agent):
    def setup(self):
        self.signal = np.random.normal(self.model.p.common_value, self.model.p.signal_std)
        self.valuation_history = [self.signal]
        self.initial_signal = self.signal
        self.active = True  # Track whether bidder has dropped

    def a_t(self, t):
        return 0.8 * np.exp(-0.05 * t) + 0.2  # Decaying trust in initial signal

    def update_valuation(self, current_price, dropout_prices, remaining_bidders, time_step):
        if not self.active:
            # Once dropped out, hold valuation constant
            self.valuation_history.append(self.valuation_history[-1])
            return

        v_prev = self.valuation_history[-1]
        m = self.model.p.n_bidders
        r = remaining_bidders
        k = len(dropout_prices)
        p_t = current_price
        t = time_step

        # -- Dynamic weights --
        a = self.a_t(t)
        delta = 1 - a
        b = delta * (k / m) if m > 0 else 0
        c = delta * (r / m) if m > 0 else 0

        # -- Dropout signal: overestimators get penalized
        dropout_adjustment = 0
        if k > 0:
            for d_n in dropout_prices:
                if v_prev > d_n:
                    dropout_adjustment += -1.0 * ((v_prev - d_n) / v_prev)
            dropout_adjustment *= (b / k)

        # -- Survival signal: boosts confidence near price
        proximity = 1 - abs(v_prev - p_t) / v_prev
        proximity = np.clip(proximity, 0, 1)
        survival_signal = c * (proximity ** 2) * p_t

        # -- Valuation update --
        v_new = a * v_prev + dropout_adjustment + survival_signal

        # -- Bounded rationality --
        max_val = self.initial_signal + 2 * self.model.p.signal_std
        min_val = self.initial_signal - 2 * self.model.p.signal_std
        v_new = np.clip(v_new, min_val, max_val)

        self.valuation_history.append(v_new)
