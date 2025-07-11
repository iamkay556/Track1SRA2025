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
        Updated valuation formula with differential responsiveness:
        Lower bidders are more influenced by survival signals
        Higher bidders are more confident in their valuations
        """
        
        previous_val = self.valuation_history[-1]
        total_bidders = self.p.n_bidders
        
        # Calculate relative position: how does my valuation compare to current price?
        price_ratio = previous_val / current_price if current_price > 0 else 1.0
        
        # Dynamic weights based on relative position
        # Lower bidders (price_ratio < 1) should be more responsive to survival signals
        # Higher bidders (price_ratio > 1) should be more confident
        if price_ratio < 0.9:  # Well below current price
            α = 0.4  # Less persistence - more willing to update
            β = 0.2  # Moderate dropout sensitivity
            γ = 0.4  # High survival signal sensitivity
        elif price_ratio < 1.1:  # Close to current price
            α = 0.5  # Moderate persistence
            β = 0.25 # Standard dropout sensitivity
            γ = 0.25 # Moderate survival signal sensitivity
        else:  # Well above current price
            α = 0.7  # High persistence - more confident
            β = 0.2  # Lower dropout sensitivity
            γ = 0.1  # Low survival signal sensitivity
        
        # 1. Dropout adjustment: Only use recent dropouts
        dropout_adjustment = 0
        if len(dropout_prices) > 0:
            # Only consider last 3 dropouts to avoid over-adjustment
            recent_dropouts = dropout_prices[-3:]
            for i, dropout_price in enumerate(recent_dropouts):
                # Weight more recent dropouts higher
                recency_weight = (i + 1) / len(recent_dropouts)
                
                # Dropout effect: if dropout is close to my valuation, it's more informative
                distance_factor = max(0.1, 1.0 / (1.0 + abs(dropout_price - previous_val) / 100))
                
                # Direction: dropouts below my valuation are negative signals
                if dropout_price < previous_val:
                    dropout_adjustment -= recency_weight * distance_factor * 10
                else:
                    dropout_adjustment += recency_weight * distance_factor * 5
        
        # 2. Survival signal: Strong positive signal when others stay at high prices
        survival_rate = remaining_bidders / total_bidders
        
        # The survival signal should be stronger when:
        # - Many bidders remain (high survival rate)
        # - At high prices (current_price is high)
        # - For bidders with lower valuations (they should learn more)
        
        if survival_rate > 0.6 and current_price > previous_val:
            # Strong positive signal: others are bidding above my valuation
            survival_signal = (survival_rate - 0.5) * (current_price - previous_val) * 0.5
        elif survival_rate > 0.4:
            # Moderate positive signal
            survival_signal = (survival_rate - 0.3) * current_price * 0.1
        else:
            # Weak or negative signal when few remain
            survival_signal = (survival_rate - 0.5) * current_price * 0.05
        
        # 3. Combine all information
        new_val = α * previous_val + β * dropout_adjustment + γ * survival_signal
        
        # 4. Bounded rationality with asymmetric bounds
        # Allow more upward movement than downward for learning
        max_upward = self.initial_signal + 3 * self.p.signal_std
        max_downward = self.initial_signal - 1.5 * self.p.signal_std
        
        new_val = np.clip(new_val, max_downward, max_upward)
        
        # 5. Ensure gradual updates (no huge jumps)
        max_change = 0.15 * previous_val  # Max 15% change per round
        if abs(new_val - previous_val) > max_change:
            if new_val > previous_val:
                new_val = previous_val + max_change
            else:
                new_val = previous_val - max_change
        
        self.valuation_history.append(new_val)