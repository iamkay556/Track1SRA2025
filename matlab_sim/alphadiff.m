% === Example Data (replace with your own vectors)
alpha_diff = [0.1, 0.3, -0.2, 0.5, -0.4];     % x-axis
signal_diff = [50, -30, 20, -10, 5];         % y-axis

% === Scatter Plot
figure('Color','w', 'Position', [300, 300, 700, 500]);
scatter(alpha_diff, signal_diff, 80, 'filled', 'MarkerFaceColor', [0.2 0.5 0.8])

% === Axes & Labels
xlabel('Difference in \alpha (Initial Signal Weight)', 'FontName', 'Arial', 'FontSize', 14)
ylabel('Difference in Initial Signal', 'FontName', 'Arial', 'FontSize', 14)
title('Alpha vs. Initial Signal Differences', 'FontName', 'Arial', 'FontSize', 16)

grid on
set(gca, 'FontName', 'Arial', 'FontSize', 12)
