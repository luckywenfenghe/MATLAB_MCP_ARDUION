from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
import sys
import logging
import asyncio
import numpy as np
import json
import re
import openai
import os
import tempfile

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    # timestamp, logger name, level, message
)

logger = logging.getLogger("MatlabMCP")

import matlab.engine
mcp = FastMCP("MatlabMCP")


def try_auto_start_matlab():
    """
    Try to automatically start MATLAB and share engine if no shared sessions found.
    """
    try:
        import subprocess
        import time
        
        logger.info("Attempting to auto-start MATLAB...")
        
        # Create temporary MATLAB script for sharing engine
        startup_script = "temp_auto_startup.m"
        with open(startup_script, 'w') as f:
            f.write("matlab.engine.shareEngine;\n")
            f.write("fprintf('MATLAB engine auto-shared successfully!\\n');\n")
            f.write("fprintf('MCP Server can now connect.\\n');\n")
        
        # Start MATLAB with the startup script
        subprocess.Popen(['matlab', '-r', f"run('{startup_script}')"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # Wait for MATLAB to start and share engine
        logger.info("Waiting for MATLAB to start (30 seconds)...")
        for i in range(30):
            time.sleep(1)
            names = matlab.engine.find_matlab()
            if names:
                logger.info("MATLAB engine auto-started successfully!")
                # Clean up temporary file
                try:
                    os.remove(startup_script)
                except:
                    pass
                return names
            if i % 5 == 0:
                logger.info(f"Still waiting... ({i+1}/30 seconds)")
        
        # Clean up temporary file if MATLAB didn't start
        try:
            os.remove(startup_script)
        except:
            pass
            
        logger.warning("Auto-start timeout. MATLAB may need manual startup.")
        return []
        
    except Exception as e:
        logger.error(f"Auto-start failed: {e}")
        return []

logger.info("Finding shared MATLAB sessions...")
names = matlab.engine.find_matlab()
logger.info(f"Found sessions: {names}")

if not names:
    logger.warning("No shared MATLAB sessions found.")
    logger.info("Attempting to auto-start MATLAB...")
    names = try_auto_start_matlab()

if not names:
    logger.error("No shared MATLAB sessions found after auto-start attempt.")
    logger.error("Please start MATLAB manually and run 'matlab.engine.shareEngine' in its Command Window.")
    logger.error("Or use the provided batch file: start_matlab_mcp.bat")
    sys.exit(0)
else:
    session_name = names[0] 
    logger.info(f"Connecting to session: {session_name}")
    try:
        eng = matlab.engine.connect_matlab(session_name)
        logger.info("Successfully connected to shared MATLAB session.")
    except matlab.engine.EngineError as e:
        logger.error(f"Error connecting or communicating with MATLAB: {e}")
        sys.exit(0)

# Helper Function
def matlab_to_python(data : Any) -> Any:
    """
    Converts common MATLAB data types returned by the engine into JSON-Serializable Python types.
    """
    if isinstance(data, (str, int, float, bool, type(None))):
        # already JSON-serializable
        return data
    elif isinstance(data, matlab.double):
        # convert MATLAB double array to Python list (handles scalars, vectors, matrices)
        # using squeeze to remove singleton dimensions for simpler representation
        np_array = np.array(data).squeeze()
        if np_array.ndim == 0:
            return float(np_array)
        else:
            return np_array.tolist()
    elif isinstance(data, matlab.logical):
        np_array = np.array(data).squeeze()
        if np_array.ndim == 0:
            return bool(np_array)
        else:
            return np_array.tolist()
    elif isinstance(data, matlab.char):
        return str(data)
    else:
        logger.warning(f"Unsupported MATLAB type encountered: {type(data)}. Returning string representation.")
        try:
            return str(data)
        except Exception as e:
            return f"Unserializable MATLAB Type: {type(data)}"
    
    # --- TODO: Add more MATLAB types ---

async def get_ai_response(prompt: str, context: str = "") -> str:
    """
    Get AI response for MATLAB input prompt.
    """
    try:
        # Prepare the prompt for the AI
        system_prompt = """You are an AI assistant helping to control a MATLAB Arduino data collection system.
        You need to provide appropriate responses to MATLAB input prompts.
        Consider the context and provide the most suitable response."""
        
        user_prompt = f"""Context: {context}
        MATLAB Input Prompt: {prompt}
        Please provide an appropriate response. For yes/no questions, use 'y' or 'n'.
        For numeric inputs, provide a number. For file paths, provide a valid path.
        Keep responses concise and appropriate for the context."""
        
        # Call OpenAI API (you'll need to set up your API key)
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=50
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"Error getting AI response: {e}")
        return "1"  # Fallback to default value

def preprocess_matlab_commands(code: str) -> str:
    """
    Preprocess MATLAB commands to handle special cases that might cause JSON parsing issues.
    """
    # List of special MATLAB commands that need to be handled
    special_commands = {
        'clear all': 'clear("all")',
        'close all': 'close("all")',
        'clc': 'clc()',
        'MergeDataF': 'MergeDataF',
        'MergingDat': 'MergingDat',
        'PlotingArd': 'PlotingArd',
        'autoSaveDa': 'autoSaveDa',
        'auto_input': 'auto_input',
        'displayDat': 'displayDat'
    }
    
    # Replace special commands
    processed_code = code
    for cmd, replacement in special_commands.items():
        processed_code = processed_code.replace(cmd, replacement)
    
    return processed_code

def verify_matlab_path(path: str) -> str:
    """
    Verify and normalize MATLAB file paths.
    """
    # Convert any single backslashes to double backslashes
    normalized_path = path.replace('\\', '\\\\')
    return normalized_path

def sanitize_matlab_output(output: str) -> str:
    """
    Sanitize MATLAB output to make it JSON-safe.
    """
    if not isinstance(output, str):
        return str(output)
    
    # Replace problematic characters and escape sequences
    output = output.replace('\\', '\\\\')  # Escape backslashes
    output = output.replace('"', '\\"')    # Escape quotes
    output = output.replace('\n', '\\n')   # Handle newlines
    output = output.replace('\r', '\\r')   # Handle carriage returns
    output = output.replace('\t', '\\t')   # Handle tabs
    
    # Remove or replace other problematic characters
    output = ''.join(char if ord(char) >= 32 else ' ' for char in output)
    
    return output

def extract_filename_from_code(code: str) -> str:
    """
    从 Claude 的指令或代码中提取 filename（如有）。
    支持 @xxx.m 文件名 或 filename='xxx.txt' 格式。
    """
    # 匹配 @xxx.m 文件名
    match = re.match(r'@\w+\.m\s+([^\s]+)', code.strip())
    if match:
        return match.group(1)
    # 匹配 filename='xxx.txt' 或 filename="xxx.txt"
    match2 = re.search(r'filename\s*=\s*[\'"]([^\'"]+)[\'"]', code)
    if match2:
        return match2.group(1)
    return None

def inject_filename_parameter(code: str, filename: str) -> str:
    """
    如果 MATLAB 代码中有 filename 变量或 input filename，则自动注入 filename 参数。
    """
    # 1. 替换函数调用中的 filename 参数
    code = re.sub(
        r'renewPlotArduinoData\s*\(\s*filename\s*\)',
        f"renewPlotArduinoData('{filename}')",
        code
    )
    # 2. 替换 input('filename') 或 input("filename")
    code = re.sub(
        r"input\s*\(\s*['\"]filename['\"]\s*\)",
        f"'{filename}'",
        code
    )
    # 3. 替换 filename=xxx 赋值
    code = re.sub(
        r"filename\s*=\s*['\"].*?['\"]",
        f"filename='{filename}'",
        code
    )
    return code

@mcp.tool()
async def runMatlabCode(code: str) -> dict:
    """
    Run MATLAB code in a shared MATLAB session with AI-controlled input handling.
    """
    logger.info(f"Running MATLAB code request: {code[:100]}...")
    
    # 新增：自动提取并注入 filename 参数（如有）
    filename = extract_filename_from_code(code)
    if filename:
        code = inject_filename_parameter(code, filename)
    
    try:
        # Preprocess the code to handle special MATLAB commands
        processed_code = preprocess_matlab_commands(code)
        
        # First, check if the code contains input statements
        input_patterns = [
            r'input\s*\([^)]*\)',
            r'input\s*\([^)]*,\s*[\'"]s[\'"]\)',
            r'getUserConfirmation\s*\([^)]*\)',
            r'getNumericInput\s*\([^)]*\)',
            r'getBooleanInput\s*\([^)]*\)'
        ]
        
        has_input = any(re.search(pattern, processed_code) for pattern in input_patterns)
        
        if has_input:
            logger.info("Code contains input statements, using AI-controlled method...")
            
            # Replace input statements with auto_input
            modified_code = processed_code
            for pattern in input_patterns:
                modified_code = re.sub(
                    pattern,
                    lambda m: f"auto_input({m.group(0)}, 'auto')",
                    modified_code
                )
            
            # Run the modified code and sanitize output
            result = await asyncio.to_thread(eng.evalc, modified_code)
            sanitized_result = sanitize_matlab_output(result)
            logger.info("Code executed successfully using AI-controlled method.")
            return {"status": "success", "output": sanitized_result}
        else:
            # For code without input statements, try to use the eval approach first
            # This avoids the "Too many output parameters" error
            try:
                # Try with evalc first for capturing output
                result = await asyncio.to_thread(eng.evalc, processed_code)
                sanitized_result = sanitize_matlab_output(result)
                logger.info("Code executed successfully using direct evaluation.")
                return {"status": "success", "output": sanitized_result}
            except Exception as eval_error:
                logger.info(f"Direct evaluation failed with error: {eval_error}")
                logger.info("Falling back to simplified execution without capturing output...")
                
                # Try with eval instead of evalc (doesn't capture output but may avoid parameter issues)
                try:
                    await asyncio.to_thread(eng.eval, processed_code)
                    logger.info("Code executed successfully using simplified evaluation.")
                    return {"status": "success", "output": "Code executed successfully (output not captured)."}
                except Exception as simple_eval_error:
                    logger.info(f"Simplified evaluation failed with error: {simple_eval_error}")
                    logger.info("Falling back to temp file approach...")
                    
                    # Last resort: temp file approach but with careful execution
                    import os
                    import tempfile
                    
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_filename = os.path.join(temp_dir, "temp_script.m")
                        
                        # Write the code to the temporary file with UTF-8 encoding
                        with open(temp_filename, "w", encoding='utf-8') as f:
                            f.write(processed_code)
                        
                        # Get the absolute path of the temporary file
                        abs_temp_path = os.path.abspath(temp_filename)
                        
                        try:
                            # Create a diary file to capture output
                            diary_file = os.path.join(temp_dir, "output.txt")
                            await asyncio.to_thread(eng.eval, f"diary('{verify_matlab_path(diary_file)}')")
                            await asyncio.to_thread(eng.eval, "diary on")
                            
                            # Execute the file but be careful about output parameters
                            # Use eval with run instead of direct run to avoid parameter issues
                            await asyncio.to_thread(eng.eval, f"run('{verify_matlab_path(abs_temp_path)}')")
                            
                            # Get the output from the diary
                            await asyncio.to_thread(eng.eval, "diary off")
                            output = ""
                            if os.path.exists(diary_file):
                                with open(diary_file, 'r', encoding='utf-8') as f:
                                    output = f.read()
                            
                            sanitized_output = sanitize_matlab_output(output)
                            logger.info("Code executed successfully using temp file method.")
                            return {"status": "success", "output": sanitized_output}
                        except Exception as run_error:
                            error_msg = str(run_error)
                            logger.error(f"All execution methods failed. Final error: {error_msg}")
                            return {
                                "status": "error",
                                "error_type": "MatlabExecutionError",
                                "message": f"All execution methods failed. Final error: {error_msg}"
                            }

    except matlab.engine.MatlabExecutionError as e:
        error_msg = sanitize_matlab_output(str(e))
        logger.error(f"MATLAB execution error: {error_msg}", exc_info=True)
        return {
            "status": "error",
            "error_type": "MatlabExecutionError",
            "message": f"Execution failed: {error_msg}"
        }
    except matlab.engine.EngineError as e:
        error_msg = sanitize_matlab_output(str(e))
        logger.error(f"MATLAB Engine communication error: {error_msg}", exc_info=True)
        return {
            "status": "error",
            "error_type": "EngineError",
            "message": f"MATLAB Engine error: {error_msg}"
        }
    except Exception as e:
        error_msg = sanitize_matlab_output(str(e))
        logger.error(f"Unexpected error executing MATLAB code: {error_msg}", exc_info=True)
        return {
            "status": "error",
            "error_type": e.__class__.__name__,
            "message": f"Unexpected error: {error_msg}"
        }

@mcp.tool()
async def getVariable(variable_name: str) -> dict:
    """
    Gets the value of a variable from the MATLAB workspace.

    Args:
        variable_name: The name of the variable to retrieve.

    Returns:
        A dictionary with status and either the variable's value (JSON serializable)
        or an error message, including error_type.
    """
    logger.info(f"Attempting to get variable: '{variable_name}'")
    try:
        if not eng:
            logger.error("No active MATLAB session found for getVariable.")
            return {"status": "error", "error_type": "RuntimeError", "message": "No active MATLAB session found."}

        # using asyncio.to_thread for the potentially blocking workspace access
        # directly accessing eng.workspace[variable_name] is blocking
        def get_var_sync():
             var_str = str(variable_name)
             if var_str not in eng.workspace:
                 raise KeyError(f"Variable '{var_str}' not found in MATLAB workspace.")
             return eng.workspace[var_str]

        matlab_value = await asyncio.to_thread(get_var_sync)

        # convert matlab value to a JSON-serializable Python type
        python_value = matlab_to_python(matlab_value)

        # test serialization before returning
        try:
            json.dumps({"value": python_value}) # test within dummy "dict"
            logger.info(f"Successfully retrieved and converted variable '{variable_name}'.")
            return {"status": "success", "variable": variable_name, "value": python_value}
        except TypeError as json_err:
            logger.error(f"Failed to serialize MATLAB value for '{variable_name}' after conversion: {json_err}", exc_info=True)
            return {
                "status": "error",
                "error_type": "TypeError",
                "message": f"Could not serialize value for variable '{variable_name}'. Original MATLAB type: {type(matlab_value)}"
            }

    except KeyError as ke:
        logger.warning(f"Variable '{variable_name}' not found in workspace: {ke}")
        return {"status": "error", "error_type": "KeyError", "message": str(ke)}
    except matlab.engine.EngineError as e_eng:
        logger.error(f"MATLAB Engine communication error during getVariable: {e_eng}", exc_info=True)
        return {"status": "error", "error_type": "EngineError", "message": f"MATLAB Engine error: {str(e_eng)}"}
    except Exception as e:
        logger.error(f"Unexpected error getting variable '{variable_name}': {e}", exc_info=True)
        return {
            "status": "error",
            "error_type": e.__class__.__name__,
            "message": f"Failed to get variable '{variable_name}': {str(e)}"
        }

def get_default_input(prompt: str) -> Any:
    """
    Generate appropriate default responses based on the input prompt.
    """
    # Convert prompt to lowercase for easier matching
    prompt_lower = prompt.lower()
    
    # Handle Arduino system specific prompts
    if 'select mode (1-5)' in prompt_lower:
        return '1'  # Default to real-time data collection
    
    # Handle settings modification prompts
    if 'modify these settings?' in prompt_lower:
        return 'n'  # Always return 'n' for settings modification
    
    # Handle numeric inputs with default values
    if '[' in prompt and ']' in prompt:
        # Extract default value from prompt if available
        try:
            default_value = re.search(r'\[(.*?)\]', prompt).group(1)
            return default_value.strip()
        except:
            pass
    
    # Handle specific settings prompts
    if 'auto-save interval' in prompt_lower:
        return '1000'
    elif 'frames per file' in prompt_lower:
        return '100'
    elif 'enable excel auto-save?' in prompt_lower:
        return 'y'
    elif 'excel save interval' in prompt_lower:
        return '100'
    elif 'excel frames per file' in prompt_lower:
        return '20'
    elif 'enable txt auto-save?' in prompt_lower:
        return 'y'
    elif 'txt save interval' in prompt_lower:
        return '100'
    elif 'enable temperature filtering?' in prompt_lower or 'temperature filtering?' in prompt_lower:
        return 'y'  # Always return 'y' for temperature filtering
    elif 'select method (1-3)' in prompt_lower:
        return '1'  # Default to moving average
    elif 'window size' in prompt_lower:
        return '5'
    
    # Default handlers for common input types
    if any(word in prompt_lower for word in ['yes', 'no', 'continue', '(y/n)']):
        return 'y'  # Default to yes for confirmation prompts
    elif 'file' in prompt_lower or 'path' in prompt_lower:
        return 'default.txt'  # Default filename
    elif 'number' in prompt_lower:
        return '1'  # Default number
    elif any(word in prompt_lower for word in ['name', 'string']):
        return 'default'  # Default string
    else:
        return '1'  # Generic default response

@mcp.tool()
async def handleMatlabInput(prompt: str = None) -> dict:
    """
    Automatically handle MATLAB input requests with predefined or generated responses.
    
    Args:
        prompt: The input prompt from MATLAB (if available)
        
    Returns:
        A dictionary with status and the provided input value
    """
    try:
        if not prompt:
            return {
                "status": "error",
                "error_type": "ValueError",
                "message": "No input prompt provided"
            }

        logger.info(f"Handling MATLAB input request: {prompt}")
        
        # Generate appropriate response based on the prompt
        response = get_default_input(prompt)
        
        logger.info(f"Providing automatic response: {response}")
        
        # Set the response in MATLAB's global variable
        try:
            # Clear previous response if any
            await asyncio.to_thread(eng.eval, "global AUTO_INPUT_RESPONSE; AUTO_INPUT_RESPONSE = [];")
            # Set new response
            await asyncio.to_thread(eng.eval, f"AUTO_INPUT_RESPONSE = '{response}';")
            
            return {
                "status": "success",
                "prompt": prompt,
                "provided_input": response
            }
        except matlab.engine.MatlabExecutionError as e:
            logger.error(f"Failed to send response to MATLAB: {e}")
            return {
                "status": "error",
                "error_type": "MatlabExecutionError",
                "message": f"Failed to handle input: {str(e)}"
            }
            
    except Exception as e:
        logger.error(f"Unexpected error handling MATLAB input: {e}", exc_info=True)
        return {
            "status": "error",
            "error_type": e.__class__.__name__,
            "message": f"Failed to handle input request: {str(e)}"
        }

if __name__ == "__main__":
    logger.info("Starting MATLAB MCP server...")
    mcp.run(transport='stdio')
    logger.info("MATLAB MCP server is running...")