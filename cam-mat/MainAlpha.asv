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

% Run!
k = 0.001;   % alpha interval
l = 20;      % num runs to average

finalVal = zeros(l, 1/k);
for i = 1:l
    for j = 1:1/k
        disp(['Run: ' num2str( j * i ) ' / ' num2str( l / k )]);
        alpha = j * k;
    
        auction = AuctionClass;
        auction = auction.setID(1);
        auction = auction.setVars(commonVal, rStndDv, startPrice, priceIncrement, alpha);
        auction = auction.setBidders(bidderTypes);
        auction = auction.runSim();
        finalVal(i, j) = auction.fprice;
    end
end

% Plot valuations
%auction = auction.displayPlots();

figure;
histogram(finalVal);

figure;
avgVal = zeros(1, 1/k);
for i = 1:1/k
    avgVal(i) = mean(finalVal(:, i));
end

a = 1:1/k;
a = a * k;
plot(a, avgVal);
