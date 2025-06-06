% Arduino Data Collection System
% Clear workspace and command window
close all;
clear all;
clc;

% Display welcome banner
displayWelcomeBanner();

% Initialize global configuration variables
initializeGlobalSettings();

% Show current settings
displayCurrentSettings();

% Allow user to modify settings
if getUserConfirmation('Do you want to modify these settings?')
    modifySettings();
    displayCurrentSettings();
end

% Get operation mode from user
mode = selectOperationMode();

% Execute selected mode
switch mode
    case 1
        % Real-time data collection
        runRealTimeCollection();
    case 2
        % Offline data processing
        runOfflineProcessing();
    case 3
        % Merge data files
        runDataFileMerge();
    case 4
        % Generate reports from existing data
        runReportGeneration();
    case 5
        fprintf('\nExiting program...\n');
end

% Function definitions
function displayWelcomeBanner()
    fprintf('=====================================================\n');
    fprintf('||                                                 ||\n');
    fprintf('||          ARDUINO DATA COLLECTION SYSTEM         ||\n');
    fprintf('||                                                 ||\n');
    fprintf('||     Flow, Pressure, and Temperature Sensors     ||\n');
    fprintf('||                                                 ||\n');
    fprintf('=====================================================\n\n');
end

function text = onOffText(value)
    if value
        text = 'On';
    else
        text = 'Off';
    end
end

function result = getUserConfirmation(promptMessage)
    while true
        response = input([promptMessage ' (y/n): '], 's');
        if strcmpi(response, 'y') || strcmpi(response, 'yes')
            result = true;
            break;
        elseif strcmpi(response, 'n') || strcmpi(response, 'no')
            result = false;
            break;
        else
            fprintf('Please enter "y" or "n".\n');
        end
    end
end

function initializeGlobalSettings()
    global autoSaveInterval autoSaveCount excelAutoSaveEnabled excelSaveInterval
    global excelSaveCount tempFilterEnabled tempFilterMethod tempFilterWindowSize
    global tempFilterAlpha tempFilterThreshold showFilteredTempOnly
    global pressureDensity pressureGravity pressureHeight
    global saveTxtEnabled txtSaveInterval

    % Auto-save settings
    autoSaveInterval = 1000;     % Every 1000 frames
    autoSaveCount = 100;         % Save 100 frames per file

    % Excel auto-save settings
    excelAutoSaveEnabled = true; % Enable Excel auto-save
    excelSaveInterval = 100;     % Every 100 frames
    excelSaveCount = 20;         % Save 20 frames to Excel

    % Temperature filtering settings
    tempFilterEnabled = true;     % Enable temperature filtering
    tempFilterMethod = 'movmean'; % Default method: movmean, expsmooth, kalman
    tempFilterWindowSize = 5;     % Moving average window size
    tempFilterAlpha = 0.3;        % Alpha for exponential smoothing
    tempFilterThreshold = 1.5;    % Max allowed temp change (°C)
    showFilteredTempOnly = false; % Show both raw and filtered temp data
    
    % Pressure difference calculation parameters
    pressureDensity = 1.225;      % Default air density (kg/m³)
    pressureGravity = 9.81;       % Default gravity acceleration (m/s²)
    pressureHeight = 0.0;         % Default height difference (m)

    % TXT save settings
    saveTxtEnabled = true;        % Enable TXT save
    txtSaveInterval = 100;        % Every 100 frames save to TXT
end

function displayCurrentSettings()
    global autoSaveInterval autoSaveCount excelAutoSaveEnabled excelSaveInterval
    global excelSaveCount tempFilterEnabled tempFilterMethod tempFilterWindowSize
    global tempFilterAlpha tempFilterThreshold showFilteredTempOnly
    global pressureDensity pressureGravity pressureHeight
    global saveTxtEnabled txtSaveInterval

    fprintf('\n===== CURRENT SETTINGS =====\n');
    
    % Display auto-save settings
    fprintf('\nData auto-save:\n');
    fprintf('  - Interval: Every %d frames\n', autoSaveInterval);
    fprintf('  - Frames per file: %d\n', autoSaveCount);

    % Display Excel settings
    fprintf('\nExcel auto-save:\n');
    fprintf('  - Enabled: %s\n', onOffText(excelAutoSaveEnabled));
    if excelAutoSaveEnabled
        fprintf('  - Interval: Every %d frames\n', excelSaveInterval);
        fprintf('  - Frames per file: %d\n', excelSaveCount);
    end

    % Display temperature filter settings
    fprintf('\nTemperature filtering:\n');
    fprintf('  - Enabled: %s\n', onOffText(tempFilterEnabled));
    if tempFilterEnabled
        fprintf('  - Method: %s\n', tempFilterMethod);
        fprintf('  - Window size: %d\n', tempFilterWindowSize);
        fprintf('  - Alpha: %.2f\n', tempFilterAlpha);
        fprintf('  - Threshold: %.1f°C\n', tempFilterThreshold);
        fprintf('  - Show filtered only: %s\n', onOffText(showFilteredTempOnly));
    end

    % Display pressure settings
    fprintf('\nPressure calculation parameters:\n');
    fprintf('  - Fluid density: %.3f kg/m³\n', pressureDensity);
    fprintf('  - Gravity: %.2f m/s²\n', pressureGravity);
    fprintf('  - Height difference: %.2f m\n', pressureHeight);

    % Display TXT settings
    fprintf('\nTXT auto-save:\n');
    fprintf('  - Enabled: %s\n', onOffText(saveTxtEnabled));
    if saveTxtEnabled
        fprintf('  - Interval: Every %d frames\n', txtSaveInterval);
    end
end

function mode = selectOperationMode()
    fprintf('\n===== OPERATION MODES =====\n');
    fprintf('1. Real-time data collection\n');
    fprintf('2. Offline data processing\n');
    fprintf('3. Merge data files\n');
    fprintf('4. Generate reports from existing data\n');
    fprintf('5. Exit\n');

    while true
        selection = input('\nSelect mode (1-5): ');
        if isnumeric(selection) && selection >= 1 && selection <= 5 && round(selection) == selection
            mode = selection;
            break;
        else
            fprintf('Invalid selection. Please enter a number between 1 and 5.\n');
        end
    end
end

function value = getNumericInput(prompt, defaultValue)
    input_str = input(prompt, 's');
    if isempty(input_str)
        value = defaultValue;
    else
        value = str2double(input_str);
        if isnan(value)
            fprintf('Invalid input. Using default value: %g\n', defaultValue);
            value = defaultValue;
        end
    end
end

function value = getBooleanInput(prompt, defaultValue)
    input_str = input(prompt, 's');
    if isempty(input_str)
        value = defaultValue;
    else
        if strcmpi(input_str, 'y') || strcmpi(input_str, 'yes')
            value = true;
        elseif strcmpi(input_str, 'n') || strcmpi(input_str, 'no')
            value = false;
        else
            fprintf('Invalid input. Using default value: %s\n', onOffText(defaultValue));
            value = defaultValue;
        end
    end
end

function modifySettings()
    global autoSaveInterval autoSaveCount excelAutoSaveEnabled excelSaveInterval
    global excelSaveCount tempFilterEnabled tempFilterMethod tempFilterWindowSize
    global tempFilterAlpha tempFilterThreshold showFilteredTempOnly
    global pressureDensity pressureGravity pressureHeight
    global saveTxtEnabled txtSaveInterval

    fprintf('\n===== MODIFY SETTINGS =====\n');

    % Data auto-save settings
    fprintf('\nData auto-save settings:\n');
    autoSaveInterval = getNumericInput(['Auto-save interval (frames) [', num2str(autoSaveInterval), ']: '], autoSaveInterval);
    autoSaveCount = getNumericInput(['Frames per file [', num2str(autoSaveCount), ']: '], autoSaveCount);
    
    % Excel auto-save settings
    fprintf('\nExcel auto-save settings:\n');
    excelAutoSaveEnabled = getBooleanInput(['Enable Excel auto-save? (y/n) [', onOffText(excelAutoSaveEnabled), ']: '], excelAutoSaveEnabled);
    if excelAutoSaveEnabled
        excelSaveInterval = getNumericInput(['Excel save interval (frames) [', num2str(excelSaveInterval), ']: '], excelSaveInterval);
        excelSaveCount = getNumericInput(['Excel frames per file [', num2str(excelSaveCount), ']: '], excelSaveCount);
    end

    % TXT auto-save settings
    fprintf('\nTXT auto-save settings:\n');
    saveTxtEnabled = getBooleanInput(['Enable TXT auto-save? (y/n) [', onOffText(saveTxtEnabled), ']: '], saveTxtEnabled);
    if saveTxtEnabled
        txtSaveInterval = getNumericInput(['TXT save interval (frames) [', num2str(txtSaveInterval), ']: '], txtSaveInterval);
    end

    % Temperature filter settings
    fprintf('\nTemperature filter settings:\n');
    tempFilterEnabled = getBooleanInput(['Enable temperature filtering? (y/n) [', onOffText(tempFilterEnabled), ']: '], tempFilterEnabled);
    if tempFilterEnabled
        % Filter method selection
        fprintf('Available filter methods:\n');
        fprintf('1. Moving average (movmean)\n');
        fprintf('2. Exponential smoothing (expsmooth)\n');
        fprintf('3. Kalman filter (kalman)\n');

        methodSelection = getNumericInput('Select method (1-3): ', 1);
        switch methodSelection
            case 1
                tempFilterMethod = 'movmean';
                tempFilterWindowSize = getNumericInput(['Window size [', num2str(tempFilterWindowSize), ']: '], tempFilterWindowSize);
            case 2
                tempFilterMethod = 'expsmooth';
                tempFilterAlpha = getNumericInput(['Alpha value (0-1) [', num2str(tempFilterAlpha), ']: '], tempFilterAlpha);
            case 3
                tempFilterMethod = 'kalman';
        end

        tempFilterThreshold = getNumericInput(['Max temperature change (°C) [', num2str(tempFilterThreshold), ']: '], tempFilterThreshold);
        showFilteredTempOnly = getBooleanInput(['Show only filtered temperatures? (y/n) [', onOffText(showFilteredTempOnly), ']: '], showFilteredTempOnly);
    end

    % Pressure difference calculation parameters
    fprintf('\nPressure difference calculation parameters:\n');
    pressureDensity = getNumericInput(['Fluid density (kg/m³) [', num2str(pressureDensity), ']: '], pressureDensity);
    pressureGravity = getNumericInput(['Gravity (m/s²) [', num2str(pressureGravity), ']: '], pressureGravity);
    pressureHeight = getNumericInput(['Height difference (m) [', num2str(pressureHeight), ']: '], pressureHeight);
end

function runRealTimeCollection()
    fprintf('\nStarting real-time data collection...\n');
    if exist('Arduino_Serial_Data_Reader_Optimized.m', 'file') == 2
        Arduino_Serial_Data_Reader_Optimized();
    else
        fprintf('Error: Arduino_Serial_Data_Reader_Optimized.m not found.\n');
        fprintf('Please make sure the data collection script is in the current directory.\n');
    end
end

function runOfflineProcessing()
    fprintf('\nStarting offline data processing...\n');
    if exist('ProcessArduinoDataEnhanced.m', 'file') == 2
        ProcessArduinoDataEnhanced();
    else
        fprintf('Error: ProcessArduinoDataEnhanced.m not found.\n');
        fprintf('Please make sure the data processing script is in the current directory.\n');
    end
end

function runDataFileMerge()
    fprintf('\nStarting data file merge utility...\n');
    if exist('MergeDataFiles.m', 'file') == 2
        MergeDataFiles();
    else
        fprintf('Error: MergeDataFiles.m not found.\n');
        fprintf('Please make sure the file merging script is in the current directory.\n');
    end
end

function runReportGeneration()
    fprintf('\nStarting report generation utility...\n');
    if exist('PlotingArduinoData.m', 'file') == 2
        PlotingArduinoData();
    else
        fprintf('Error: PlotingArduinoData.m not found.\n');
        fprintf('Please make sure the plotting script is in the current directory.\n');
    end
end