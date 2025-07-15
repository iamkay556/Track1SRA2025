% Matlab English Auction Simulation
clear; clc; close all;

% Values to pass into auction object
commonVal = 1000;
rStndDv = 150;
startPrice = 500;
priceIncrement = 20;
alpha = 1/3;

% Bidders to pass into auction object
nAverage = 0;
nABG = 20;
bidderTypes = [nAverage, nABG];

% New auction object
auction = AuctionClass;
auction = auction.setID(1);
auction = auction.setVars(commonVal, rStndDv, startPrice, priceIncrement, alpha);
auction = auction.setBidders(bidderTypes);

% Run!
auction = auction.runSim();

% Plot valuations
auction = auction.displayPlots();