from flask import Flask, render_template, request, jsonify
import agentpy as ap
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
import base64
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import threading
import time

app = Flask(__name__)

# Global variables for simulation state
current_model = None
simulation_running = False
simulation_thread = None

class RationalBidder(ap.Agent):
    def setup(self):
        self.signal = np.random.normal(self.model.p.common_value, self.model.p.signal_std)
        self.initial_signal = self.signal
        self.valuation_history = [self.signal]
        self.active = True
        self.dropout_round = None
        self.bidder_type = getattr(self.model.p, 'bidder_type', 'strategic')
        self.a_value = getattr(self.model.p, 'a_value', 1/3)

    def update_valuation(self, current_price, dropout_prices, remaining_bidders):
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

class NonstrategicBidder(ap.Agent):
    def setup(self):
        self.signal = np.random.normal(self.model.p.common_value, self.model.p.signal_std)
        self.initial_signal = self.signal
        self.valuation_history = [self.signal]
        self.active = True
        self.dropout_round = None
        self.bidder_type = getattr(self.model.p, 'bidder_type', 'naive')
        self.a_value = getattr(self.model.p, 'a_value', 1.0)  # Naive bidders stick to initial signal

    def update_valuation(self, current_price, dropout_prices, remaining_bidders):
        if not self.active:
            self.valuation_history.append(self.valuation_history[-1])
            return

        if self.bidder_type == 'naive':
            # Naive bidders don't update their valuation
            self.valuation_history.append(self.initial_signal)
        elif self.bidder_type == 'overconfident':
            # Overconfident bidders update but with higher weight on initial signal
            v0 = self.initial_signal
            total = self.model.p.n_bidders
            dropouts = len(dropout_prices)
            a = 0.8  # Higher weight on initial signal
            b = (1 - a) * (dropouts / total)
            c = (1 - a) * (remaining_bidders / total)
            dropout_term = np.mean(dropout_prices) if dropouts > 0 else 0
            new_val = a * v0 + b * dropout_term + c * current_price
            self.valuation_history.append(new_val)
        else:
            # Default to strategic behavior
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

class MixedEnglishAuction(ap.Model):
    def setup(self):
        self.bidders = ap.AgentList(self)
        
        # Create different types of bidders based on configuration
        bidder_config = getattr(self.p, 'bidder_config', {})
        
        for bidder_type, config in bidder_config.items():
            count = config.get('count', 0)
            a_value = config.get('a_value', 1/3)
            
            for _ in range(count):
                if bidder_type == 'strategic':
                    bidder = RationalBidder(self)
                    bidder.a_value = a_value
                    bidder.bidder_type = bidder_type
                else:
                    bidder = NonstrategicBidder(self)
                    bidder.a_value = a_value
                    bidder.bidder_type = bidder_type
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
            bidder.update_valuation(self.current_price, self.dropout_prices, len(self.remaining_ids))

        self.price_history.append(self.current_price)
        self.active_bidders_history.append(len(self.remaining_ids))

        # Stop after max steps
        if self.round_number >= self.p.steps:
            self.end_auction()

    def end_auction(self):
        self.final_price = self.current_price
        if len(self.remaining_ids) >= 1:
            winner_id = self.remaining_ids[0] if len(self.remaining_ids) == 1 else max(
                self.remaining_ids, key=lambda i: self.bidders[i].valuation_history[-1])
            self.winner = self.bidders[winner_id]
        self.auction_ended = True
        self.stop()

def create_bidder_dynamics_plot(model):
    """Create the bidder dynamics plot and return as base64 string"""
    plt.figure(figsize=(12, 8))
    colors = plt.cm.tab20(np.linspace(0, 1, len(model.bidders)))
    
    # Group bidders by type for legend
    type_colors = {}
    
    for i, bidder in enumerate(model.bidders):
        values = bidder.valuation_history
        rounds = bidder.dropout_round or len(values)
        
        # Get color for bidder type
        if bidder.bidder_type not in type_colors:
            type_colors[bidder.bidder_type] = colors[len(type_colors)]
        
        color = type_colors[bidder.bidder_type]
        alpha = 0.7 if bidder.bidder_type == 'strategic' else 0.5
        
        plt.plot(range(rounds), values[:rounds], color=color, alpha=alpha, linewidth=1)
        
        if bidder.dropout_round:
            plt.plot(bidder.dropout_round - 1, values[bidder.dropout_round - 1], 'x', 
                    color=color, markersize=8)
        else:
            plt.plot(len(values) - 1, values[-1], 'o', color=color, markersize=10)

    plt.plot(range(len(model.price_history)), model.price_history, '--', 
             color='black', linewidth=2, label='Auction Price')
    plt.axhline(model.p.common_value, linestyle='--', color='red', 
                linewidth=2, label='True Common Value')
    
    # Add legend for bidder types
    for bidder_type, color in type_colors.items():
        plt.plot([], [], color=color, label=f'{bidder_type.capitalize()} Bidders')
    
    plt.title("Bidder Valuation Trajectories", fontsize=16)
    plt.xlabel("Round")
    plt.ylabel("Valuation")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Convert to base64
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    img_buffer.seek(0)
    plot_data = base64.b64encode(img_buffer.read()).decode()
    plt.close()
    
    return plot_data

def create_summary_plot(model):
    """Create summary statistics plot"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Plot 1: Price history
    ax1.plot(model.price_history, linewidth=2, color='blue')
    ax1.axhline(model.p.common_value, linestyle='--', color='red', label='True Value')
    ax1.set_title('Price Evolution')
    ax1.set_xlabel('Round')
    ax1.set_ylabel('Price')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Active bidders over time
    ax2.plot(model.active_bidders_history, linewidth=2, color='green')
    ax2.set_title('Active Bidders Over Time')
    ax2.set_xlabel('Round')
    ax2.set_ylabel('Number of Active Bidders')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Final valuations by bidder type
    bidder_types = {}
    for bidder in model.bidders:
        if bidder.bidder_type not in bidder_types:
            bidder_types[bidder.bidder_type] = []
        bidder_types[bidder.bidder_type].append(bidder.valuation_history[-1])
    
    types = list(bidder_types.keys())
    avg_valuations = [np.mean(bidder_types[t]) for t in types]
    
    bars = ax3.bar(types, avg_valuations, alpha=0.7)
    ax3.axhline(model.p.common_value, linestyle='--', color='red', label='True Value')
    ax3.set_title('Average Final Valuation by Bidder Type')
    ax3.set_ylabel('Average Valuation')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Dropout distribution
    dropout_rounds = [b.dropout_round for b in model.bidders if b.dropout_round is not None]
    if dropout_rounds:
        ax4.hist(dropout_rounds, bins=max(1, len(dropout_rounds)//3), alpha=0.7, color='orange')
        ax4.set_title('Distribution of Dropout Rounds')
        ax4.set_xlabel('Round')
        ax4.set_ylabel('Number of Bidders')
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Convert to base64
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    img_buffer.seek(0)
    plot_data = base64.b64encode(img_buffer.read()).decode()
    plt.close()
    
    return plot_data

def run_simulation(params):
    """Run the auction simulation with given parameters"""
    global current_model, simulation_running
    
    simulation_running = True
    
    try:
        model = MixedEnglishAuction(params)
        current_model = model
        model.run()
        return model
    except Exception as e:
        print(f"Simulation error: {e}")
        return None
    finally:
        simulation_running = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start_simulation', methods=['POST'])
def start_simulation():
    global simulation_thread, current_model
    
    if simulation_running:
        return jsonify({'error': 'Simulation already running'}), 400
    
    data = request.json
    
    # Parse bidder configuration
    bidder_config = {}
    for bidder_type in ['strategic', 'naive', 'overconfident']:
        count = data.get(f'{bidder_type}_count', 0)
        a_value = data.get(f'{bidder_type}_a', 1/3 if bidder_type == 'strategic' else 1.0)
        if count > 0:
            bidder_config[bidder_type] = {'count': count, 'a_value': a_value}
    
    # Set n_bidders
    n_bidders = sum(config['count'] for config in bidder_config.values())
    
    # Create parameters
    params = {
        'common_value': data.get('common_value', 1000),
        'signal_std': data.get('signal_std', 150),
        'start_price': data.get('start_price', 500),
        'price_increment': data.get('price_increment', 20),
        'steps': data.get('max_steps', 1000),
        'bidder_config': bidder_config,
        'n_bidders': n_bidders
    }
    
    # Start simulation in a separate thread
    simulation_thread = threading.Thread(target=lambda: run_simulation(params))
    simulation_thread.start()
    
    return jsonify({'status': 'started'})

@app.route('/api/simulation_status')
def simulation_status():
    global current_model, simulation_running, simulation_thread
    
    if not current_model:
        return jsonify({'status': 'not_started'})
    
    if simulation_running or (simulation_thread and simulation_thread.is_alive()):
        return jsonify({
            'status': 'running',
            'current_round': current_model.round_number,
            'current_price': current_model.current_price,
            'active_bidders': len(current_model.remaining_ids)
        })
    else:
        return jsonify({
            'status': 'completed',
            'final_price': current_model.final_price,
            'winner_type': current_model.winner.bidder_type if current_model.winner else None,
            'total_rounds': current_model.round_number
        })

@app.route('/api/get_plots')
def get_plots():
    global current_model
    
    if not current_model or not current_model.auction_ended:
        return jsonify({'error': 'No completed simulation available'}), 400
    
    try:
        dynamics_plot = create_bidder_dynamics_plot(current_model)
        summary_plot = create_summary_plot(current_model)
        
        return jsonify({
            'dynamics_plot': dynamics_plot,
            'summary_plot': summary_plot
        })
    except Exception as e:
        return jsonify({'error': f'Error generating plots: {str(e)}'}), 500

@app.route('/api/reset')
def reset_simulation():
    global current_model, simulation_running
    
    current_model = None
    simulation_running = False
    
    return jsonify({'status': 'reset'})

@app.route('/api/export_data')
def export_data():
    global current_model
    
    if not current_model or not current_model.auction_ended:
        return jsonify({'error': 'No completed simulation available'}), 400
    
    # Prepare data for export
    data = {
        'parameters': {
            'common_value': current_model.p.common_value,
            'signal_std': current_model.p.signal_std,
            'start_price': current_model.p.start_price,
            'price_increment': current_model.p.price_increment,
        },
        'results': {
            'final_price': current_model.final_price,
            'winner_type': current_model.winner.bidder_type if current_model.winner else None,
            'total_rounds': current_model.round_number,
            'price_history': current_model.price_history,
            'active_bidders_history': current_model.active_bidders_history
        },
        'bidders': []
    }
    
    for i, bidder in enumerate(current_model.bidders):
        data['bidders'].append({
            'id': i,
            'type': bidder.bidder_type,
            'a_value': bidder.a_value,
            'initial_signal': bidder.initial_signal,
            'final_valuation': bidder.valuation_history[-1],
            'dropout_round': bidder.dropout_round,
            'valuation_history': bidder.valuation_history
        })
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)