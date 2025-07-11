import agentpy as ap
import numpy as np

class RationalBidder(ap.Agent):
    def setup(self):
        # Initial private signal about the common value
        self.signal = np.random.normal(self.p.common_value, self.p.signal_std)
        self.valuation_history = [self.signal]
        
        # Track for learning
        self.observed_dropouts = []
        self.initial_signal = self.signal

    def update_valuation(self, current_price, dropout_prices, remaining_bidders, time_step):
        """
        Updated valuation formula based on auction theory:
        v_i(t) = α * v_i(t-1) + β * dropout_adjustment + γ * survival_signal
        """
        
        # Dynamic weights that change over time
        α = 0.6  # Weight on previous valuation (persistence)
        β = 0.25  # Weight on dropout information
        γ = 0.15  # Weight on survival signal
        
        previous_val = self.valuation_history[-1]
        
        # 1. Dropout adjustment: Recent dropouts are more informative
        dropout_adjustment = 0
        if len(dropout_prices) > 0:
            # Weight recent dropouts more heavily
            for i, dropout_price in enumerate(dropout_prices):
                recency_weight = 1.0 / (len(dropout_prices) - i)  # More recent = higher weight
                
                # If dropout price is below my valuation, it's bad news (item worth less)
                # If dropout price is above my valuation, it's good news (item worth more)
                price_diff = dropout_price - previous_val
                dropout_adjustment += recency_weight * price_diff * 0.1  # Small adjustment factor
        
        # 2. Survival signal: The fact that others are still bidding is informative
        total_bidders = self.p.n_bidders
        survival_rate = remaining_bidders / total_bidders
        
        # If many bidders remain at high prices, that's a positive signal
        # If few bidders remain, that's a negative signal
        survival_signal = (survival_rate - 0.5) * current_price * 0.1
        
        # 3. Combine all information
        new_val = α * previous_val + β * dropout_adjustment + γ * survival_signal
        
        # 4. Bounded rationality: Don't deviate too far from initial signal
        max_deviation = 2 * self.p.signal_std
        new_val = np.clip(new_val, 
                         self.initial_signal - max_deviation, 
                         self.initial_signal + max_deviation)
        
        self.valuation_history.append(new_val)