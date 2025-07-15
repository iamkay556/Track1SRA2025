import agentpy as ap
import numpy as np
from BidderClass import BidderClass

class AuctionClass(ap.Model):
    # Set starting values
    def setup(self):
        # Bidders
        self.bidders = ap.AgentList(self, self.p.total_bidders, BidderClass)    # AgentList; Bidder list
        
        # Changing Variables
        self.auction_ended = False                              # Bool; True if ongoing, False if ended
        self.current_time = 0                                   # Int; current time
        self.current_price = self.p.start_price                 # Int; current price
        self.remaining_ids = list(range(self.p.total_bidders))  # List; ids of bidders in
        self.dropout_prices = []                                # Array; drop-out prices
        
        # End Variables
        self.winner = None              # Bidder; winning bidder
        self.final_price = None         # Int; selling price
        
        # Data Collection
        self.auction_history = []                               # Array; records time, price, bidders in, new drops, valuations in each element
        self.price_history = [self.current_price]               # Array; records prices
        self.active_bidders_history = [self.p.total_bidders]    # Array; records bidders in


    # Increase time
    def step(self):
        # End auction if there is less than 2 bidders in
        if len(self.remaining_ids) <= 1:
            self.end_auction()
            return
        
        # Increment time and price
        self.current_time += 1
        self.current_price += self.p.price_increment

        # To store this time's drops
        new_dropouts = []

        # Get new drops
        for i in self.remaining_ids[:]:
            # Make a copy
            bidder = self.bidders[i]

            # Remove if bidder's valuation is lower than the new price
            if bidder.should_dropout(self.current_price):
                # Update bidder values
                bidder.active = False
                bidder.dropout_time = self.current_time

                # Update dropout_prices
                self.dropout_prices.append(self.current_price)

                # Updates this time's drop-outs
                new_dropouts.append((i, self.current_price))
                
                # Remove bidder
                self.remaining_ids.remove(i)

        # Number of bidders still in
        remaining_count = len(self.remaining_ids)

        # Update remaining bidders' valuations
        for bidder in self.bidders:
            bidder.update_valuation(
                current_price = self.current_price,
                dropout_prices = self.dropout_prices,
                remaining_bidders = remaining_count,
                time_step = self.current_time
            )
        
        # Update auction_history
        self.auction_history.append({
            'Time': self.current_time,
            'Price': self.current_price,
            'Bidders In': remaining_count,
            'New Drop-outs': len(new_dropouts),
            'Valuations': [b.valuation_history[-1] for b in self.bidders]
        })

        # Update price and bidder histories
        self.price_history.append(self.current_price)
        self.active_bidders_history.append(remaining_count)

        # Log time information
        print(f"Time {self.current_time}: Price=${self.current_price}, Remaining: {remaining_count}, New dropouts: {len(new_dropouts)}")


    # End auction and save/log statistics
    def end_auction(self):
        # Change ended boolean
        self.auction_ended = True

        # Finds winner; chooses if ambiguous
        if len(self.remaining_ids) == 1:
            self.winner = self.bidders[self.remaining_ids[0]]
            self.final_price = self.current_price

            print(f"\nAuction ended! Winner: Bidder {self.winner}, Final price: ${self.final_price}")
        
        elif len(self.remaining_ids) > 1:
            # Picks higher of valuations as winner
            remaining_valuations = [(i, self.bidders[i].valuation_history[-1]) for i in self.remaining_ids]
            winner = max(remaining_valuations, key = lambda x: x[1])[0]
            
            self.winner = self.bidders[winner]
            self.final_price = self.current_price

            print(f"\nAuction ended with multiple bidders! Winner: Bidder {winner}, Final price: ${self.final_price}")
        
        else:
            print("\nAuction ended with no bidders remaining!")

        # Data
        valuation_matrix = np.array([b.valuation_history for b in self.bidders])

        final_valuations = [b.valuation_history[-1] for b in self.bidders]
        avg_final_valuation = np.mean(final_valuations)

        self.report = ap.DataDict({
            'valuation_matrix': valuation_matrix,
            'auction_history': self.auction_history,
            'winner': self.winner,
            'final_price': self.final_price,
            'convergence_error': abs(avg_final_valuation - self.p.common_value)
        })

        self.stop()
