% Matlab English Auction Simulation
clear; clc; close all;

% Values to pass into auction obrunsect
commonVal = 1000;
rStndDv = 150;
startPrice = 500;
priceIncrement = 20;

% Set runs
runs = 100;

% Get all combinations and save in mtx
total = 20;
mtx = [];
for a = 0:(total)
    for b = 0:(total - a)
        for c = 0:(total - a - b)
            for d = 0:(total - a - b - c)
                for e = 0:(total - a - b - c - d)
                    if (a + b + c + d + e == 20)
                        mtx(:, end + 1) = [a, b, c, d, e];
                    end
                     
                end
            end
        end
    end
end

% Get mtx size
[~, combs] = size(mtx);

% Data cell array
% {[a, b, c, d, e], [winner type count], [avg selling price per
% winning bidder], [avg percent improvement per bidder type]}
aucData = {};

% Set a timer
tic;

% Data Collection!
for currComb = 1:combs
    % Pre-allocate data for this combination
    winTypeCount = zeros(1, 5);
    sellingPrices = {[], [], [], [], []};
    dError = {[], [], [], [], []};
    
    % Start runs for combination
    for currRun = 1:runs
        disp(['Simulation ', num2str(currRun + (currComb - 1) * runs), ' / ', num2str(combs * runs), ' -----------------------'])

        % Bidders to pass into auction obrunsect
        nAverage = 0;
        nABG0 = mtx(1, currComb);
        nABG03 = mtx(2, currComb);
        nABG05 = mtx(3, currComb);
        nABG07 = mtx(4, currComb);
        nABG1 = mtx(5, currComb);
        bidderTypes = [nAverage, nABG0, nABG03, nABG05, nABG07, nABG1];
    
        % New auction obrunsect
        auction = AuctionClass;
        auction = auction.setID(currComb * currRun);
        auction = auction.setVars(commonVal, rStndDv, startPrice, priceIncrement);
        auction = auction.setBidders(bidderTypes);
    
        % Run!
        auction = auction.runSim();
        
        % Save data from this run
        winType = auction.wintype - 1;

        winTypeCount(1, winType) = winTypeCount(1, winType) + 1;
        sellingPrices{1, winType}(end + 1) = auction.fprice;
        
        [m, n] = size(auction.bidders);
        commonVal = auction.commonVal;
        for i = 1:m
            for j = 1:n
                b = auction.bidders{i, j};
                if (~isempty(b))
                    dError{1, b.id(1, 2) - 1}(end + 1) = abs(b.signal - commonVal) - abs(b.vals(1, end) - commonVal);
                end
            end
        end

        % Runtime
        elapsedTime = toc;
        disp(['Elapsed time: ', num2str(elapsedTime), ' seconds']);
    end

    % Average sellingPrice per bidder type
    avgfprice = zeros(1, 5);
    for l = 1:5
        avgfprice(l) = mean(sellingPrices{l}); 
    end

    % Average percent improvement per bidder type
    avgPerImprov = zeros(1, 5);
    for l = 1:5
        avgPerImprov(l) = mean(dError{l}); 
    end

    % Update data
    aucData(:, currComb) = {[nABG0, nABG03, nABG05, nABG07, nABG1], winTypeCount, avgfprice, avgPerImprov};
end

disp("All Simulations Finished. --------------------")

elapsedTime = toc;
disp(['Elapsed time: ', num2str(elapsedTime), ' seconds']);

disp("Saving Data...")
save;
disp("Saved.")

disp("Done.")