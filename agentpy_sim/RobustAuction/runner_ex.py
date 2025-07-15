import agentpy as ap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from AuctionClass import AuctionClass

# Parameters for the auction
parameters = {
    'total_bidders': 20,
    'common_value': 1000,
    'standard_deviation': 150,
    'start_price': 500,
    'price_increment': 20
}

print("Running English Auction Simulation")
print(f"True common value: ${parameters['common_value']}")
print(f"Number of bidders: {parameters['total_bidders']}")
print(f"Signal noise standard deviation: ${parameters['standard_deviation']}")

# Run the simulation
model = AuctionClass(parameters)
results = model.run()

# Extract results
valuation_matrix = model.report['valuation_matrix']
total_bidders, auction_length = valuation_matrix.shape

# Display initial signals
print("\nInitial private signals:")
for i in range(total_bidders):
    print(f"Bidder {i}: ${valuation_matrix[i, 0]:.2f}")

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Plot 1: Valuation evolution with dropout markers
for i in range(total_bidders):
    values = valuation_matrix[i]
    is_winner = i == model.report['winner']
    final_price = model.report['final_price']

    dropout_round = None
    for t in range(1, auction_length - 1):
        if np.isclose(values[t], values[t - 1]) and np.isclose(values[t + 1], values[t]):
            if not is_winner and values[t] < final_price:
                dropout_round = t
                break

    # Plot line up to dropout or full length
    if dropout_round is not None:
        ax1.plot(range(dropout_round), values[:dropout_round],
                 label=f'Bidder {i}', marker='o', markersize=3)
        ax1.plot(dropout_round, values[dropout_round],
                 marker='x', markersize=8, color='red',
                 label='Dropout' if i == 0 else None)
    else:
        ax1.plot(range(auction_length), values, label=f'Bidder {i}',
                 marker='o', markersize=3)


ax1.axhline(y=parameters['common_value'], color='red', linestyle='--',
            label=f'True Value (${parameters["common_value"]})', linewidth=2)
ax1.set_xlabel('Round')
ax1.set_ylabel('Valuation Estimate ($)')
ax1.set_title('Valuation Updates Over total_bidders')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Convergence analysis (final valuation distribution)
final_valuations = valuation_matrix[:, -1]
ax2.hist(final_valuations, bins=10, alpha=0.7, edgecolor='black')
ax2.axvline(x=parameters['common_value'], color='red', linestyle='--',
            label=f'True Value (${parameters["common_value"]})', linewidth=2)
ax2.axvline(x=np.mean(final_valuations), color='green', linestyle='-',
            label=f'Mean Final (${np.mean(final_valuations):.2f})', linewidth=2)
ax2.set_xlabel('Final Valuation ($)')
ax2.set_ylabel('Frequency')
ax2.set_title('Distribution of Final Valuations')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Analysis summary
print(f"\n=== AUCTION RESULTS ===")
print(f"Winner: Bidder {model.report['winner']}")
print(f"Final price: ${model.report['final_price']}")