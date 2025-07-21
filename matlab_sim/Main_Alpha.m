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
nABG07 = 0;
nABG1 = 20;

bidderTypes = [nAverage, nABG0, nABG03, nABG05, nABG07, nABG1];

% Set runs
j = 1000;

% Determine which bidder types are actually present
numBidderTypes = length(bidderTypes);
presentTypes = find(bidderTypes > 0);  % Get indices of non-zero bidder types

% Data pre-allocation - use dynamic sizing based on total number of types
auctions = {1, j};
fprices = cell(1, numBidderTypes);
winTypeCount = zeros(1, numBidderTypes);
allFinalVals = cell(1, numBidderTypes);
winSig = cell(1, numBidderTypes);
% NEW: Track highest losing signal by winner type
highestLosingSig = cell(1, numBidderTypes);
dError = cell(1, numBidderTypes);
ftimes = zeros(1, j);

% Initialize cell arrays
for i = 1:numBidderTypes
    fprices{i} = [];
    allFinalVals{i} = [];
    winSig{i} = [];
    highestLosingSig{i} = [];
    dError{i} = [];
end

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
    winType = auction.winID(1, 2);  % This is the actual bidder type (1-6)
    fprices{winType}(end + 1) = auction.fprice;
    winTypeCount(winType) = winTypeCount(winType) + 1;

    [m, n] = size(auction.bidders);
    commonVal = auction.commonVal;

    % NEW: Find highest signal among losing bidders
    losingSignals = [];
    
    for k = 1:m
        for l = 1:n
            b = auction.bidders{k, l};
            if (~isempty(b))
                bType = b.id(1, 2);  % Actual bidder type (1-6)
                allFinalVals{bType}(end + 1) = b.vals(1, end);
                
                if (b.id == auction.winID)
                    winSig{bType}(end + 1) = b.signal;
                else
                    % This is a losing bidder - collect their signal
                    losingSignals(end + 1) = b.signal;
                end
                
                dError{bType}(end + 1) = abs(b.signal - commonVal) - abs(b.vals(1, end) - commonVal);
            end
        end
    end
    
    % Store the highest losing signal for this auction, categorized by winner type
    if ~isempty(losingSignals)
        highestLosingSig{winType}(end + 1) = max(losingSignals);
    end

    ftimes(1, i) = (auction.fprice - auction.startPrice) / auction.priceIncrement;
end

disp("All Simulations Finished. --------------------")

% Edit Data
disp("Organizing Data...")

% Average final valuations by type (only for present types)
avgAllFinalVals = zeros(1, numBidderTypes);
for i = 1:numBidderTypes
    if ~isempty(allFinalVals{i})
        avgAllFinalVals(i) = mean(allFinalVals{i});
    end
end

% Average final price by winner type (only for present types)
avgfprices = zeros(1, numBidderTypes);
for i = 1:numBidderTypes
    if ~isempty(fprices{i})
        avgfprices(i) = mean(fprices{i});
    end
end

% Average difference to common value
avgdCV = avgfprices - 1000;

% Average of all final prices
avgAllfprices = 0;
totalWins = 0;
for i = 1:numBidderTypes
    if ~isempty(fprices{i})
        avgAllfprices = avgAllfprices + sum(fprices{i});
        totalWins = totalWins + length(fprices{i});
    end
end
if totalWins > 0
    avgAllfprices = avgAllfprices / totalWins;
end

% Average of winner signals by type
avgWinSig = zeros(1, numBidderTypes);
for i = 1:numBidderTypes
    if ~isempty(winSig{i})
        avgWinSig(i) = mean(winSig{i});
    end
end

% NEW: Average of highest losing signals by winner type
avgHighestLosingSig = zeros(1, numBidderTypes);
for i = 1:numBidderTypes
    if ~isempty(highestLosingSig{i})
        avgHighestLosingSig(i) = mean(highestLosingSig{i});
    end
end

% Percent of sims won by type
winTypePercent = winTypeCount * 100 / j;

% Average error by type (all bidders)
avgdError = zeros(1, numBidderTypes);
for i = 1:numBidderTypes
    if ~isempty(dError{i})
        avgdError(i) = mean(dError{i});
    end
end

% Average auction length
avgTime = mean(ftimes(ftimes ~= 0));

% Figures
disp("Displaying Figures...")

% ========== DISPLAY ALL RESULTS ==========
disp(" ");
disp("========================================");
disp("           AUCTION ANALYTICS           ");
disp("========================================");

% Bidder type names - dynamically map type numbers to names
typeNames = containers.Map('KeyType', 'int32', 'ValueType', 'char');
typeNames(1) = 'Average';
typeNames(2) = 'ABG α=0';
typeNames(3) = 'ABG α=0.3';
typeNames(4) = 'ABG α=0.5';
typeNames(5) = 'ABG α=0.7';
typeNames(6) = 'ABG α=1.0';

% Helper function to get type name
getTypeName = @(typeNum) typeNames(typeNum);

disp(" ");
disp("1. MEAN FINAL VALUATIONS BY BIDDER TYPE:");
for i = presentTypes
    if ~isempty(allFinalVals{i})
        fprintf('   %s: %.2f\n', getTypeName(i), avgAllFinalVals(i));
    end
end

disp(" ");
fprintf('2. OVERALL MEAN SELLING PRICE: %.2f\n', avgAllfprices);

disp(" ");
disp("3. WIN PERCENTAGES BY BIDDER TYPE:");
for i = presentTypes
    if winTypeCount(i) > 0
        fprintf('   %s: %.1f%% (%d/%d wins)\n', getTypeName(i), winTypePercent(i), winTypeCount(i), j);
    end
end

disp(" ");
fprintf('4. WINNER''S CURSE (Average overpayment above common value $1000): $%.2f\n', avgAllfprices - 1000);

disp(" ");
disp("5. AVERAGE SELLING PRICE BY WINNER TYPE:");
for i = presentTypes
    if ~isempty(fprices{i})
        fprintf('   %s winners: $%.2f (overpayment: $%.2f)\n', getTypeName(i), avgfprices(i), avgdCV(i));
    end
end

disp(" ");
disp("6. CHANGE IN ERROR (Initial Error - Final Error):");
disp("   Positive values = improvement (closer to common value)");
for i = presentTypes
    if ~isempty(dError{i})
        fprintf('   %s: %.2f\n', getTypeName(i), avgdError(i));
    end
end

disp(" ");
fprintf('7. AVERAGE AUCTION LENGTH: %.2f rounds\n', avgTime);

disp(" ");
disp("8. AVERAGE WINNER SIGNALS BY TYPE:");
for i = presentTypes
    if ~isempty(winSig{i})
        fprintf('   %s: %.2f\n', getTypeName(i), avgWinSig(i));
    end
end

disp(" ");
disp("9. AVERAGE HIGHEST LOSING BIDDER SIGNALS BY WINNER TYPE:");
for i = presentTypes
    if ~isempty(highestLosingSig{i})
        fprintf('   When %s wins, highest losing signal: %.2f\n', getTypeName(i), avgHighestLosingSig(i));
    end
end

disp(" ");
disp("10. SIGNAL COMPARISON (Winner vs Highest Loser):");
for i = presentTypes
    if ~isempty(winSig{i}) && ~isempty(highestLosingSig{i})
        fprintf('   %s wins: Winner=%.2f, Highest Loser=%.2f, Difference=%.2f\n', ...
            getTypeName(i), avgWinSig(i), avgHighestLosingSig(i), ...
            avgWinSig(i) - avgHighestLosingSig(i));
    end
end

disp(" ");
disp("========================================");
disp("           END OF ANALYTICS            ");
disp("========================================");

disp("Done.") 