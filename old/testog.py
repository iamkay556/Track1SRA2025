import agentpy as ap
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
import seaborn as sns
from typing import Dict, List, Tuple

class RationalBidder(ap.Agent):
    """Rational bidder agent using AgentPy framework with original valuation equation"""
    
    def setup(self):
        # Core attributes
        self.signal = np.random.normal(self.model.p.common_value, self.model.p.signal_std)
        self.valuation_history = [self.signal]
        self.initial_signal = self.signal
        self.active = True
        self.dropout_round = None
        
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
                    dropout_adjustment += -1.0 * ((v_prev - d_n))
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
    
    def should_dropout(self, current_price: float) -> bool:
        """Rational dropout decision with small noise"""
        if not self.active:
            return False
            
        # Add tiny amount of noise to prevent exact ties
        noise_std = 0.01 * self.model.p.signal_std
        noisy_threshold = self.valuation_history[-1] + np.random.normal(0, noise_std)
        
        return current_price > noisy_threshold

class EnglishAuction(ap.Model):
    """English auction model using AgentPy framework"""
    
    def setup(self):
        # Create bidders using AgentPy
        self.bidders = ap.AgentList(self, self.p.n_bidders, RationalBidder)
        self.current_price = self.p.start_price
        self.dropout_prices = []
        self.remaining_ids = list(range(self.p.n_bidders))
        self.round_number = 0
        
        # State variables
        self.auction_ended = False
        self.winner = None
        self.final_price = None
        
        # Data collection
        self.auction_history = []
        self.price_history = [self.current_price]
        self.active_bidders_history = [self.p.n_bidders]
        
    def step(self):
        """Run one round of the auction"""
        if len(self.remaining_ids) <= 1:
            self.end_auction()
            return

        self.current_price += self.p.price_increment
        self.round_number += 1

        new_dropouts = []

        for i in self.remaining_ids[:]:  # Copy to allow safe removal
            bidder = self.bidders[i]
            if bidder.should_dropout(self.current_price):
                new_dropouts.append((i, self.current_price))
                self.dropout_prices.append(self.current_price)
                self.remaining_ids.remove(i)
                bidder.active = False
                bidder.dropout_round = self.round_number

        remaining_count = len(self.remaining_ids)

        # Update all bidders
        for bidder in self.bidders:
            bidder.update_valuation(
                current_price=self.current_price,
                dropout_prices=self.dropout_prices,
                remaining_bidders=remaining_count,
                time_step=self.round_number
            )

        # Record history
        self.auction_history.append({
            'round': self.round_number,
            'price': self.current_price,
            'remaining_bidders': remaining_count,
            'new_dropouts': len(new_dropouts),
            'valuations': [b.valuation_history[-1] for b in self.bidders]
        })
        
        self.price_history.append(self.current_price)
        self.active_bidders_history.append(remaining_count)

        print(f"Round {self.round_number}: Price=${self.current_price}, Remaining: {remaining_count}, New dropouts: {len(new_dropouts)}")

    def end_auction(self):
        self.auction_ended = True
        if len(self.remaining_ids) == 1:
            self.winner = self.bidders[self.remaining_ids[0]]
            self.final_price = self.current_price
            print(f"Auction ended! Winner: Bidder {self.remaining_ids[0]}, Final price: ${self.final_price}")
        elif len(self.remaining_ids) > 1:
            remaining_valuations = [(i, self.bidders[i].valuation_history[-1]) for i in self.remaining_ids]
            winner_id = max(remaining_valuations, key=lambda x: x[1])[0]
            self.winner = self.bidders[winner_id]
            self.final_price = self.current_price
            print(f"Auction ended with multiple bidders! Winner: Bidder {winner_id}, Final price: ${self.final_price}")
        else:
            print("Auction ended with no bidders remaining!")

        self.stop()
    
    def get_results(self) -> Dict:
        """Get auction results for analysis"""
        results = {
            'final_price': self.final_price,
            'winner_initial_signal': self.winner.initial_signal if self.winner else None,
            'winner_final_valuation': self.winner.valuation_history[-1] if self.winner else None,
            'common_value': self.p.common_value,
            'rounds': self.round_number,
            'total_dropouts': len(self.dropout_prices),
            'price_history': self.price_history,
            'active_bidders_history': self.active_bidders_history,
            'dropouts': self.get_dropout_info()
        }
        
        return results
    
    def get_dropout_info(self):
        """Get detailed dropout information"""
        dropouts = []
        for i, bidder in enumerate(self.bidders):
            if bidder.dropout_round is not None:
                dropouts.append({
                    'bidder_id': i,
                    'price': self.dropout_prices[len([b for b in self.bidders[:i+1] if b.dropout_round is not None]) - 1] if self.dropout_prices else None,
                    'round': bidder.dropout_round,
                    'valuation': bidder.valuation_history[-1],
                    'initial_signal': bidder.initial_signal
                })
        return dropouts

def run_single_auction(**kwargs) -> EnglishAuction:
    """Run a single auction and return the model"""
    
    # Default parameters
    params = {
        'common_value': 100,
        'signal_std': 15,
        'n_bidders': 20,
        'start_price': 20,
        'price_increment': 2,
        'steps': 1000  # Large number to ensure auction completes
    }
    params.update(kwargs)
    
    model = EnglishAuction(params)
    model.run()
    
    return model

def plot_rational_bidder_dynamics(model: EnglishAuction, save_path: str = None):
    """Plot the valuation dynamics of all rational bidders"""
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'Rational Bidders Auction Dynamics (n={model.p.n_bidders})', fontsize=16)
    
    # 1. All bidder valuation trajectories
    colors = plt.cm.tab20(np.linspace(0, 1, model.p.n_bidders))
    
    for i, bidder in enumerate(model.bidders):
        # Plot valuation history up to dropout point
        if bidder.dropout_round is not None:
            # End at dropout round
            rounds_to_plot = min(bidder.dropout_round, len(bidder.valuation_history))
            x_vals = range(rounds_to_plot)
            y_vals = bidder.valuation_history[:rounds_to_plot]
            
            # Plot line
            axes[0, 0].plot(x_vals, y_vals, color=colors[i], alpha=0.7, linewidth=1.5)
            
            # Mark dropout point
            if rounds_to_plot > 0:
                axes[0, 0].scatter(rounds_to_plot-1, y_vals[-1], color=colors[i], 
                                 s=50, marker='x', alpha=0.8)
        else:
            # Winner - plot full history
            x_vals = range(len(bidder.valuation_history))
            y_vals = bidder.valuation_history
            axes[0, 0].plot(x_vals, y_vals, color=colors[i], alpha=0.9, 
                          linewidth=3, label=f'Winner (Bidder {i+1})')
            
            # Mark final point
            if len(y_vals) > 0:
                axes[0, 0].scatter(len(y_vals)-1, y_vals[-1], color=colors[i], 
                                 s=100, marker='o', alpha=1.0)
    
    # Add reference lines
    axes[0, 0].axhline(model.p.common_value, color='red', linestyle='--', 
                       linewidth=2, label='True Common Value')
    axes[0, 0].set_xlabel('Round')
    axes[0, 0].set_ylabel('Valuation')
    axes[0, 0].set_title('Bidder Valuation Trajectories')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Price evolution and active bidders
    price_rounds = range(len(model.price_history))
    axes[0, 1].plot(price_rounds, model.price_history, 'b-o', linewidth=2, 
                   markersize=4, label='Auction Price')
    axes[0, 1].axhline(model.p.common_value, color='red', linestyle='--', 
                       linewidth=2, label='True Common Value')
    axes[0, 1].set_xlabel('Round')
    axes[0, 1].set_ylabel('Price')
    axes[0, 1].set_title('Price Evolution')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Active bidders over time
    active_rounds = range(len(model.active_bidders_history))
    axes[1, 0].plot(active_rounds, model.active_bidders_history, 'g-o', 
                   linewidth=2, markersize=4)
    axes[1, 0].set_xlabel('Round')
    axes[1, 0].set_ylabel('Active Bidders')
    axes[1, 0].set_title('Active Bidders Over Time')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Dropout analysis
    dropouts = model.get_dropout_info()
    if dropouts:
        dropout_rounds = [d['round'] for d in dropouts]
        dropout_prices = [d['price'] for d in dropouts if d['price'] is not None]
        dropout_valuations = [d['valuation'] for d in dropouts]
        initial_signals = [d['initial_signal'] for d in dropouts]
        
        # Plot dropout points
        if dropout_prices:
            axes[1, 1].scatter(dropout_rounds[:len(dropout_prices)], dropout_prices, c='red', 
                              alpha=0.7, s=50, label='Dropout Price')
        axes[1, 1].scatter(dropout_rounds, dropout_valuations, c='blue', 
                          alpha=0.7, s=50, label='Final Valuation')
        axes[1, 1].scatter(dropout_rounds, initial_signals, c='green', 
                          alpha=0.7, s=50, label='Initial Signal')
        
        axes[1, 1].axhline(model.p.common_value, color='red', linestyle='--', 
                          linewidth=2, label='True Common Value')
        axes[1, 1].set_xlabel('Dropout Round')
        axes[1, 1].set_ylabel('Value')
        axes[1, 1].set_title('Dropout Analysis')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()

def analyze_rational_auction(model: EnglishAuction):
    """Analyze the results of a rational bidder auction"""
    
    print("=== RATIONAL BIDDER AUCTION ANALYSIS ===")
    print(f"Common Value: ${model.p.common_value:.2f}")
    print(f"Final Price: ${model.final_price:.2f}")
    print(f"Price Deviation: ${model.final_price - model.p.common_value:.2f}")
    print(f"Efficiency: {model.final_price / model.p.common_value:.3f}")
    print(f"Total Rounds: {model.round_number}")
    print(f"Total Dropouts: {len(model.dropout_prices)}")
    
    if model.winner:
        print(f"\nWINNER ANALYSIS:")
        print(f"Initial Signal: ${model.winner.initial_signal:.2f}")
        print(f"Final Valuation: ${model.winner.valuation_history[-1]:.2f}")
        print(f"Signal Accuracy: {abs(model.winner.initial_signal - model.p.common_value):.2f}")
    
    # Dropout analysis
    dropouts = model.get_dropout_info()
    if dropouts:
        print(f"\nDROPOUT ANALYSIS:")
        dropout_rounds = [d['round'] for d in dropouts]
        dropout_prices = [d['price'] for d in dropouts if d['price'] is not None]
        dropout_vals = [d['valuation'] for d in dropouts]
        initial_sigs = [d['initial_signal'] for d in dropouts]
        
        print(f"Average Dropout Round: {np.mean(dropout_rounds):.1f}")
        if dropout_prices:
            print(f"Average Dropout Price: ${np.mean(dropout_prices):.2f}")
        print(f"Average Final Valuation: ${np.mean(dropout_vals):.2f}")
        print(f"Average Initial Signal: ${np.mean(initial_sigs):.2f}")
        
        # Convergence analysis
        initial_errors = [abs(sig - model.p.common_value) for sig in initial_sigs]
        final_errors = [abs(val - model.p.common_value) for val in dropout_vals]
        
        print(f"\nCONVERGENCE ANALYSIS:")
        print(f"Average Initial Error: ${np.mean(initial_errors):.2f}")
        print(f"Average Final Error: ${np.mean(final_errors):.2f}")
        print(f"Learning Improvement: ${np.mean(initial_errors) - np.mean(final_errors):.2f}")
    
    # Signal distribution analysis
    all_initial_signals = [bidder.initial_signal for bidder in model.bidders]
    print(f"\nSIGNAL DISTRIBUTION:")
    print(f"Signal Mean: ${np.mean(all_initial_signals):.2f}")
    print(f"Signal Std: ${np.std(all_initial_signals):.2f}")
    print(f"Signal Range: ${np.min(all_initial_signals):.2f} to ${np.max(all_initial_signals):.2f}")

def run_multiple_rational_auctions(num_auctions: int = 10, **kwargs):
    """Run multiple rational bidder auctions for comparison"""
    
    results = []
    
    for i in range(num_auctions):
        print(f"\nRunning auction {i+1}/{num_auctions}...")
        model = run_single_auction(**kwargs)
        
        result = {
            'auction': i+1,
            'final_price': model.final_price,
            'common_value': model.p.common_value,
            'rounds': model.round_number,
            'efficiency': model.final_price / model.p.common_value,
            'price_deviation': model.final_price - model.p.common_value,
            'winner_signal': model.winner.initial_signal if model.winner else None,
            'winner_valuation': model.winner.valuation_history[-1] if model.winner else None
        }
        results.append(result)
        
        # Show single auction dynamics for first few auctions
        if i < 3:
            plot_rational_bidder_dynamics(model)
            analyze_rational_auction(model)
    
    # Summary analysis
    df = pd.DataFrame(results)
    print("\n=== SUMMARY ACROSS ALL AUCTIONS ===")
    print(f"Mean Final Price: ${df['final_price'].mean():.2f} ± ${df['final_price'].std():.2f}")
    print(f"Mean Common Value: ${df['common_value'].mean():.2f}")
    print(f"Mean Efficiency: {df['efficiency'].mean():.3f} ± {df['efficiency'].std():.3f}")
    print(f"Mean Price Deviation: ${df['price_deviation'].mean():.2f} ± {df['price_deviation'].std():.2f}")
    print(f"Mean Rounds: {df['rounds'].mean():.1f} ± {df['rounds'].std():.1f}")
    
    return df

# Example usage
if __name__ == "__main__":
    print("Running Rational Bidder English Auction...")
    print("=" * 50)
    
    # Run a single auction with detailed analysis
    model = run_single_auction(
        common_value=100,
        signal_std=15,
        n_bidders=20,
        start_price=20,
        price_increment=2
    )
    
    # Analyze and visualize
    analyze_rational_auction(model)
    plot_rational_bidder_dynamics(model)
    
    # Optional: Run multiple auctions for statistical analysis
    print("\n" + "="*50)
    print("RUNNING MULTIPLE AUCTIONS FOR COMPARISON...")
    
    multiple_results = run_multiple_rational_auctions(
        num_auctions=5,
        common_value=1000,
        signal_std=150,
        n_bidders=20,
        start_price=600,
        price_increment=20
    )
    
    print("\nAll auctions completed!")