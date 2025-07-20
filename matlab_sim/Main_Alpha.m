% Runs multiple auction simulations. Provides selling price histogram and valuation plots.
clear; clc; close all;

% Values to pass into auction object
commonVal = 1000;
rStndDv = 150;
startPrice = 500;
priceIncrement = 20;

% Bidders to pass into auction object
nAverage = 0;
nABG0 = 0;
nABG03 = 0;
nABG05 = 0;
nABG07 = 20;
nABG1 = 0;
bidderTypes = [nAverage, nABG0, nABG03, nABG05, nABG07, nABG1];

% Set runs
j = 100;

% Data pre-allocation
auctions = {1, j};
fprices = {[], [], [], [], []};
winTypeCount = zeros(1, 5);
allFinalVals = {[], [], [], [], []};
winSig = {[], [], [], [], []};
dError = {[], [], [], [], []};
ftimes = zeros(1, j);

for i = 1:j    
    disp(['Simulation ', num2str(i), ' / ', num2str(j), ' -----------------------'])

    % New auction object
    auction = AuctionClass;
    auction = auction.setID(i);
    auction = auction.setVars(commonVal, rStndDv, startPrice, priceIncrement);
    auction = auction.setBidders(bidderTypes);

    % Run!
    auction = auction.runSim();
    
    % Update data
    auctions{1, i} = auction;
    
    winType = auction.winID(1, 2) - 1;
    fprices{1, winType}(1, end + 1) = auction.fprice;

    winTypeCount(1, winType) = winTypeCount(1, winType) + 1;

    [m, n] = size(auction.bidders);
    commonVal = auction.commonVal;
    for k = 1:m
        for l = 1:n
            b = auction.bidders{k, l};
            if (~isempty(b))
                bType = b.id(1, 2) - 1;

                allFinalVals{1, bType}(end + 1) = b.vals(1, end);

                if (b.id == auction.winID)
                    winSig{1, bType}(end + 1) = b.signal;
                end

                dError{1, bType}(end + 1) = abs(b.signal - commonVal) - abs(b.vals(1, end) - commonVal);
            end
        end
    end
    
    ftimes(1, j) = (auction.fprice - auction.startPrice) / auction.priceIncrement;

end

disp("All Simulations Finished. --------------------")

% Edit Data
disp("Organizing Data...")

% Average final valuations by type
avgAllFinalVals = zeros(1, 5);
for i = 1:5
    avgAllFinalVals(1, i) = mean(allFinalVals{1, i});
end

% Average final price by winner type
avgfprices = zeros(1, 5);
for i = 1:5
    avgfprices(1, i) = mean(fprices{1, i});
end

% Average difference to common value
avgdCV = avgfprices - 1000;

% Average of all final prices
avgAllfprices = 0;
for i = 1:5
    avgAllfprices = avgAllfprices + sum(fprices{1, i});
end
avgAllfprices = avgAllfprices / j;

% Average of winner signals by type
avgWinSig = zeros(1, 5);
for i = 1:5
    avgWinSig(1, i) = mean(winSig{1, i});
end

% Percent of sims won by type
winTypePercent = winTypeCount * 100 / j;

% Average error by type (all bidders)
avgdError = zeros(1, 5);
for i = 1:5
    avgdError(1, i) = mean(dError{1, i});
end

% Average auction length
avgTime = mean(ftimes(ftimes ~= 0));

% Figures
disp("Displaying Figures...")

disp("Done.")