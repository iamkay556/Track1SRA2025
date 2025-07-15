% Matlab English Auction Simulation
clear; clc; close all;

% Values to pass into auction object
commonVal = 1000;
rStndDv = 150;
startPrice = 500;
priceIncrement = 20;

% Bidders to pass into auction object
nRational = 20;
bidderTypes = [nRational];

% Record Selling Price
spmtx = [];

for i = 1:100
    % New auction object
    auction = AuctionClass;
    auction = auction.setID(1);
    auction = auction.setVars(commonVal, rStndDv, startPrice, priceIncrement);
    auction = auction.setBidders(bidderTypes);
    
    % Run!
    auction = auction.runSim();
    
    % Update spmtx
    spmtx(1, end + 1) = auction.fprice;
end

% Display Histogram of average selling price
disp(["Avg Selling Price: ", num2str(mean(spmtx))]);
figure;
histogram(spmtx);

% Plot valuations (single runs)
%auction = auction.displayPlots();


% to do: 
% Update valuation eq. (back to old)
% comment code better, start a readme
% fix double winner thing (random?)
% fix last dropout extra step by exiting loop when numBidders = 1
% optimise
% x on end of graph, add o on end for winner
% figure out how to run a bunch with diff const
% credits & readme