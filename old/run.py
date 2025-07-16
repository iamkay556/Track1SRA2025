import agentpy as ap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from old.model import EnglishAuctionModel

# Parameters for the auction
parameters = {
    'n_bidders': 20,
    'common_value': 1000,
    'signal_std': 150,
    'start_price': 500,
    'price_increment': 20
}

print("Running English Auction Simulation")
print(f"True common value: ${parameters['common_value']}")
print(f"Number of bidders: {parameters['n_bidders']}")
print(f"Signal noise (std): ${parameters['signal_std']}")

# Run the simulation
model = EnglishAuctionModel(parameters)
results = model.run()

# Extract results
valuation_matrix = model.report['valuation_matrix']
n_bidders, n_rounds = valuation_matrix.shape

# Display initial signals
print("\nInitial private signals:")
for i in range(n_bidders):
    print(f"Bidder {i}: ${valuation_matrix[i, 0]:.2f}")

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Plot 1: Valuation evolution with dropout markers
for i in range(n_bidders):
    values = valuation_matrix[i]
    is_winner = i == model.report['winner_id']
    final_price = model.report['final_price']

    dropout_round = None
    for t in range(1, n_rounds - 1):
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
        ax1.plot(range(n_rounds), values, label=f'Bidder {i}',
                 marker='o', markersize=3)


ax1.axhline(y=parameters['common_value'], color='red', linestyle='--',
            label=f'True Value (${parameters["common_value"]})', linewidth=2)
ax1.set_xlabel('Round')
ax1.set_ylabel('Valuation Estimate ($)')
ax1.set_title('Valuation Updates Over Time')
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
print(f"Winner: Bidder {model.report['winner_id']}")
print(f"Final price: ${model.report['final_price']}")
print(f"Convergence error: ${model.report['convergence_error']:.2f}")

# Save detailed results
df = pd.DataFrame(valuation_matrix.T, columns=[f'Bidder_{i}' for i in range(n_bidders)])
df['Round'] = range(n_rounds)
df['True_Value'] = parameters['common_value']
df.to_csv('bidder_valuation_history.csv', index=False)
print("\nDetailed results saved to 'bidder_valuation_history.csv'")

# Additional analysis
print(f"\n=== CONVERGENCE ANALYSIS ===")
initial_error = np.mean(np.abs(valuation_matrix[:, 0] - parameters['common_value']))
final_error = np.mean(np.abs(valuation_matrix[:, -1] - parameters['common_value']))
print(f"Initial average error: ${initial_error:.2f}")
print(f"Final average error: ${final_error:.2f}")
print(f"Improvement: {((initial_error - final_error) / initial_error * 100):.1f}%")
    
# Show final valuations
print(f"\n=== FINAL VALUATIONS ===")
for i in range(n_bidders):
    final_val = valuation_matrix[i, -1]
    error = abs(final_val - parameters['common_value'])
    print(f"Bidder {i}: ${final_val:.2f} (error: ${error:.2f})")