import agentpy as ap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from model import EnglishAuctionModel

parameters = {
    'n_bidders': 10,            # You can increase this to test large-N behavior
    'common_value': 1000,
    'signal_std': 0,            # Not used but required by param structure
    'start_price': 800,
    'price_increment': 25,
    'steps': 15,
}

model = EnglishAuctionModel(parameters)
results = model.run()

valuation_matrix = model.report['valuation_matrix']
n_bidders, n_rounds = valuation_matrix.shape

# Plot valuation curves
plt.figure(figsize=(10, 6))
for i in range(n_bidders):
    plt.plot(valuation_matrix[i], label=f'Bidder {i}')
plt.xlabel('Round')
plt.ylabel('Valuation Estimate')
plt.title('Valuation Convergence to Common Value')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Export to CSV
df = pd.DataFrame(valuation_matrix.T, columns=[f'Bidder_{i}' for i in range(n_bidders)])
df.to_csv('bidder_valuation_history.csv', index_label='Round')
print("Valuation data saved to bidder_valuation_history.csv")