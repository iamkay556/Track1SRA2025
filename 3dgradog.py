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

        new_val = a * v_prev - b * dropout_term + c * p_t * survival_weight
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

    def step(self):
        self.price += self.p.increment
        self.round_number += 1

        for i in self.remaining_ids[:]:
            bidder = self.bidders[i]
            if bidder.should_dropout(self.price):
                bidder.active = False
                self.remaining_ids.remove(i)
                self.dropout_prices.append(self.price)

        for bidder in self.bidders:
            bidder.update_valuation(
                self.p.a, self.p.b, self.p.c,
                self.price,
                self.dropout_prices,
                len(self.remaining_ids),
                self.p.n_bidders
            )

        if len(self.remaining_ids) <= 1:
            self.stop()

# Run parameter grid
step = 0.01
results = []
trajectories = []

for a in np.arange(0, 1 + step, step):
    for b in np.arange(0, 1 - a + step, step):
        c = 1 - a - b
        if 0 <= c <= 1:
            params = {
                'common_value': 100,
                'signal_std': 15,
                'n_bidders': 10,
                'start_price': 20,
                'increment': 5,
                'a': a,
                'b': b,
                'c': c
            }
            model = SimpleAuction(params)
            model.run()
            print(f"Run with a={a:.2f}, b={b:.2f}, c={c:.2f} - Final Price: ${model.price:.2f}")

            results.append((a, b, c, model.price))
            matrix = np.array([bid.valuation_history for bid in model.bidders])
            trajectories.append((a, b, c, matrix))

# Plot 3D results
df = pd.DataFrame(results, columns=["a", "b", "c", "final_price"])
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
p = ax.scatter(df["a"], df["b"], df["c"], c=df["final_price"], cmap='Blues', s=50)
ax.set_xlabel("a (persistence)")
ax.set_ylabel("b (dropout adj.)")
ax.set_zlabel("c (price signal)")
ax.set_title("Final Price by (a, b, c) Settings")
fig.colorbar(p, ax=ax, label="Final Price")
plt.tight_layout()
plt.show()

# Plot sample bidder trajectories
_, _, _, example_matrix = trajectories[len(trajectories)//2]
plt.figure(figsize=(12, 6))
for i in range(example_matrix.shape[0]):
    plt.plot(example_matrix[i], label=f'Bidder {i+1}')
plt.axhline(100, color='red', linestyle='--', label='True Value')
plt.title("Sample Bidder Valuation Trajectories")
plt.xlabel("Round")
plt.ylabel("Valuation")
plt.grid(True)
plt.legend(ncol=2)
plt.tight_layout()
plt.show()
