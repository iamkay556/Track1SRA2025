% Matlab English Auction Simulation
clear; clc; close all;

% Values to pass into auction object
commonVal = 1000;
rStndDv = 150;
startPrice = 0;
priceIncrement = 1;

% Bidders to pass into auction object
nRational = 10;
bidderTypes = [nRational];

% New auction object
% % auction = AuctionClass;
% % auction = auction.setID(1);
% % auction = auction.setVars(commonVal, rStndDv, startPrice, priceIncrement);
% % auction = auction.setBidders(bidderTypes);

% Run!
% % auction = auction.runSim();
finalVal = zeros(1, 10000);
for i = 1:length(finalVal)
    auction = AuctionClass;
    auction = auction.setID(1);
    auction = auction.setVars(commonVal, rStndDv, startPrice, priceIncrement);
    auction = auction.setBidders(bidderTypes);
    auction = auction.runSim();
    finalVal(i) = auction.fprice;
end

% Plot valuations
% auction = auction.displayPlots();
histogram(finalVal)

% bidder valuation update func
    % change inp in auction class funcs
    % change inp in bidder parent class func
    % actually write in rational bidder

% to do: 
% fix double winner thing
% credits & readme