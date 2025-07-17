import agentpy as ap
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
import seaborn as sns
from typing import Dict, List, Tuple

# === CONFIGURATION ===
BIDDER_TYPES = {
    'malleable/flex': {'count': 0, 'a_value': 0.0, 'color': 'blue'},
    'strategic/respon': {'count': 0, 'a_value': 0.33, 'color': 'green'},
    'balanced': {'count': 10, 'a_value': .5, 'color': 'red'},
    'confident': {'count': 10, 'a_value': .7, 'color': 'purple'},
    'static/inflex': {'count': 0, 'a_value': 1, 'color': 'yellow'},
}
COMMON_VALUE = 1000
SIGNAL_STD = 150
START_PRICE = 500
PRICE_INCREMENT = 20
MAX_STEPS = 1000
N_RUNS = 1000  # Number of auctions to run

class FlexibleBidder(ap.Agent):
    def setup(self):
        self.signal = np.random.normal(self.model.p.common_value, self.model.p.signal_std)
        self.initial_signal = self.signal
        self.valuation_history = [self.signal]
        self.active = True
        self.dropout_round = None
        self.bidder_type = getattr(self, 'bidder_type', 'unknown')
        self.a_value = getattr(self, 'a_value', 1.0)
        self.color = getattr(self, 'color', 'gray')

    def update_valuation(self, current_price, dropout_prices, remaining_bidders, time_step):
        if not self.active:
            self.valuation_history.append(self.valuation_history[-1])
            return
        v0 = self.initial_signal
        total = self.model.p.n_bidders
        dropouts = len(dropout_prices)
        a = self.a_value
        b = (1 - a) * (dropouts / total)
        c = (1 - a) * (remaining_bidders / total)
        dropout_term = np.mean(dropout_prices) if dropouts > 0 else 0
        new_val = a * v0 + b * dropout_term + c * current_price
        self.valuation_history.append(new_val)

    def should_dropout(self, price):
        return self.active and price > self.valuation_history[-1]

class FlexibleAuction(ap.Model):
    def setup(self):
        self.bidders = ap.AgentList(self)
        for bidder_type, config in self.p.bidder_config.items():
            for _ in range(config['count']):
                bidder = FlexibleBidder(self)
                bidder.bidder_type = bidder_type
                bidder.a_value = config['a_value']
                bidder.color = config['color']
                self.bidders.append(bidder)
        self.current_price = self.p.start_price
        self.dropout_prices = []
        self.remaining_ids = list(range(len(self.bidders)))
        self.round_number = 0
        self.price_history = [self.current_price]
        self.active_bidders_history = [len(self.remaining_ids)]
        self.final_price = None
        self.winner = None
        self.auction_ended = False

    def step(self):
        if len(self.remaining_ids) <= 1:
            self.end_auction()
            return
        self.current_price += self.p.price_increment
        self.round_number += 1
        for i in self.remaining_ids[:]:
            bidder = self.bidders[i]
            if bidder.should_dropout(self.current_price):
                bidder.active = False
                bidder.dropout_round = self.round_number
                self.dropout_prices.append(self.current_price)
                self.remaining_ids.remove(i)
        for bidder in self.bidders:
            bidder.update_valuation(self.current_price, self.dropout_prices, len(self.remaining_ids), self.round_number)
        self.price_history.append(self.current_price)
        self.active_bidders_history.append(len(self.remaining_ids))
        if self.round_number >= self.p.steps:
            self.end_auction()

    def end_auction(self):
        self.final_price = self.current_price
        if len(self.remaining_ids) >= 1:
            if len(self.remaining_ids) == 1:
                winner_id = self.remaining_ids[0]
            else:
                # Handle ties by randomly selecting from bidders with highest valuation
                remaining_valuations = [(i, self.bidders[i].valuation_history[-1]) for i in self.remaining_ids]
                max_val = max(remaining_valuations, key=lambda x: x[1])[1]
                tied_bidders = [i for i, val in remaining_valuations if val == max_val]
                winner_id = np.random.choice(tied_bidders)
            self.winner = self.bidders[winner_id]
        else:
            # No remaining bidders - select winner from all bidders based on final valuation
            all_valuations = [(i, self.bidders[i].valuation_history[-1]) for i in range(len(self.bidders))]
            max_val = max(all_valuations, key=lambda x: x[1])[1]
            tied_bidders = [i for i, val in all_valuations if val == max_val]
            winner_id = np.random.choice(tied_bidders)
            self.winner = self.bidders[winner_id]
        self.auction_ended = True
        self.stop()

def run_auction_once(bidder_types=BIDDER_TYPES):
    bidder_config = {k: {'count': v['count'], 'a_value': v['a_value'], 'color': v['color']} for k, v in bidder_types.items()}
    n_bidders = sum(cfg['count'] for cfg in bidder_config.values())
    params = {
        'common_value': COMMON_VALUE,
        'signal_std': SIGNAL_STD,
        'start_price': START_PRICE,
        'price_increment': PRICE_INCREMENT,
        'steps': MAX_STEPS,
        'bidder_config': bidder_config,
        'n_bidders': n_bidders
    }
    model = FlexibleAuction(params)
    model.run()
    return model

def plot_flexible_bidder_dynamics_multi(models, save_path: str = None):
    plt.figure(figsize=(12, 6))
    for run_idx, model in enumerate(models):
        for bidder in model.bidders:
            color = getattr(bidder, 'color', 'gray')
            if bidder.dropout_round is not None:
                rounds_to_plot = min(bidder.dropout_round, len(bidder.valuation_history))
                x_vals = range(rounds_to_plot)
                y_vals = bidder.valuation_history[:rounds_to_plot]
                plt.plot(x_vals, y_vals, color=color, alpha=0.5, linewidth=1)
                if rounds_to_plot > 0:
                    plt.scatter(rounds_to_plot-1, y_vals[-1], color=color, s=30, marker='x', alpha=0.7)
            else:
                x_vals = range(len(bidder.valuation_history))
                y_vals = bidder.valuation_history
                plt.plot(x_vals, y_vals, color=color, alpha=0.8, linewidth=2, label=f'Winner ({bidder.bidder_type})' if run_idx == 0 else None)
                if len(y_vals) > 0:
                    plt.scatter(len(y_vals)-1, y_vals[-1], color=color, s=60, marker='o', alpha=0.9)
    # Add auction price for last run
    plt.plot(models[-1].price_history, '--', color='black', linewidth=2, label='Auction Price (last run)')
    plt.axhline(COMMON_VALUE, color='red', linestyle='--', linewidth=2, label='True Common Value')
    for btype, config in BIDDER_TYPES.items():
        plt.plot([], [], color=config['color'], label=f'{btype} (a={config["a_value"]})')
    plt.title(f"Bidder Valuation Trajectories (All {len(models)} Runs)")
    plt.xlabel("Round")
    plt.ylabel("Valuation")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_flexible_bidder_dynamics_single(model, run_idx=None, save_path: str = None):
    plt.figure(figsize=(12, 6))
    for bidder in model.bidders:
        color = getattr(bidder, 'color', 'gray')
        if bidder.dropout_round is not None:
            rounds_to_plot = min(bidder.dropout_round, len(bidder.valuation_history))
            x_vals = range(rounds_to_plot)
            y_vals = bidder.valuation_history[:rounds_to_plot]
            plt.plot(x_vals, y_vals, color=color, alpha=0.7, linewidth=1.5)
            if rounds_to_plot > 0:
                plt.scatter(rounds_to_plot-1, y_vals[-1], color=color, s=50, marker='x', alpha=0.8)
        else:
            x_vals = range(len(bidder.valuation_history))
            y_vals = bidder.valuation_history
            plt.plot(x_vals, y_vals, color=color, alpha=0.9, linewidth=3, label=f'Winner ({bidder.bidder_type})')
            if len(y_vals) > 0:
                plt.scatter(len(y_vals)-1, y_vals[-1], color=color, s=100, marker='o', alpha=1.0)
    plt.plot(range(len(model.price_history)), model.price_history, color='black', linestyle='--', linewidth=2, label='Auction Price')
    plt.axhline(COMMON_VALUE, color='red', linestyle='--', linewidth=2, label='True Common Value')
    for btype, config in BIDDER_TYPES.items():
        plt.plot([], [], color=config['color'], label=f'{btype} (a={config["a_value"]})')
    title = f"Bidder Valuation Trajectories (Run {run_idx+1})" if run_idx is not None else "Bidder Valuation Trajectories"
    plt.title(title)
    plt.xlabel("Round")
    plt.ylabel("Valuation")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    print("Running Flexible Bidder Auction...")
    print("=" * 50)
    all_models = []
    winner_types = []
    final_prices = []
    round_counts = []
    for i in range(N_RUNS):
        print(f"Run {i+1}/{N_RUNS}")
        model = run_auction_once(BIDDER_TYPES)
        all_models.append(model)
        winner_types.append(model.winner.bidder_type if model.winner else 'None')
        final_prices.append(model.final_price)
        round_counts.append(model.round_number)
        # Only plot the first 5 runs
        if i < 10:
            plot_flexible_bidder_dynamics_single(model, run_idx=i)
    print(f"Winner Types: {winner_types}")
    print(f"Final Prices: {final_prices}")
    print(f"Round Counts: {round_counts}")
    
    # Calculate statistics
    print("\n" + "="*50)
    print("STATISTICS SUMMARY")
    print("="*50)
    
    # Win percentage by bidder type
    winner_counts = {}
    for winner_type in winner_types:
        winner_counts[winner_type] = winner_counts.get(winner_type, 0) + 1
    
    print("\nWIN PERCENTAGE BY BIDDER TYPE:")
    for bidder_type in BIDDER_TYPES.keys():
        wins = winner_counts.get(bidder_type, 0)
        percentage = (wins / N_RUNS) * 100
        print(f"{bidder_type}: {wins}/{N_RUNS} ({percentage:.1f}%)")
    
    # Average final valuation by bidder type
    print("\nAVERAGE FINAL VALUATION BY BIDDER TYPE:")
    for bidder_type in BIDDER_TYPES.keys():
        valuations = []
        for model in all_models:
            for bidder in model.bidders:
                if bidder.bidder_type == bidder_type:
                    valuations.append(bidder.valuation_history[-1])
        if valuations:
            avg_val = np.mean(valuations)
            std_val = np.std(valuations)
            print(f"{bidder_type}: mean: ${avg_val:.2f}, std: ${std_val:.2f}")
        else:
            print(f"{bidder_type}: No bidders")
    
    # Average final price
    avg_final_price = np.mean(final_prices)
    std_final_price = np.std(final_prices)
    print(f"\nAVERAGE FINAL PRICE: mean: ${avg_final_price:.2f}, std: ${std_final_price:.2f}")
    print(f"AVERAGE ROUNDS: mean: {np.mean(round_counts):.1f}, std: {np.std(round_counts):.1f}")