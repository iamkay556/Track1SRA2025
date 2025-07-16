% Matlab English Auction Simulation
clear; clc; close all;

% Values to pass into auction object
commonVal = 1000;
rStndDv = 150;
startPrice = 500;
priceIncrement = 20;

% Bidders to pass into auction object
nStrat1 = 0;
nStrat2 = 20;
bidderTypes = [nStrat1, nStrat2];

% Running values
k = 0.001;   % alpha interval
l = 1000;      % num runs to average

% Run!
finalVal = zeros(l, 1/k);
for i = 1:l
    for j = 1:1/k
        disp(['Run: ' num2str( j + (i-1)/k ) ' / ' num2str( l / k )]);
        alpha1 = j * k;
        alpha2 = j * k;
    
        auction = AuctionClass;
        auction = auction.setID(1);
        auction = auction.setVars(commonVal, rStndDv, startPrice, priceIncrement, alpha1, alpha2);
        auction = auction.setBidders(bidderTypes);
        auction = auction.runSim();
        finalVal(i, j) = auction.fprice;
    end
end

% ----- Calculating CI -----

% Dimensions
[l, numCols] = size(finalVal);  % numCols = 1/k

% X-axis (scaled by k)
a = (1:numCols) * k;

% Precomputed mean
avgVal = mean(finalVal, 1);  % 1 x numCols

% Compute 95% confidence interval (CI)
std_vals = std(finalVal, 0, 1);      % Standard deviation across rows
sem = std_vals / sqrt(l);            % Standard error
t_score = tinv(0.975, l - 1);        % 95% CI for n = l samples
ci95 = t_score * sem;                % Margin of error

upperBound = avgVal + ci95; 
lowerBound = avgVal - ci95;

% smoothWin = 5;  % adjust window size as needed
% upperBound = movmean(avgVal + ci95, smoothWin);
% lowerBound = movmean(avgVal - ci95, smoothWin);

% ----- Plotting -----

% Plot Selling Price Histogram
% figure; hold on;
% histogram(finalVal);

% Plot Confidence Interval and Mean Value
figure; hold on;

% Shaded smoothed CI region
fill([a, fliplr(a)], ...
     [upperBound, fliplr(lowerBound)], ...
     [0.63 0.63 0.96], 'EdgeColor', 'none', 'FaceAlpha', 0.8);

% Mean line
plot(a, avgVal, 'LineWidth',2);

xlabel('Alpha');
ylabel('Final Selling Price');
title('Final Selling Price vs. Alpha');
legend('95% Confidence Interval', 'Mean');