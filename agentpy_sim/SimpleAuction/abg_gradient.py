import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import agentpy as ap
import pandas as pd

class NewBidder(ap.Agent):
    def setup(self):
        self.signal = np.random.normal(self.model.p.common_value, self.model.p.signal_std)
        self.valuation_history = [self.signal]
        self.active = True

    def update_valuation(self, a, b, c, p_t, dropout_prices):
        if not self.active:
            self.valuation_history.append(self.valuation_history[-1])
            return

        v_prev = self.valuation_history[-1]
        v0 = self.valuation_history[0]
        k = len(dropout_prices)
        dropout_term = sum(dropout_prices) / k if k > 0 else 0
        new_val = a * v_prev - b * dropout_term + c * v0
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
            bidder.update_valuation(self.p.a, self.p.b, self.p.c, self.price, self.dropout_prices)

        if len(self.remaining_ids) <= 1:
            self.stop()

# === Grid Search ===

step = 0.01
results = []

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
            final_price = model.price
            results.append((a, b, c, final_price))

# === Plot Results ===

df = pd.DataFrame(results, columns=["a", "b", "c", "final_price"])

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
scatter = ax.scatter(df["a"], df["b"], df["c"], c=df["final_price"], cmap='Blues', s=50)

ax.set_xlabel("a")
ax.set_ylabel("b")
ax.set_zlabel("c")
ax.set_title("Final Auction Price by (a, b, c) Combination")
fig.colorbar(scatter, ax=ax, label="Final Price (Darker = Higher)")
plt.tight_layout()
plt.show()