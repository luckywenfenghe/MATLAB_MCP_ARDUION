function response = auto_input(original_input, mode_type, ai_response)
% AUTO_INPUT Simulates input function with automatic or AI-controlled responses
% Usage:
%   response = auto_input(original_input) - replaces original input with automatic response
%   response = auto_input(original_input, 'auto') - automatic handling based on content
%   response = auto_input(original_input, 'string') - forces string response
%   response = auto_input(original_input, 'numeric') - forces numeric response
%
% Examples:
%   x = auto_input(input('Enter value: '));
%   name = auto_input(input('Enter name: ', 's'), 'string');
%   
% This function works with the Python interface by checking for a global
% AUTO_INPUT_RESPONSE variable that can be set externally.

% Handle input arguments
if nargin < 2
    mode_type = 'auto';
end

if nargin < 3
    ai_response = '';
end

% Check if original_input is already a function call
if isa(original_input, 'function_handle')
    % If it's a function handle, we'll need to evaluate it
    try
        original_prompt = func2str(original_input);
    catch
        original_prompt = 'Unknown prompt';
    end
    
    % We won't actually call the original input function
    is_string_input = strcmpi(mode_type, 'string');
else
    % It's probably the result of an evaluated input already
    original_prompt = original_input;
    % Try to determine if string input was requested
    is_string_input = strcmpi(mode_type, 'string');
end

% First check for global response variable set by Python
global AUTO_INPUT_RESPONSE;
if ~isempty(AUTO_INPUT_RESPONSE)
    % If Python set a response, use it and clear the variable
    response_str = AUTO_INPUT_RESPONSE;
    AUTO_INPUT_RESPONSE = '';  % Clear for next use
    
    % Convert to appropriate type if needed
    if is_string_input || strcmpi(mode_type, 'string')
        response = response_str;
    else
        % Try to convert to number if possible
        num_val = str2double(response_str);
        if ~isnan(num_val)
            response = num_val;
        else
            response = response_str;
        end
    end
    
    % Display simulated input/output
    fprintf('%s %s\n', original_prompt, response_str);
    return;
end

% If no global variable, proceed with built-in logic
prompt = original_prompt;

% Convert prompt to lower case for matching
if ischar(prompt)
    prompt_lower = lower(prompt);
else
    prompt_lower = '';
end

% Extract default value if present in [default_value] format
if ischar(prompt)
    default_match = regexp(prompt, '\[(.*?)\]', 'tokens');
    if ~isempty(default_match)
        default_value = default_match{1}{1};
    else
        default_value = '';
    end
else
    default_value = '';
end

% If AI response is provided, use it
if ~isempty(ai_response)
    response = ai_response;
else
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
            if is_string_input || strcmpi(mode_type, 'string')
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
            if is_string_input || strcmpi(mode_type, 'string')
                response = 'y';
            else
                response = 1;
            end
        end
    end
end

% Convert response type if needed
if (is_string_input || strcmpi(mode_type, 'string')) && ~ischar(response)
    response = num2str(response);
elseif strcmpi(mode_type, 'numeric') && ischar(response)
    response = str2double(response);
end

% Display the prompt and response
if ischar(response)
    fprintf('%s %s\n', prompt, response);
else
    fprintf('%s %g\n', prompt, response);
end
end