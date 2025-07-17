% Matlab English Auction Simulation
clear; clc; close all;

% Values to pass into auction object
commonVal = 1000;
rStndDv = 150;
startPrice = 500;
priceIncrement = 20;

% Bidders to pass into auction object
nAverage = 0;
nABG0 = 20;
nABG03 = 0;
nABG05 = 0;
nABG07 = 0;
nABG1 = 0;
bidderTypes = [nAverage, nABG0, nABG03, nABG05, nABG07, nABG1];

% Set runs
j = 1000;

% Data pre-allocation
auctions = {1, j};
spmtx = [1, j];

for i = 1:j
    alpha = i/j;
    
    disp(['Simulation ', num2str(i), ' / ', num2str(j), ' -----------------------'])

    % New auction object
    auction = AuctionClass;
    auction = auction.setID(i);
    auction = auction.setVars(commonVal, rStndDv, startPrice, priceIncrement);
    auction = auction.setBidders(bidderTypes);

    % Run!
    auction = auction.runSim();
    
    % Update data
    auctions{1, i} = auction;
    spmtx(1, i) = auction.fprice;
end

disp("All Simulations Finished. --------------------")
disp("Displaying Plots...")

% Display Histogram of average selling price
figure;
histogram(spmtx);
plot((1:j)/j, spmtx);

% Plot 10 valuations, evenly spaced (single runs)
for i = 1:j
    if (mod(i, j/10) == 0)
        auctions{1, i} = auctions{1, i}.displayPlots();
    end
end

disp("Done.")