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
% % auction = auction.runSim();
finalVal = zeros(1, 100);
for k = 1:5
    for i = 1:100
        alpha = i*0.01;
    
        auction = AuctionClass;
        auction = auction.setID(1);
        auction = auction.setVars(commonVal, rStndDv, startPrice, priceIncrement, alpha);
        auction = auction.setBidders(bidderTypes);
        auction = auction.runSim();
        finalVal(k, i) = auction.fprice;
    end
end

% Plot valuations
%auction = auction.displayPlots();

figure;
histogram(finalVal);

figure;

% avgVal = zeros(1, 100);
% for i = 1:1000
%     avgVal(i) = mean(finalVal(:, i));
% end
% 
% a = 1:100;
% a = a*0.001;
plot(a, finalVal);
