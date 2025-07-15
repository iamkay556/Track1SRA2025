import agentpy as ap
import numpy as np

class BidderClass(ap.Agent):
    # Set starting values
    def setup(self):
        # General
        self.active = True                                                                          # Bool; True if in, False if out
        self.signal = np.random.normal(self.model.p.common_value, self.model.p.standard_deviation)  # Int; generate initial signal
        
        # History
        self.valuation_history = [self.signal]      # Array; valuations over time

        # End Values
        self.dropout_time = None            # Int; time when dropped
        self.dropout_price = None           # Int; price when dropped


    # Does bidder drop?
    def should_dropout(self, current_price: float) -> bool:
        if not self.active:
            return False

        return current_price > self.valuation_history[-1]


    # Update valuation
    def update_valuation(self, current_price, dropout_prices, remaining_bidders, time_step):
        if (not self.active):
            self.valuation_history.append(self.valuation_history[-1])
            return
        
        # For convenience
        valuation_prev = self.valuation_history[-1]

        # Constants
        a = 1/3
        b = 2/3 * (len(dropout_prices)) / (len(dropout_prices) + (remaining_bidders))
        c = 2/3 * ((remaining_bidders)) / (len(dropout_prices) + (remaining_bidders))

        # Average dropout price calculation
        if (len(dropout_prices) != 0):
            avg_dropout_price = sum(dropout_prices) / len(dropout_prices)
        else:
            avg_dropout_price = 0

        # Get new valuation
        valuation_new = a * self.signal + b * avg_dropout_price + c * current_price
        self.valuation_history.append(valuation_new)


    
