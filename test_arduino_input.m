% test_arduino_input.m
% Test script to verify MCP input handling functionality

function test_arduino_input()

clear('all');
close('all');
clc();

% Test different types of input prompts
fprintf('Testing MCP input handling...\n\n');

% Test 1: Mode selection
fprintf('Test 1: Mode selection\n');
mode = auto_input('Select mode (1-5): ', 'numeric');
fprintf('Received mode: %d\n\n', mode);

% Test 2: Settings modification
fprintf('Test 2: Settings modification\n');
modify = auto_input('Do you want to modify these settings? (y/n): ', 'string');
fprintf('Received modify response: %s\n\n', modify);

% Test 3: Numeric input with default
fprintf('Test 3: Numeric input with default\n');
interval = auto_input('Auto-save interval (frames) [1000]: ', 'numeric');
fprintf('Received interval: %d\n\n', interval);

% Test 4: Excel settings
fprintf('Test 4: Excel settings\n');
excel_enabled = auto_input('Enable Excel auto-save? (y/n) [y]: ', 'string');
fprintf('Received Excel enabled: %s\n\n', excel_enabled);

% Test 5: Temperature filter settings
fprintf('Test 5: Temperature filter settings\n');
filter_enabled = auto_input('Enable temperature filtering? (y/n) [y]: ', 'string');
fprintf('Received filter enabled: %s\n\n', filter_enabled);

% Test 6: Method selection
fprintf('Test 6: Method selection\n');
method = auto_input('Select method (1-3): ', 'numeric');
fprintf('Received method: %d\n\n', method);

fprintf('All tests completed!\n');

end

function response = auto_input(prompt, default_type)
% AUTO_INPUT Simulates input function with automatic responses
if nargin < 2
    default_type = 'auto';
end

% Convert prompt to lower case for matching
prompt_lower = lower(prompt);

% Extract default value if present in [default_value] format
default_match = regexp(prompt, '\[(.*?)\]', 'tokens');
if ~isempty(default_match)
    default_value = default_match{1}{1};
else
    default_value = '';
end

% Handle specific prompts
if contains(prompt_lower, 'select mode (1-5)')
    response = 1;
elseif contains(prompt_lower, 'modify these settings?')
    response = 'n';
elseif contains(prompt_lower, 'auto-save interval')
    response = 1000;
elseif contains(prompt_lower, 'frames per file')
    response = 100;
elseif contains(prompt_lower, 'enable excel auto-save?')
    response = 'y';
elseif contains(prompt_lower, 'excel save interval')
    response = 100;
elseif contains(prompt_lower, 'excel frames per file')
    response = 20;
elseif contains(prompt_lower, 'enable txt auto-save?')
    response = 'y';
elseif contains(prompt_lower, 'txt save interval')
    response = 100;
elseif contains(prompt_lower, 'enable temperature filtering?')
    response = 'y';
elseif contains(prompt_lower, 'select method (1-3)')
    response = 1;
elseif contains(prompt_lower, 'window size')
    response = 5;
else
    % Use default value if available
    if ~isempty(default_value)
        if strcmpi(default_type, 'string')
            response = default_value;
        else
            % Try to convert to number if possible
            num_val = str2double(default_value);
            if ~isnan(num_val)
                response = num_val;
            else
                response = default_value;
            end
        end
    else
        % Generic defaults
        if strcmpi(default_type, 'string')
            response = 'y';
        else
            response = 1;
        end
    end
end

% Convert response type if needed
if strcmpi(default_type, 'string') && ~ischar(response)
    response = num2str(response);
elseif strcmpi(default_type, 'numeric') && ischar(response)
    response = str2double(response);
end

% Display the prompt and automatic response
fprintf('%s %s\n', prompt, num2str(response));
end 