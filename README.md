# Track1SRA2025 Ascending Clock Auction Simulation
### Analyzing Bidding Strategies in Ascending Auctions Using An Agent-Based Modeling Approach (2025)
Sophia Cheng, Camryn Nguyen, Kshitij Singhal

## General
MATLAB and Python (Agentpy Library) simulations for an asceneding clock auction with different bidder types.


## Files
Listed in order as in GitHub.

### agentpy_sim (Folder)
Coded by Kshitij Singhal. Minorly edited by Sophia Cheng.

Auction simulation in Python using the Agentpy library.

#### Robust Auction (Subfolder)
Files for the auction, bidders, and runner are in separate files. Calculates and saves more information than the Simple_Auction folder code. Includes plots.

Contains AuctionClass.py, BidderClass.py, runner_ex.py.

#### AuctionClass.py
Contains AuctionClass class.

#### BidderClass.py
Contains BidderClass class.

#### runner_ex.py
Contains a sample runner code.

#### Simple Auction (Subfolder)
Holds a file that integrates all the class code into one .py file.

Contains abg_gradient.py.

#### abg_gradient.py
Calculates the selling price for different values of alpha, beta, and gamma onto a triangular gradient for a symmetrical bidder population.

Contains SimpleAuction, NewBidder classes.


### matlab_data (Folder)
Data collected by Camryn Nguyen.

Holds data from MATLAB simulations containing information on auctions with symmetrical bidder strategies for 1000 different alpha values with each value run multiple times.

Contains 1000x1000.mat, 100x1000.mat, 20x1000.mat.

#### 1000x1000.mat
Holds information over 1000 runs for each of the 1000 alpha values.

#### 100x1000.mat
Holds information over 100 runs for each of the 1000 alpha values.

#### 20x1000.mat
Holds information over 20 runs for each of the 1000 alpha values.


### matlab_sim (Folder)
Coded by Sophia Cheng, assisted by Camryn Nguyen.

Auction simulation using MATLAB.

#### 100xcombs.mat
Holds minor information over 100 runs for each of the bidder strategy compositions.

#### 100xcombs2.mat
Holds more information (than 100xcombs.mat) over 100 runs for each of the bidder strategy compositions. 

#### AuctionClass.m
Contains AuctionClass class.

#### BidderClass.m
Contains BidderClass superclass.

#### BidderClass_ABG.m
Contains BidderClass_ABG class.

#### BidderClass_ABG0.m
Contains BidderClass_ABG0 child class.

#### BidderClass_ABG03.m
Contains BidderClass_ABG03 child class.

#### BidderClass_ABG05.m
Contains BidderClass_ABG05 child class.

#### BidderClass_ABG07.m
Contains BidderClass_ABG07 child class.

#### BidderClass_ABG1.m
Contains BidderClass_ABG1 child class.

#### BidderClass_Average.m
Contains unused BidderClass_Average class.

Works more accurately the smaller the price increment is.

#### Main_Alpha.m
Runs multiple simulations, then provides a selling price histogram and valuation plots.

#### Main_Combs.m
Runs a number of simulations over every 5 strategy combination of 20 bidders. Automatically saves data once finished.

#### Main_Single.m
Runs a single simulation. Plots a valuation graph when finished.

#### Plot_Combs.m
For 100xcombs.mat. Graphs pentagonal scatterplot displaying bidder strategy composition and final selling price.

#### Plot_Combs2.m
For 100xcombs2.mat. Graphs pentagonal scatterplot displaying bidder strategy composition and final selling price. Also creates bar charts to compare winner types, winner's curse, and strategy effectiveness.
