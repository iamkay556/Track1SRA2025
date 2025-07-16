import numpy as np
import matplotlib.pyplot as plt
import agentpy as ap
import pandas as pd

class NewBidder(ap.Agent):
    def setup(self):
        self.signal = np.random.normal(self.model.p.common_value, self.model.p.signal_std)
        self.valuation_history = [self.signal]
        self.active = True

    def update_valuation(self, a, b, c, p_t, dropout_prices, remaining_bidders, total_bidders):
        if not self.active:
            self.valuation_history.append(self.valuation_history[-1])
            return

        v_prev = self.valuation_history[-1]
        v0 = self.valuation_history[0]
        k = len(dropout_prices)

        dropout_term = sum(v_prev - d for d in dropout_prices) / k if k > 0 else 0
        survival_weight = 1 + 0.1 * np.sqrt(remaining_bidders / total_bidders) if total_bidders > 0 else 1.0

        new_val = a * v0 - b * dropout_term + c * p_t
        self.valuation_history.append(new_val)

    def should_dropout(self, price):
        return self.active and price > self.valuation_history[-1]

class SimpleAuction(ap.Model):
    def setup(self):
        self.bidders = ap.AgentList(self, self.p.n_bidders, NewBidder)
        self.price = self.p.start_price
        self.dropout_prices = []
        self.remaining_ids = list(range(self.p.n_bidders))
        self.round_number = 0
        self.b_history = []
        self.c_history = []

    def step(self):
        self.price += self.p.increment
        self.round_number += 1

        # Stop if step limit exceeded
        if self.round_number > 2000:
            print("Max step limit reached. Ending auction.")
            if self.remaining_ids:
                self.price = max(self.bidders[i].valuation_history[-1] for i in self.remaining_ids)
            self.stop()
            return

        for i in self.remaining_ids[:]:
            bidder = self.bidders[i]
            if bidder.should_dropout(self.price):
                bidder.active = False
                self.remaining_ids.remove(i)
                self.dropout_prices.append(self.price)

        total = self.p.n_bidders
        dropouts = total - len(self.remaining_ids)
        a = self.p.a
        b = (1 - a) * (dropouts / total) if total > 0 else 0
        c = 1 - a - b

        # Log b and c values
        self.b_history.append(b)
        self.c_history.append(c)

        for bidder in self.bidders:
            bidder.update_valuation(
                a, b, c,
                self.price,
                self.dropout_prices,
                len(self.remaining_ids),
                total
            )

        if len(self.remaining_ids) <= 1:
            self.stop()


# Run parameter grid
step = 0.01
results = []
trajectories = []

for a in np.arange(0, 1 + step, step):
    params = {
        'common_value': 1000,
        'signal_std': 150,
        'n_bidders': 20,
        'start_price': 500,
        'increment': 20,
        'a': a,
    }
    model = SimpleAuction(params)
    model.run()

    # Compute average b and c used during simulation
    avg_b = np.mean(model.b_history)
    avg_c = np.mean(model.c_history)

    print(f"Run with a={a:.2f}, avg b={avg_b:.2f}, avg c={avg_c:.2f} - Final Price: ${model.price:.2f}")

    results.append((a, avg_b, avg_c, model.price))
    matrix = np.array([bid.valuation_history for bid in model.bidders])
    trajectories.append((a, avg_b, avg_c, matrix))

# === Plot 3D results ===
# === Plot 3D results with conditional coloring ===
df = pd.DataFrame(results, columns=["a", "b", "c", "final_price"])

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Split data into two groups
df_blue = df[df["final_price"] <= 1500]
df_red = df[df["final_price"] > 1500]

# Normalize blue prices between 1–1500 for color scaling
norm = plt.Normalize(vmin=500, vmax=1500)
blue_colors = plt.cm.Blues(norm(df_blue["final_price"]))

# Blue points (scaled)
ax.scatter(df_blue["a"], df_blue["b"], df_blue["c"],
           c=blue_colors, s=50, label="Price ≤ 1500")

# Red points (high prices)
ax.scatter(df_red["a"], df_red["b"], df_red["c"],
           c='red', s=50, label="Price > 1500")

# Axis labeling
ax.set_xlabel("a (persistence)")
ax.set_ylabel("b (dropout adj.)")
ax.set_zlabel("c (price signal)")
ax.set_title("Final Price by (a, b, c) Settings")

# Add color bar for blue prices
mappable = plt.cm.ScalarMappable(cmap='Blues', norm=norm)
mappable.set_array([])
fig.colorbar(mappable, ax=ax, label="Final Price (≤1500)")

ax.legend()
plt.tight_layout()
plt.show()


# === Plot sample bidder trajectories with dropout markers ===
_, _, _, example_matrix = trajectories[len(trajectories) // 2]
n_bidders, n_rounds = example_matrix.shape

plt.figure(figsize=(12, 6))

for i in range(n_bidders):
    values = example_matrix[i]

    # Detect dropout: if valuation is flat for 2+ rounds, we assume dropout occurred
    dropout_round = n_rounds
    for t in range(2, n_rounds):
        if np.isclose(values[t], values[t - 1]) and np.isclose(values[t - 1], values[t - 2]):
            dropout_round = t
            break

    # Plot up to dropout
    plt.plot(range(dropout_round), values[:dropout_round], label=f'Bidder {i+1}', alpha=0.8)

    # Mark dropout with an "X"
    if dropout_round < n_rounds:
        plt.plot(dropout_round - 1, values[dropout_round - 1], 'x', color='black', markersize=8)

# Common value reference line
plt.axhline(100, color='red', linestyle='--', label='True Value')
plt.title("Sample Bidder Valuation Trajectories (Dropouts Marked)")
plt.xlabel("Round")
plt.ylabel("Valuation")
plt.grid(True, alpha=0.3)
plt.legend(ncol=2)
plt.tight_layout()
plt.show()

