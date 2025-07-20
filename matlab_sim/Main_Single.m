% Matlab English Auction Simulation
clear; clc; close all;

% Values to pass into auction object
commonVal = 1000;
rStndDv = 150;
startPrice = 500;
priceIncrement = 20;

% Bidders to pass into auction object
nAverage = 0;
nABG0 = 5;
nABG03 = 0;
nABG05 = 10;
nABG07 = 0;
nABG1 = 5;
bidderTypes = [nAverage, nABG0, nABG03, nABG05, nABG07, nABG1];

% New auction object
auction = AuctionClass;
auction = auction.setID(1);
auction = auction.setVars(commonVal, rStndDv, startPrice, priceIncrement);
auction = auction.setBidders(bidderTypes);

% Run!
auction = auction.runSim();

% Plot valuations vs time
auction = auction.displayPlots("arial");