% Alpha Analysis: Signal differences when lower alpha bidders win
clear; clc; close all;

% Simulation parameters
commonVal = 1000;
rStndDv = 150;
startPrice = 500;
priceIncrement = 20;
numSimulations = 1000;
numBiddersPerType = 10;

% Alpha values for comparison
alphaValues = [0.0, 0.3, 0.5, 0.7, 1.0];
numAlphaValues = length(alphaValues);

% Results storage
winningSignals = [];
alphaDifferences = [];
winRates = [];
lowerAlphaValues = []; % Store the lower alpha values for color mapping

fprintf('Starting Alpha Analysis...\n');
fprintf('Total comparisons to run: %d\n', sum(1:(numAlphaValues-1)));

comparisonCounter = 0;

% Nested loops for alpha comparisons
for i = 1:numAlphaValues-1
    alphaLower = alphaValues(i);
    
    for j = i+1:numAlphaValues
        alphaHigher = alphaValues(j);
        comparisonCounter = comparisonCounter + 1;
        alphaDiff = alphaHigher - alphaLower;
        
        fprintf('\nComparison %d: Alpha %.1f vs Alpha %.1f (diff: %.1f)\n', ...
                comparisonCounter, alphaLower, alphaHigher, alphaDiff);
        
        % Storage for this comparison
        winnerSignals = [];
        lowerAlphaWins = 0;
        
        % Run simulations for this alpha pair
        for sim = 1:numSimulations
            if mod(sim, 250) == 0
                fprintf('  Simulation %d/%d\n', sim, numSimulations);
            end
            
            % Create auction
            auction = AuctionClass;
            auction = auction.setID(sim);
            auction = auction.setVars(commonVal, rStndDv, startPrice, priceIncrement);
            
            % Initialize auction properties
            auction.bidderTypes = [0, 0, 0, 0, 0, 0];
            auction.numBidders = 2 * numBiddersPerType;
            auction.biddersIn(1, 1) = auction.numBidders;
            auction.time = 1;
            auction.price = startPrice;
            auction.dropOutTimes = [];
            auction.dropOutPrices = [];
            
            % Create custom bidder matrix
            auction.bidders = cell(2, numBiddersPerType);
            
            % Create lower alpha bidders (type 1)
            for k = 1:numBiddersPerType
                b = CustomBidder(alphaLower);
                b = b.setID(sim, 1, k);
                b = b.newBidder(normrnd(commonVal, rStndDv));
                auction.bidders{1, k} = b;
            end
            
            % Create higher alpha bidders (type 2)
            for k = 1:numBiddersPerType
                b = CustomBidder(alphaHigher);
                b = b.setID(sim, 2, k);
                b = b.newBidder(normrnd(commonVal, rStndDv));
                auction.bidders{2, k} = b;
            end
            
            % Run auction simulation
            auction = runCustomAuction(auction);
            
            % Fixed: Check if lower alpha bidder won
            % Determine winner type based on winID structure
            winnerType = 0;
            if ~isempty(auction.winID) && length(auction.winID) >= 2
                winnerType = auction.winID(2); % Second element should be type
            elseif ~isempty(auction.winID)
                % If winID is just a scalar or different structure,
                % we need to find the winner type differently
                [m, n] = size(auction.bidders);
                for row = 1:m
                    for col = 1:n
                        b = auction.bidders{row, col};
                        if ~isempty(b) && isequal(b.id, auction.winID)
                            winnerType = row; % Row indicates type
                            break;
                        end
                    end
                    if winnerType > 0
                        break;
                    end
                end
            end
            
            if winnerType == 1  % Type 1 (lower alpha) won
                lowerAlphaWins = lowerAlphaWins + 1;
                
                % Find winner signal
                winnerSignal = 0;
                [m, n] = size(auction.bidders);
                for row = 1:m
                    for col = 1:n
                        b = auction.bidders{row, col};
                        if ~isempty(b) && isequal(b.id, auction.winID)
                            winnerSignal = b.signal;
                            break;
                        end
                    end
                    if winnerSignal > 0
                        break;
                    end
                end
                
                % Store winner signal
                if winnerSignal > 0
                    winnerSignals(end + 1) = winnerSignal;
                end
            end
        end
        
        % Calculate metrics for this alpha pair
        winRate = (lowerAlphaWins / numSimulations) * 100;
        
        if ~isempty(winnerSignals)
            avgWinnerSignal = mean(winnerSignals);
            
            % Store results
            winningSignals(end + 1) = avgWinnerSignal;
            alphaDifferences(end + 1) = alphaDiff;
            winRates(end + 1) = winRate;
            lowerAlphaValues(end + 1) = alphaLower; % Store lower alpha for color mapping
            
            fprintf('  Results: Avg Winner Signal = %.2f, Win Rate = %.1f%% (%d wins)\n', ...
                    avgWinnerSignal, winRate, lowerAlphaWins);
        else
            fprintf('  No wins by lower alpha bidder in this comparison\n');
        end
    end
end

fprintf('\nAnalysis Complete! Creating visualization...\n');

% Create single scatter plot
figure('Position', [200, 200, 800, 600]);

% Create scatter plot with color based on lower alpha value
scatter(alphaDifferences, winningSignals, 100, lowerAlphaValues, 'filled', 'o');
colorbar;
colormap(viridis); % Use viridis colormap for better distinction

% Customize the plot
title('Winning Signal vs Alpha Difference (Lower Alpha Wins)', ...
      'FontSize', 14, 'FontWeight', 'bold');
xlabel('Alpha Difference (Higher α - Lower α)', 'FontSize', 12);
ylabel('Average Winning Signal Value', 'FontSize', 12);

% Add colorbar label
c = colorbar;
c.Label.String = 'Lower Alpha Value';
c.Label.FontSize = 11;

% Set colorbar limits to match alpha range
clim([0.0, 0.7]);

% Add grid for better readability
grid on;
grid minor;

% Add a horizontal line at common value for reference
hold on;
plot([min(alphaDifferences), max(alphaDifferences)], [commonVal, commonVal], 'k--', 'LineWidth', 1);
text(mean(alphaDifferences), commonVal + 20, 'Common Value', 'HorizontalAlignment', 'center');
hold off;

% Print summary statistics
fprintf('\n=== SUMMARY STATISTICS ===\n');
fprintf('Total comparisons: %d\n', length(winningSignals));
fprintf('Mean winning signal: %.4f\n', mean(winningSignals));
fprintf('Std winning signal: %.4f\n', std(winningSignals));
fprintf('Mean win rate: %.2f%%\n', mean(winRates));
fprintf('Range of alpha differences: %.1f to %.1f\n', min(alphaDifferences), max(alphaDifferences));

% Show correlation
corrCoeff = corr(alphaDifferences', winningSignals');
fprintf('Correlation between alpha difference and winning signal: %.4f\n', corrCoeff);

% Save results
save('alpha_analysis_results.mat', 'winningSignals', 'alphaDifferences', ...
     'winRates', 'lowerAlphaValues', 'alphaValues');
fprintf('\nResults saved to alpha_analysis_results.mat\n');


%% Supporting Functions

% Custom auction running function
function auction = runCustomAuction(auction)
    % Run the auction simulation for custom bidders
    while auction.biddersIn(end) > 1
        auction = timeStepCustom(auction);
    end
    
    % Find winner (last bidder standing)
    [m, n] = size(auction.bidders);
    found = false;
    for i = 1:m
        for j = 1:n
            if (~isempty(auction.bidders{i, j}) && auction.bidders{i, j}.stillIn)
                auction.winID = auction.bidders{i, j}.id;
                found = true;
                break;
            end
        end
        if found
            break;
        end
    end
    
    % Set final price
    if length(auction.dropOutPrices) >= 1
        auction.fprice = auction.dropOutPrices(end);
    else
        auction.fprice = auction.price - auction.priceIncrement;
    end
end

function auction = timeStepCustom(auction)
    % Custom time step function for our auction
    auction.time = auction.time + 1;
    auction.price = auction.price + auction.priceIncrement;
    
    % Process dropouts
    [m, n] = size(auction.bidders);
    for i = 1:m
        for j = 1:n
            b = auction.bidders{i, j};
            if (~isempty(b) && b.stillIn)
                % Check if bidder should drop out
                b = b.isDropping(auction.time, auction.price);
                
                % Update dropout tracking
                if ~b.stillIn
                    auction.dropOutTimes(1, end + 1) = b.dropOutTime;
                    auction.dropOutPrices(1, end + 1) = b.dropOutPrice;
                end
                
                auction.bidders{i, j} = b;
            end
        end
    end
    
    % Update valuations and count active bidders
    activeCount = 0;
    for i = 1:m
        for j = 1:n
            b = auction.bidders{i, j};
            if (~isempty(b) && b.stillIn)
                % Update valuation
                b = b.updateVal(auction.time, auction.numBidders, auction.biddersIn, ...
                               auction.dropOutPrices, auction.price);
                
                activeCount = activeCount + 1;
                auction.bidders{i, j} = b;
            end
        end
    end
    
    % Update biddersIn array
    auction.biddersIn(auction.time) = activeCount;
end