% Grid Dimensions
rows = 30;
cols = 30;
[X, Y] = meshgrid(1:cols, 1:rows);

% Parameters
k_attr = 1; % Attractive constant
k_rep = 10; % Repulsive constant
d_safe = 5; % Safety distance

% Target Position
target_x = 15; % Center of the grid
target_y = 15;

% Obstacles (Rust Locations)
obstacles = [5, 5; 5, 25; 25, 5; 25, 25];

% Compute Potential Field
U_attr = k_attr * ((X - target_x).^2 + (Y - target_y).^2);

U_rep = zeros(size(X));
for i = 1:size(obstacles, 1)
    obs_x = obstacles(i, 1);
    obs_y = obstacles(i, 2);
    dist_to_obs = sqrt((X - obs_x).^2 + (Y - obs_y).^2);
    U_rep = U_rep + k_rep * ((1 ./ dist_to_obs - 1 / d_safe).^2) .* (dist_to_obs <= d_safe);
end

U_total = U_attr + U_rep;


figure;
surf(X, Y, U_total);
xlabel('X');
ylabel('Y');
zlabel('Potential');
title('Potential Field');
shading interp;

figure;
contour(X, Y, U_total, 50);
xlabel('X');
ylabel('Y');
title('Potential Field Contour');

