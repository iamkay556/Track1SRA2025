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
        
        # Track auction dynamics
        self.auction_history = []
        self.winner_id = None
        self.final_price = None

    def step(self):
        t = self.t
        if t >= len(self.price_schedule) or len(self.remaining_ids) <= 1:
            self.end_auction()
            return

        self.current_price = self.price_schedule[t]
        
        # Store new dropouts this round
        new_dropouts = []
        
        # Check which bidders drop out at this price
        for i in self.remaining_ids[:]:  # Copy list to avoid modification during iteration
            bidder = self.bidders[i]
            current_valuation = bidder.valuation_history[-1]
            
            # Bidder drops out if current price exceeds their valuation
            if self.current_price > current_valuation:
                new_dropouts.append((i, self.current_price))
                self.dropout_prices.append(self.current_price)
                self.remaining_ids.remove(i)

        # Update valuations for remaining bidders
        remaining_count = len(self.remaining_ids)
        
        for bidder in self.bidders:
            bidder.update_valuation(
                current_price=self.current_price,
                dropout_prices=self.dropout_prices,
                remaining_bidders=remaining_count,
                time_step=t
            )
        
        # Record auction state
        self.auction_history.append({
            'round': t,
            'price': self.current_price,
            'remaining_bidders': remaining_count,
            'new_dropouts': len(new_dropouts),
            'valuations': [b.valuation_history[-1] for b in self.bidders]
        })
        
        print(f"Round {t}: Price=${self.current_price}, Remaining: {remaining_count}, New dropouts: {len(new_dropouts)}")

    def end_auction(self):
        """End the auction and determine winner"""
        if len(self.remaining_ids) == 1:
            self.winner_id = self.remaining_ids[0]
            self.final_price = self.current_price
            print(f"Auction ended! Winner: Bidder {self.winner_id}, Final price: ${self.final_price}")
        elif len(self.remaining_ids) > 1:
            # If auction ends with multiple bidders, highest valuation wins
            remaining_valuations = [(i, self.bidders[i].valuation_history[-1]) 
                                  for i in self.remaining_ids]
            self.winner_id = max(remaining_valuations, key=lambda x: x[1])[0]
            self.final_price = self.current_price
            print(f"Auction ended at max rounds! Winner: Bidder {self.winner_id}, Final price: ${self.final_price}")
        else:
            print("Auction ended with no bidders remaining!")
        
        self.stop()

    def end(self):
        print('Processing results...')
        valuation_matrix = np.array([b.valuation_history for b in self.bidders])
        
            # Calculate convergence metrics
        final_valuations = [b.valuation_history[-1] for b in self.bidders]
        avg_final_valuation = np.mean(final_valuations)
        valuation_std = np.std(final_valuations)
        
        print(f"True common value: ${self.p.common_value}")
        print(f"Average final valuation: ${avg_final_valuation:.2f}")
        print(f"Valuation standard deviation: ${valuation_std:.2f}")
        print(f"Convergence error: ${abs(avg_final_valuation - self.p.common_value):.2f}")
        
        self.report = ap.DataDict({
            'valuation_matrix': valuation_matrix,
            'auction_history': self.auction_history,
            'winner_id': self.winner_id,
            'final_price': self.final_price,
            'convergence_error': abs(avg_final_valuation - self.p.common_value)
        })