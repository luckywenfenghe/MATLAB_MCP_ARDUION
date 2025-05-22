function test_ai_input()
% TEST_AI_INPUT Test script to verify AI-controlled input handling

% Test different types of input prompts
fprintf('Testing AI-controlled input handling...\n\n');

% Test 1: Mode selection with AI response
fprintf('Test 1: Mode selection with AI\n');
mode = auto_input('Select mode (1-5): ', 'numeric', '2');  % AI suggests mode 2
fprintf('Received mode: %d\n\n', mode);

% Test 2: Settings modification with AI response
fprintf('Test 2: Settings modification with AI\n');
modify = auto_input('Do you want to modify these settings? (y/n): ', 'string', 'y');  % AI suggests yes
fprintf('Received modify response: %s\n\n', modify);

% Test 3: Numeric input with AI response
fprintf('Test 3: Numeric input with AI\n');
interval = auto_input('Auto-save interval (frames) [1000]: ', 'numeric', '500');  % AI suggests 500
fprintf('Received interval: %d\n\n', interval);

% Test 4: Excel settings with AI response
fprintf('Test 4: Excel settings with AI\n');
excel_enabled = auto_input('Enable Excel auto-save? (y/n) [y]: ', 'string', 'n');  % AI suggests no
fprintf('Received Excel enabled: %s\n\n', excel_enabled);

% Test 5: Temperature filter settings with AI response
fprintf('Test 5: Temperature filter settings with AI\n');
filter_enabled = auto_input('Enable temperature filtering? (y/n) [y]: ', 'string', 'y');  % AI suggests yes
fprintf('Received filter enabled: %s\n\n', filter_enabled);

% Test 6: Method selection with AI response
fprintf('Test 6: Method selection with AI\n');
method = auto_input('Select method (1-3): ', 'numeric', '3');  % AI suggests method 3
fprintf('Received method: %d\n\n', method);

fprintf('All AI-controlled tests completed!\n');
end