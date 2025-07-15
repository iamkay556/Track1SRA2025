% Matlab English Auction Simulation
clear; clc; close all;

% Values to pass into auction object
commonVal = 1000;
rStndDv = 150;
startPrice = 0;
priceIncrement = 50;
alpha = 1/3;

% Bidders to pass into auction object
nRational = 10;
bidderTypes = [nRational];

% New auction object
auction = AuctionClass;
auction = auction.setID(1);
auction = auction.setVars(commonVal, rStndDv, startPrice, priceIncrement, alpha);
auction = auction.setBidders(bidderTypes);

% Run!
auction = auction.runSim();

% Plot valuations
auction = auction.displayPlots();


% bidder valuation update func
    % change inp in auction class funcs
    % change inp in bidder parent class func
    % actually write in rational bidder

% to do: 
% fix double winner thing
% credits & readme