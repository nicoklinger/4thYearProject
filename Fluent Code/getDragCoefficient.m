%% Script to gather Cd value for a specific geometry
clc
clear all

%% Get all simulation folders 
geom_name = "AssySeed_05h_5r_025t_15spokes_2Circles";
geom_sim_dir = convertCharsToStrings(pwd) + "\Sims\" + geom_name + "\Sims";
all_folders = dir(geom_sim_dir);
dir_flags = [all_folders.isdir];
folders = all_folders(dir_flags); 
folders_name = {folders(3:end).name};

%% Get Reynolds number and initialise Cd
re = str2double(strrep(convertCharsToStrings(folders_name), "_", "."));
cd = nan(1, length(re));

%% Iterate over folders
for f = 1:length(folders_name)
    % Csv file dir
    sim_dir = geom_sim_dir + "\" + convertCharsToStrings(folders_name{f});
    csv_file = dir(sim_dir + "\*.csv");
    
    % Read csv file
    cd_tbl = readtable(sim_dir + "\" + convertCharsToStrings(csv_file.name), ...
                'HeaderLines', 2);
    cd_data = cd_tbl{:,2};
    
    % Get average of Cd value
    cd(f) = getCd(cd_data);
    
end

% Plot
figure("Color", "w")
hold on
grid on
grid minor
box on
plot(re, cd, "LineWidth", 2, "Color", "b")
xlabel("Re [-]")
ylabel("Cd [-]")
title(sprintf("%s - Cd curve", geom_name), 'Interpreter', 'none')

% Save structure .mat
s = struct;
s.("Re_Cd") = horzcat(re', cd');
save(convertCharsToStrings(pwd) + "\Sims\" + geom_name + "\Cd.mat", "s")

function cd = getCd(cd_array)
    % Average of Cd values from iterations
    
    perc = 0.1;
    idx_start = length(cd_array) - round(length(cd_array) * perc);
    cd = mean(cd_array(idx_start:end));

end