import agentpy as ap
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class RationalBidder(ap.Agent):
    def setup(self):
        self.signal = np.random.normal(self.model.p.common_value, self.model.p.signal_std)
        self.initial_signal = self.signal
        self.valuation_history = [self.signal]
        self.active = True
        self.dropout_round = None

    def update_valuation(self, current_price, dropout_prices, remaining_bidders):
        if not self.active:
            self.valuation_history.append(self.valuation_history[-1])
            return

        v0 = self.initial_signal
        total = self.model.p.n_bidders
        dropouts = len(dropout_prices)
        a = self.model.p.a
        b = (1 - a) * (dropouts / total)
        c = (1 - a) * (remaining_bidders / total)
        dropout_term = np.mean(dropout_prices) if dropouts > 0 else 0
        new_val = a * v0 + b * dropout_term + c * current_price
        self.valuation_history.append(new_val)

    def should_dropout(self, price):
        return self.active and price > self.valuation_history[-1]


class EnglishAuction(ap.Model):
    def setup(self):
        self.bidders = ap.AgentList(self, self.p.n_bidders, RationalBidder)
        self.current_price = self.p.start_price
        self.dropout_prices = []
        self.remaining_ids = list(range(self.p.n_bidders))
        self.round_number = 0
        self.price_history = [self.current_price]
        self.active_bidders_history = [len(self.remaining_ids)]
        self.final_price = None
        self.winner = None

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

    def end_auction(self):
        self.final_price = self.current_price
        if len(self.remaining_ids) >= 1:
            winner_id = self.remaining_ids[0] if len(self.remaining_ids) == 1 else max(
                self.remaining_ids, key=lambda i: self.bidders[i].valuation_history[-1])
            self.winner = self.bidders[winner_id]
        self.stop()


def run_single_auction(**kwargs):
    default_params = {
        'common_value': 100,
        'signal_std': 15,
        'n_bidders': 20,
        'start_price': 20,
        'price_increment': 10,
        'steps': 1000,
        'a': 1/3
    }
    default_params.update(kwargs)
    model = EnglishAuction(default_params)
    model.run()
    return model


def plot_rational_bidder_dynamics(model):
    plt.figure(figsize=(12, 8))
    colors = plt.cm.tab20(np.linspace(0, 1, model.p.n_bidders))

    for i, bidder in enumerate(model.bidders):
        values = bidder.valuation_history
        rounds = bidder.dropout_round or len(values)
        plt.plot(range(rounds), values[:rounds], color=colors[i], alpha=0.7)
        if bidder.dropout_round:
            plt.plot(bidder.dropout_round - 1, values[bidder.dropout_round - 1], 'x', color=colors[i], markersize=8)
        else:
            plt.plot(len(values) - 1, values[-1], 'o', color=colors[i], markersize=10, label=f'Winner {i + 1}')

    plt.plot(range(len(model.price_history)), model.price_history, '--', color='black', label='Auction Price')
    plt.axhline(model.p.common_value, linestyle='--', color='red', label='True Common Value')
    plt.title("Bidder Valuation Trajectories")
    plt.xlabel("Round")
    plt.ylabel("Valuation")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def run_multiple_auctions_for_sweep(a_values, runs_per_a=5):
    """Runs multiple auctions per `a` value and returns list of all individual and average results."""
    all_points = []
    avg_points = []

    for a in a_values:
        final_prices = []
        for _ in range(runs_per_a):
            model = run_single_auction(
                common_value=1000,
                signal_std=150,
                n_bidders=20,
                start_price=600,
                price_increment=10,
                a=a
            )
            price = model.final_price if model.final_price is not None else np.nan
            final_prices.append(price)
            all_points.append((a, price))
        
        avg_price = np.nanmean(final_prices)
        avg_points.append((a, avg_price))

    return all_points, avg_points


def plot_sweep_results(all_points, avg_points):
    a_all, p_all = zip(*all_points)
    a_avg, p_avg = zip(*avg_points)

    plt.figure(figsize=(14, 8))
    plt.scatter(a_all, p_all, color='lightblue', s=10, alpha=0.6, label='Individual Runs')
    plt.plot(a_avg, p_avg, color='blue', linewidth=2, label='Average Final Price')
    plt.axhline(1000, color='red', linestyle='--', linewidth=2, label='True Common Value')
    plt.title("Final Price vs a (Multiple Auctions)", fontsize=16)
    plt.xlabel("a (Weight on Initial Signal)")
    plt.ylabel("Final Auction Price")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


# Run the full flow
if __name__ == "__main__":
    # Single auction preview
    model = run_single_auction()
    plot_rational_bidder_dynamics(model)

    # Sweep of a with multiple auctions per point
    a_values = np.arange(0.0, 1.01, 0.01)
    print("\nRunning sweep of a values with multiple auctions each...")
    all_results, avg_results = run_multiple_auctions_for_sweep(a_values, runs_per_a=5)
    plot_sweep_results(all_results, avg_results)
