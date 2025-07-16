% Matlab English Auction Simulation
clear; clc; close all;

% Values to pass into auction object
commonVal = 1000;
rStndDv = 150;
startPrice = 500;
priceIncrement = 20;
alpha = 1/3;

% Bidders to pass into auction object
nAverage = 20;
nABG0 = 0;
nABG03 = 0;
nABG05 = 0;
nABG07 = 0;
nABG1 = 0;
bidderTypes = [nAverage, nABG0, nABG03, nABG05, nABG07, nABG1];

% New auction object
auction = AuctionClass;
auction = auction.setID(1);
auction = auction.setVars(commonVal, rStndDv, startPrice, priceIncrement, alpha);
auction = auction.setBidders(bidderTypes);

% Run!
auction = auction.runSim();

% Plot valuations
auction = auction.displayPlots();