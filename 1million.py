import agentpy as ap
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
import seaborn as sns
from typing import Dict, List, Tuple
import itertools
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# === CONFIGURATION ===
BIDDER_TYPES = {
    'malleable/flex': {'a_value': 0.0, 'color': 'blue'},
    'strategic/respon': {'a_value': 0.33, 'color': 'green'},
    'balanced': {'a_value': 0.5, 'color': 'red'},
    'confident': {'a_value': 0.7, 'color': 'purple'},
    'static/inflex': {'a_value': 1.0, 'color': 'orange'},
}
COMMON_VALUE = 1000
SIGNAL_STD = 150
START_PRICE = 500
PRICE_INCREMENT = 20
MAX_STEPS = 1000
N_RUNS = 1  # Number of auctions to run per combination
TOTAL_BIDDERS = 20

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
                remaining_valuations = [(i, self.bidders[i].valuation_history[-1]) for i in self.remaining_ids]
                max_val = max(remaining_valuations, key=lambda x: x[1])[1]
                tied_bidders = [i for i, val in remaining_valuations if val == max_val]
                winner_id = np.random.choice(tied_bidders)
            self.winner = self.bidders[winner_id]
        else:
            all_valuations = [(i, self.bidders[i].valuation_history[-1]) for i in range(len(self.bidders))]
            max_val = max(all_valuations, key=lambda x: x[1])[1]
            tied_bidders = [i for i, val in all_valuations if val == max_val]
            winner_id = np.random.choice(tied_bidders)
            self.winner = self.bidders[winner_id]
        self.auction_ended = True
        self.stop()

def generate_all_combinations():
    """Generate all possible combinations of 20 bidders from 5 types"""
    combinations = []
    # Generate all non-negative integer solutions to: x1 + x2 + x3 + x4 + x5 = 20
    types = list(BIDDER_TYPES.keys())
    
    for combo in itertools.combinations_with_replacement(range(TOTAL_BIDDERS + 1), 5):
        # Convert to actual counts
        counts = []
        remaining = TOTAL_BIDDERS
        for i in range(4):
            count = min(combo[i], remaining)
            counts.append(count)
            remaining -= count
        counts.append(remaining)
        
        if sum(counts) == TOTAL_BIDDERS and all(c >= 0 for c in counts):
            combinations.append(dict(zip(types, counts)))
    
    # Use a more systematic approach
    combinations = []
    for a in range(TOTAL_BIDDERS + 1):
        for b in range(TOTAL_BIDDERS + 1 - a):
            for c in range(TOTAL_BIDDERS + 1 - a - b):
                for d in range(TOTAL_BIDDERS + 1 - a - b - c):
                    e = TOTAL_BIDDERS - a - b - c - d
                    if e >= 0:
                        combo = {
                            'malleable/flex': a,
                            'strategic/respon': b,
                            'balanced': c,
                            'confident': d,
                            'static/inflex': e
                        }
                        combinations.append(combo)
    
    print(f"Generated {len(combinations)} combinations")
    return combinations

def run_auction_once(bidder_counts):
    bidder_config = {}
    for btype, count in bidder_counts.items():
        bidder_config[btype] = {
            'count': count,
            'a_value': BIDDER_TYPES[btype]['a_value'],
            'color': BIDDER_TYPES[btype]['color']
        }
    
    params = {
        'common_value': COMMON_VALUE,
        'signal_std': SIGNAL_STD,
        'start_price': START_PRICE,
        'price_increment': PRICE_INCREMENT,
        'steps': MAX_STEPS,
        'bidder_config': bidder_config,
        'n_bidders': TOTAL_BIDDERS
    }
    model = FlexibleAuction(params)
    model.run()
    return model

def run_comprehensive_analysis():
    """Run analysis for all combinations"""
    combinations = generate_all_combinations()
    results = []
    
    print(f"Running {len(combinations)} combinations with {N_RUNS} runs each...")
    total_sims = len(combinations) * N_RUNS
    print(f"Total simulations: {total_sims:,}")
    
    sim_counter = 0
    for combo_idx, combo in enumerate(combinations):
        # Run N_RUNS auctions for this combination
        combo_results = {
            'combination': combo,
            'winner_types': [],
            'final_prices': [],
            'round_counts': [],
            'winner_valuations': [],
            'efficiency': []  # How close to true value
        }
        
        for run in range(N_RUNS):
            model = run_auction_once(combo)
            combo_results['winner_types'].append(model.winner.bidder_type)
            combo_results['final_prices'].append(model.final_price)
            combo_results['round_counts'].append(model.round_number)
            combo_results['winner_valuations'].append(model.winner.valuation_history[-1])
            combo_results['efficiency'].append(abs(model.final_price - COMMON_VALUE))
            
            sim_counter += 1
        
            percent = 100 * sim_counter / total_sims
            print(f"Progress: {sim_counter}/{total_sims} simulations done ({percent:.2f}%)")
        
        results.append(combo_results)
    
    return results

def create_comprehensive_visualizations(results):
    """Create comprehensive visualizations for the research project"""
    # Convert results to DataFrame for easier analysis
    df_data = []
    for combo_result in results:
        combo = combo_result['combination']
        for i in range(len(combo_result['winner_types'])):
            row = {
                'malleable_count': combo['malleable/flex'],
                'strategic_count': combo['strategic/respon'],
                'balanced_count': combo['balanced'],
                'confident_count': combo['confident'],
                'static_count': combo['static/inflex'],
                'winner_type': combo_result['winner_types'][i],
                'final_price': combo_result['final_prices'][i],
                'round_count': combo_result['round_counts'][i],
                'winner_valuation': combo_result['winner_valuations'][i],
                'efficiency': combo_result['efficiency'][i]
            }
            df_data.append(row)
    df = pd.DataFrame(df_data)
    # Print summary statistics table
    print("Creating summary statistics...")
    summary_stats = df.groupby('winner_type').agg({
        'final_price': ['mean', 'std', 'min', 'max'],
        'round_count': ['mean', 'std'],
        'efficiency': ['mean', 'std'],
        'winner_valuation': ['mean', 'std']
    }).round(2)
    print("\nSUMMARY STATISTICS BY WINNER TYPE:")
    print("=" * 60)
    print(summary_stats)
    return df

def main():
    print("Starting Comprehensive Auction Analysis...")
    print("=" * 60)
    
    # Run the comprehensive analysis
    results = run_comprehensive_analysis()
    
    # Create visualizations
    print("\nCreating visualizations...")
    df = create_comprehensive_visualizations(results)
    
    # Save results
    print("\nSaving results...")
    df.to_csv('auction_results_comprehensive.csv', index=False)
    
    print("\nAnalysis complete! Check the generated plots and CSV file.")
    print(f"Total simulations run: {len(df):,}")
    print(f"Unique compositions tested: {len(df.groupby(['malleable_count', 'strategic_count', 'balanced_count', 'confident_count', 'static_count']))}")

if __name__ == "__main__":
    main()