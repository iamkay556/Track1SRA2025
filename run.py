import agentpy as ap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from model import EnglishAuctionModel

parameters = {
    'n_bidders': 5,
    'common_value': 1000, # goal to hit
    'signal_std': 50,
    'start_price': 500,
    'price_increment': 20,
    'steps': 20,
}

model = EnglishAuctionModel(parameters)
results = model.run()

valuation_matrix = model.report['valuation_matrix']
n_bidders, n_rounds = valuation_matrix.shape

plt.figure(figsize=(10, 6))
for i in range(n_bidders):
    plt.plot(valuation_matrix[i], label=f'Bidder {i}')
plt.xlabel('Round')
plt.ylabel('Valuation Estimate')
plt.title('Valuation Updates (Rational Bidders)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

df = pd.DataFrame(valuation_matrix.T, columns=[f'Bidder_{i}' for i in range(n_bidders)])
df.to_csv('bidder_valuation_history.csv', index_label='Round')
print("Valuation data saved to bidder_valuation_history.csv")


