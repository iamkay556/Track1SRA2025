from model import AuctionModel
import numpy as np

n_bidders = 5
valuations = np.random.randint(10, 50, size=n_bidders).tolist()
rational_flags = [True, False, True, False, True]

parameters = {
    'n_bidders': n_bidders,
    'valuations': valuations,
    'rational_flags': rational_flags,
    'steps': 100
}

model = AuctionModel(parameters)
results = model.run()

print("Winner's Valuation:", results.report['winner_valuation'])
print("Final Price:", results.report['final_price'])