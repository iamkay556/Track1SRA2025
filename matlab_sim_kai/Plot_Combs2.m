% Plots pentagonal scattergram and bar graphs to analyze 100xcombs_2.mat data.
clear; clc; close all;

load 100xcombs_2.mat;

% Get data from mat file
[m, n] = size(aucData);
nTypes = length(aucData{1, 1});

bidderPops = zeros(n, nTypes);
winTypes = zeros(n, nTypes);
fprices = zeros(n, nTypes);
avgdError = zeros(n, nTypes);

for i = 1:n
    aucPop = aucData{1, i};
    bidderPops(i, :) = aucPop(1, :);

    aucWT = aucData{2, i};
    winTypes(i, :) = aucWT(1, :);

    aucPrice = aucData{3, i};
    fprices(i, :) = aucPrice(1, :);

    aucErr = aucData{4, i};
    avgdError(i, :) = aucErr(1, :);
end

% Graph items
labels = {'\alpha = 0','\alpha = 0.3','\alpha = 0.5','\alpha = 0.7','\alpha = 1'};

customColors = [
        128, 179, 255;      % Light blue
        130, 236, 109;      % Light green
        255, 204, 51;       % Yellow
        255, 124, 124;      % Red
        175, 156, 255       % Purple
    ];
customColors = customColors / 255;

font = 'arial';


% Figue Function calls
penta_fprice(bidderPops, winTypes, fprices, labels, font);
penta_fprice(bidderPops, winTypes, fprices, labels, font, 950, 1050);
bar_winTypes_tr(winTypes, labels, customColors, font);
bar_winTypes_tc(winTypes, labels, customColors, font);
bar_winTypes_pr(winTypes, labels, customColors, font);
bar_winTypes_pc(winTypes, labels, customColors, font);
bar_dError_c(avgdError, labels, customColors, font);
bar_dCV(fprices, labels, customColors, font);


% Functions / Figures--------------------------------------------

% Average difference to common value when bidder type wins
function bar_dCV(fprices,labels, customColors, font)
    avgdCV = mean(fprices, 1, 'omitnan');
    avgdCV = avgdCV - 1000;

    figure;
    b = bar(labels, avgdCV);

    % Apply the colors to each bar
    for i = 1:length(avgdCV)
        b.FaceColor = 'flat';
        b.CData(i, :) = customColors(i, :);
    end
    
    % Label axes
    xlabel('\alpha Value', 'FontSize', 16);
    ylabel('Average Final Price Difference from Common Value', 'FontSize', 16);
    
    % Set Font
    fontname(font);
end


% Average dError by type accross all combinations
function bar_dError_c(avgdError, labels, customColors, font)
    avgADE = mean(avgdError, 1, 'omitnan');

    figure;
    b = bar(labels, avgADE);

    % Apply the colors to each bar
    for i = 1:length(avgADE)
        b.FaceColor = 'flat';
        b.CData(i, :) = customColors(i, :);
    end
    
    % Label axes
    xlabel('\alpha Value', 'FontSize', 16);
    ylabel('Average \DeltaError from Common Value', 'FontSize', 16);

    % Set Font
    fontname(font);
end


% Bar chart of winner types by percentage of combinations won (when type present)
function bar_winTypes_pc(winTypes, labels, customColors, font)
    winByComb = zeros(1, length(winTypes(1, :)));

    for i = 1:length(winTypes)
        [~, cWin] = max(winTypes(i, :));
        winByComb(1, cWin) = winByComb(1, cWin) + 1;
    end

    figure;
    b = bar(labels, winByComb/8855);

    % Apply the colors to each bar
    for i = 1:length(winByComb)
        b.FaceColor = 'flat';
        b.CData(i, :) = customColors(i, :);
    end
    
    % Label axes
    xlabel('\alpha Value', 'FontSize', 16);
    ylabel('Combination Win Percent', 'FontSize', 16);

    % Set Font
    fontname(font);
end


% Bar chart of winner types by percentage of runs won (when type present)
function bar_winTypes_pr(winTypes, labels, customColors, font)
    sumWT = sum(winTypes, 1);

    figure;
    b = bar(labels, sumWT/885500);

    % Apply the colors to each bar
    for i = 1:length(sumWT)
        b.FaceColor = 'flat';
        b.CData(i, :) = customColors(i, :);
    end
    
    % Label axes
    xlabel('\alpha Value', 'FontSize', 16);
    ylabel('Run Win Percent', 'FontSize', 16);

    % Set Font
    fontname(font);
end


% Bar chart of winner types by total of combinations won
function bar_winTypes_tc(winTypes, labels, customColors, font)
    winByComb = zeros(1, length(winTypes(1, :)));

    for i = 1:length(winTypes)
        [~, cWin] = max(winTypes(i, :));
        winByComb(1, cWin) = winByComb(1, cWin) + 1;
    end

    figure;
    b = bar(labels, winByComb);

    % Apply the colors to each bar
    for i = 1:length(winByComb)
        b.FaceColor = 'flat';
        b.CData(i, :) = customColors(i, :);
    end
    
    % Label axes
    xlabel('\alpha Value', 'FontSize', 16);
    ylabel('Combination Win Count', 'FontSize', 16);

    % Set Font
    fontname(font);
end


% Bar chart of winner types accross all runs
function bar_winTypes_tr(winTypes, labels, customColors, font)
    sumWT = sum(winTypes, 1);

    figure;
    b = bar(labels, sumWT);

    % Apply the colors to each bar
    for i = 1:length(sumWT)
        b.FaceColor = 'flat';
        b.CData(i, :) = customColors(i, :);
    end
    
    % Label axes
    xlabel('\alpha Value', 'FontSize', 16);
    ylabel('Run Win Count', 'FontSize', 16);

    % Set Font
    fontname(font);
end


% Plot a pentagon with point coordinates aligning with bidder population
% Color is the average selling price
function penta_fprice(bidderPops, winTypes, fprices, labels, font, minfprice, maxfprice)
    % Pentagon vertices on unit circle
    n = length(winTypes(1, :));
    theta = linspace(0, 2*pi, n+1); % +1 to close the loop
    theta(end) = []; % Remove duplicate
    
    % Vertices
    vx = cos(theta);
    vy = sin(theta);
    vertices = [vx; vy];
    
    % Normalize
    bidderPops = bidderPops / 20;
    
    % Calculate point positions
    positions = bidderPops * vertices';

    % Average final prices accross bidder types
    bprices = zeros(n, 1);
    for i = 1:length(fprices)
        % Skip NaNs
        nan = isnan(fprices(i, :));
        sum = 0;

        for j = 1:n
            if (nan(j) == 0)
                sum = sum + (fprices(i, j) * winTypes(i, j));
            end
        end

        bprices(i, 1) = sum / 100;
    end

    % Filter by final price range
    if nargin < 6
        minfprice = -Inf;
    end
    if nargin < 7
        maxfprice = Inf;
    end
    
    inRange = (bprices >= minfprice) & (bprices <= maxfprice);
    positions = positions(inRange, :);
    bprices = bprices(inRange);

    % Plot the pentagon outline
    figure;
    plot([vx vx(1)], [vy vy(1)], "Color", '#a6a6a6', 'LineWidth', 1.5)
    hold on
    
    % Plot bidderPops (Note: third parameter is dot size)
    scatter(positions(:,1), positions(:,2), 20, bprices, 'filled')
    axis equal
    
    % Average Point Location
    if (~isinf(minfprice) || ~isinf(maxfprice))
        avgPoint = [mean(positions(:, 1)), mean(positions(:, 2))];
        scatter(avgPoint(1, 1), avgPoint(1, 2), 20, 'filled', 'diamond','MarkerFaceColor','b');
        disp(['Min: ', num2str(minfprice), ' Max: ', num2str(maxfprice), ' Avg Point: ', num2str(avgPoint(1, 1)), ', ', num2str(avgPoint(1, 2))])
    end
    
    % Label the corners
    for i = 1:n
        text(vx(i)*1.1, vy(i)*1.1, labels{i}, 'FontWeight', 'bold', 'HorizontalAlignment','center')
    end
    
    % Colorbar
    colormap turbo
    cb = colorbar;
    
    if (minfprice == -Inf)
        climMin = 500;
    else
        climMin = minfprice;
    end
    if (maxfprice == Inf)
        climMax = 1250;
    else
        climMax = maxfprice;
    end
    fullmap = turbo(256);
    
    idxMin = round( (climMin - 500) / (1250 - 500) * 255 ) + 1;
    idxMax = round( (climMax - 500) / (1250 - 500) * 255 ) + 1;
    idxMin = max(1, min(256, idxMin));
    idxMax = max(1, min(256, idxMax));

    submap = fullmap(idxMin:idxMax, :);
    colormap(submap);
    
    clim([climMin climMax]);
    cb.Ticks = climMin:50:climMax;
    ylabel(cb, 'Final Price', 'FontSize', 16, 'Rotation', -90);

    % Set Font
    fontname(font);
end

