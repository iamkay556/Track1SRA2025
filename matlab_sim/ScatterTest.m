% === Example Data (replace with your own vectors)
alpha_diff = [0.2, 0.4, 0.7, 0.2, 0.5, 0.3];     % x-axis
signal_diff = [103.32, 135.17, 149.24, 98.28, 115.25, 98.97];         % y-axis

% === Scatter Plot
figure('Color','w', 'Position', [300, 300, 700, 500]);
scatter(alpha_diff, signal_diff, 80, 'filled', 'MarkerFaceColor', [0.2 0.5 0.8])

% === Axes & Labels
xlabel('Difference in \alpha (Initial Signal Weight)', 'FontName', 'Arial', 'FontSize', 14)
ylabel('Difference in Initial Signal', 'FontName', 'Arial', 'FontSize', 14)
title('Alpha vs. Initial Signal Differences', 'FontName', 'Arial', 'FontSize', 16)

grid on
set(gca, 'FontName', 'Arial', 'FontSize', 12)
