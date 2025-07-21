% === Bidder Types ===
bidder_types = {'Malleable', 'Strategic', 'Balanced', 'Confident', 'Static'};

% Assign a unique color to each bidder type
colors = [
    0.52, 0.72, 1.0;   % Malleable - Blue
    0.51, 0.93, 0.43;  % Strategic - Green
    1.0, 0.8, 0.2;     % Balanced - Orange
    1.0, 0.49, 0.49;   % Confident - Red
    0.69, 0.61, 1.0    % Static - Purple
];

% === Matchups (10 total) ===
matchups = {
    'Malleable', 'Strategic';
    'Malleable', 'Balanced';
    'Malleable', 'Confident';
    'Malleable', 'Static';
    'Strategic', 'Balanced';
    'Strategic', 'Confident';
    'Strategic', 'Static';
    'Balanced', 'Confident';
    'Balanced', 'Static';
    'Confident', 'Static';
};

% === Win data: each row is a matchup with two values summing to 100
win_data = [
    0, 100;
    0, 100;
    0, 100;
    0, 100;
    15.9, 84.1;
    4.4, 95.6;
    1.2, 98.8;
    28.3, 71.7;
    10.7, 89.3;
    28.7, 71.3
];

% === Format bar data into 10 x 5 matrix (matchups x bidder types)
bar_data = zeros(size(win_data,1), length(bidder_types));
for i = 1:size(matchups, 1)
    A = matchups{i, 1};
    B = matchups{i, 2};

    idx_A = find(strcmp(bidder_types, A));
    idx_B = find(strcmp(bidder_types, B));

    bar_data(i, idx_A) = win_data(i, 1);
    bar_data(i, idx_B) = win_data(i, 2);
end

% === Plot stacked bar chart
figure('Color','w', 'Position', [100, 100, 1200, 600]);
b = bar(bar_data, 'stacked', 'BarWidth', 0.6);
for i = 1:length(bidder_types)
    b(i).FaceColor = colors(i,:);
end

% === Add percentage labels inside each bar section
for bar_i = 1:size(bar_data, 1)  % loop through matchups
    tot_height = 0;
    for type_i = 1:length(bidder_types)
        val = bar_data(bar_i, type_i);
        if val > 0
            y_pos = tot_height + val / 2;
            text(bar_i, y_pos, sprintf('%.1f%%', val), ...
                'HorizontalAlignment', 'center', ...
                'VerticalAlignment', 'middle', ...
                'FontSize', 10, 'Color', 'black', ...
                'FontWeight', 'bold', 'FontName', 'Arial');
            tot_height = tot_height + val;
        end
    end
end

% === Axis and Labels
xticks(1:10)
xticklabels(strcat(matchups(:,1), {' vs '}, matchups(:,2)))
xtickangle(30)

ylabel('Win Percentage (%)', 'FontName', 'Arial', 'FontSize', 16)
ylim([0 100])
set(gca, 'FontSize', 16, 'FontName', 'Arial')
legend(bidder_types, 'Location', 'eastoutside', 'FontSize', 12, 'FontName', 'Arial')
grid on
