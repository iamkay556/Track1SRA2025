clear; clc; close all;

load 100xcombs.mat;

% Pentagon vertices on unit circle
n = 5;
theta = linspace(0, 2*pi, n+1); % +1 to close the loop
theta(end) = []; % Remove duplicate

% Vertices
vx = cos(theta);
vy = sin(theta);
vertices = [vx; vy];

% Separate point data and selling price data
[m, n] = size(aucData);

points = [n, 5];
fprices = [n];

for i = 1:n
    for j = 1:5
        aucPoint = aucData{1, i};
        points(i, j) = aucPoint(1, j);
    end

    aucPrice = aucData{2, i};
    fprices(i, 1) = aucPrice;
end

% Normalize
points = points / 20;
fprices = fprices / 1300;

% Calculate point positions
positions = points * vertices';

% Plot the pentagon outline
plot([vx vx(1)], [vy vy(1)], 'k-', 'LineWidth', 1.5)
hold on

% Plot points (Note: third parameter is dot size)
scatter(positions(:,1), positions(:,2), 20, fprices, 'filled')
colormap turbo
colorbar
axis equal

% Label the corners
labels = {'0','0.3','0.5','0.7','1'};
for i = 1:5
    text(vx(i)*1.1, vy(i)*1.1, labels{i}, 'FontWeight', 'bold', 'HorizontalAlignment','center')
end