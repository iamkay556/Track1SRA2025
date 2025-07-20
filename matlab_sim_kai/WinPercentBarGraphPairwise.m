% Simple bar graph for auction win percentages
clear; clc; close all;

%% ========== INPUT DATA ==========
% 10 auction groups, each with 2 bidder types
% Types: 1=Malleable, 2=Strategic, 3=Balanced, 4=Confident, 5=Static

% Format: [Type1_ID, Type1_%, Type2_ID, Type2_%]
auction1 = [1, 30, 5, 70];  % Malleable vs Static
auction2 = [2, 45, 4, 55];  % Strategic vs Confident  
auction3 = [3, 50, 1, 50];  % Balanced vs Malleable
auction4 = [4, 65, 2, 35];  % Confident vs Strategic
auction5 = [5, 20, 3, 80];  % Static vs Balanced
auction6 = [1, 40, 2, 60];  % Malleable vs Strategic
auction7 = [3, 55, 4, 45];  % Balanced vs Confident
auction8 = [2, 75, 5, 25];  % Strategic vs Static
auction9 = [4, 80, 1, 20];  % Confident vs Malleable
auction10 = [5, 35, 3, 65]; % Static vs Balanced

%% ========== SETUP ==========
% Combine all data
all_auctions = [auction1; auction2; auction3; auction4; auction5; 
                auction6; auction7; auction8; auction9; auction10];

% Colors for each type
type_colors = [
    0.9, 0.3, 0.3;  % 1=Malleable: Red
    0.2, 0.6, 0.9;  % 2=Strategic: Blue  
    0.4, 0.8, 0.4;  % 3=Balanced: Green
    0.9, 0.7, 0.2;  % 4=Confident: Yellow
    0.6, 0.6, 0.6   % 5=Static: Gray
];

type_names = {'Malleable', 'Strategic', 'Balanced', 'Confident', 'Static'};

%% ========== CREATE PLOT ==========
figure('Position', [100, 100, 1200, 600]);

% Create bar positions
x_positions = 1:20;
group_positions = reshape(x_positions, 2, 10)';

% Plot each bar
hold on;
for i = 1:10
    % First bar of group
    type1_id = all_auctions(i, 1);
    type1_pct = all_auctions(i, 2);
    bar(group_positions(i,1), type1_pct, 'FaceColor', type_colors(type1_id,:), 'BarWidth', 0.8);
    
    % Second bar of group  
    type2_id = all_auctions(i, 3);
    type2_pct = all_auctions(i, 4);
    bar(group_positions(i,2), type2_pct, 'FaceColor', type_colors(type2_id,:), 'BarWidth', 0.8);
end

%% ========== FORMATTING ==========
% Labels and limits
xlabel('Auction Groups', 'FontSize', 12);
ylabel('Win Percentage (%)', 'FontSize', 12);
title('Bidder Type Win Percentages Across Auctions', 'FontSize', 14);
ylim([0, 100]);

% X-axis ticks at group centers
group_centers = mean(group_positions, 2);
set(gca, 'XTick', group_centers);
set(gca, 'XTickLabel', 1:10);

% Add percentage labels on bars
for i = 1:10
    text(group_positions(i,1), all_auctions(i,2)+2, sprintf('%.0f%%', all_auctions(i,2)), ...
         'HorizontalAlignment', 'center', 'FontSize', 9);
    text(group_positions(i,2), all_auctions(i,4)+2, sprintf('%.0f%%', all_auctions(i,4)), ...
         'HorizontalAlignment', 'center', 'FontSize', 9);
end

% Legend
legend_handles = [];
for i = 1:5
    h = bar(NaN, NaN, 'FaceColor', type_colors(i,:));
    legend_handles(end+1) = h;
end
legend(legend_handles, type_names, 'Location', 'best');

grid on;
hold off;

disp('Bar graph created! Modify the auction data at the top to update.');