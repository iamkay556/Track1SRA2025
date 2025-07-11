import agentpy as ap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from model import EnglishAuctionModel

# Parameters for the auction
parameters = {
    'n_bidders': 5,
    'common_value': 1000,  # True value of the item
    'signal_std': 150,     # More noise for diverse initial signals
    'start_price': 600,    # Start closer to true value
    'price_increment': 20, # Smaller increments for gradual learning
    'steps': 25,           # Sufficient rounds for convergence
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

# Plot 1: Valuation evolution
for i in range(n_bidders):
    ax1.plot(valuation_matrix[i], label=f'Bidder {i}', marker='o', markersize=3)

ax1.axhline(y=parameters['common_value'], color='red', linestyle='--', 
           label=f'True Value (${parameters["common_value"]})', linewidth=2)
ax1.set_xlabel('Round')
ax1.set_ylabel('Valuation Estimate ($)')
ax1.set_title('Valuation Updates Over Time')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Convergence analysis
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