%% CFD Data Post Processing
clc
clear all
close all

%% Read csv files and json
geom_name = "Assy_ImperviousDisk";
path_geom = "D:\Temp\scaccia_e\dandelionCFD\Main\Sims\" + geom_name;
path_sim = path_geom + "\MeshConv\00002";

cfd_data_plane = readtable(path_sim + "\Flow_data.csv");
cfd_data_line = readtable(path_sim + "\Flow_data_line.csv");

json_str = fileread(path_geom + "\" + geom_name + ".json"); 
json_data = jsondecode(json_str); 

%% Post Processing plane
D = json_data.seed_radius * 2e-3;                   % m

% Vectors
y_coord = cfd_data_plane.("y_coordinate");
z_coord = cfd_data_plane.("z_coordinate");
v_mag = cfd_data_plane.("velocity_magnitude");
v_y = cfd_data_plane.("y_velocity");
v_z = cfd_data_plane.("z_velocity");
p = cfd_data_plane.("pressure");

[~, min_idx] = min(z_coord);
U_free_stream = v_mag(min_idx);                     % m/s

% Streamlines
res = 0.0001;
[yq, zq] = meshgrid(-2.5 * D:res:2.5 * D, max(min(z_coord), -D):res:8 * D);

% vy
cfd_data_mat = horzcat(y_coord, z_coord, v_y);
[~, idx_sort] = sort(cfd_data_mat(:,2));
cfd_data_mat = cfd_data_mat(idx_sort,:);
[~, ~, v_y_interp] = griddata(cfd_data_mat(:,1), cfd_data_mat(:,2), cfd_data_mat(:,3), yq, zq);
v_y_interp = flip(v_y_interp,2);

% vz
cfd_data_mat = horzcat(y_coord, z_coord, v_z);
[~, idx_sort] = sort(cfd_data_mat(:,2));
cfd_data_mat = cfd_data_mat(idx_sort,:);
[~, ~, v_z_interp] = griddata(cfd_data_mat(:,1), cfd_data_mat(:,2), cfd_data_mat(:,3), yq, zq);
v_z_interp = flip(v_z_interp,2);

% Wake characteristics
perc_free_stream = 0.95;

cfd_data_mat = horzcat(y_coord, z_coord, v_mag);
[~, idx_sort] = sort(cfd_data_mat(:,2));
cfd_data_mat = cfd_data_mat(idx_sort,:);

[y_interp, z_interp, v_interp] = griddata(cfd_data_mat(:,1), cfd_data_mat(:,2), cfd_data_mat(:,3), yq, zq);
y_interp = flip(y_interp,2);
v_interp = flip(v_interp,2);

z = z_interp(:,1);
y = y_interp(1,:)';
is_rhs = y >= 0;
is_lhs = y < 0;
y_coord_edge_wake_rhs = nan(length(z), 1);
y_coord_edge_wake_lhs = y_coord_edge_wake_rhs;
for i = 1:length(z)
    v_mag = v_interp(i,:)';
    is_free_stream = v_mag >= (perc_free_stream * U_free_stream);
    is_outise_edge = is_free_stream & is_rhs;
    if any(is_outise_edge)
        y_coord_edge_wake_rhs(i) = min(y(is_free_stream & is_rhs));
        y_coord_edge_wake_lhs(i) = max(y(is_free_stream & is_lhs));
    end
end

w_wake = y_coord_edge_wake_rhs - y_coord_edge_wake_lhs;
[w_max, idx_max_w] = max(w_wake);

% pressure
cfd_data_mat = horzcat(y_coord, z_coord, pressure);
[~, idx_sort] = sort(cfd_data_mat(:,2));
cfd_data_mat = cfd_data_mat(idx_sort,:);
[~, ~, p_interp] = griddata(cfd_data_mat(:,1), cfd_data_mat(:,2), cfd_data_mat(:,3), yq, zq);


% %% Post Processing Centre Line
% 
% %% Plots
% figure("Color", "w")
% plot(cfd_data_line.z_coordinate, cfd_data_line.velocity_magnitude, "LineWidth", 2)

% Velocity Contour plot
figure("Color", "w")
n_contours = 30;
contourf(y_interp,z_interp,v_interp, n_contours, 'edgecolor','none')
hold on
is_z_pos = z >= 0;
plot(y_coord_edge_wake_rhs(is_z_pos), z(is_z_pos), "LineWidth", 2, "Color", "k")
plot(y_coord_edge_wake_lhs(is_z_pos), z(is_z_pos), "LineWidth", 2, "Color", "k")
colormap(jet)
colorbar

% Pressure Contour plot
figure("Color", "w")
n_contours = 30;
contourf(y_interp, z_interp, p_interp, n_contours, 'edgecolor','none')
colormap(jet)
colorbar

% Streamlines plot
figure("Color", "w")
density = 10;
streamslice(y_interp, z_interp, v_y_interp, v_z_interp, density)

% Velocity Contour plot and streamlines
figure("Color", "w")
n_contours = 30;
contourf(y_interp,z_interp,v_interp, n_contours, 'edgecolor','none')
hold on
density = 10;
l = streamslice(y_interp, z_interp, v_y_interp, v_z_interp, density);
set(l,'LineWidth',1)
set(l,'Color','k');
colormap(jet)
colorbar
