% Matlab English Auction Simulation
clear; clc; close all;

% Values to pass into auction object
commonVal = 1000;
rStndDv = 150;
startPrice = 500;
priceIncrement = 1;
alpha1 = 1/2;
alpha2 = 1/3;

% Bidders to pass into auction object
nStrat1 = 10;
nStrat2 = 10;
bidderTypes = [nStrat1, nStrat2];

% New auction object
auction = AuctionClass;
auction = auction.setID(1);
auction = auction.setVars(commonVal, rStndDv, startPrice, priceIncrement, alpha1, alpha2);
auction = auction.setBidders(bidderTypes);

% Run!
auction = auction.runSim();

% Plot valuations
auction = auction.displayPlots();