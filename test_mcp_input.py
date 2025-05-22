import asyncio
import logging
import sys
import os
from main import runMatlabCode, eng

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("TestMCP")

async def test_mcp_input():
    try:
        # Get the current directory
        current_dir = os.getcwd()
        
        # Add current directory to MATLAB path
        logger.info(f"Adding directory to MATLAB path: {current_dir}")
        eng.addpath(current_dir)
        
        # Run the test function
        logger.info("Running test function...")
        await asyncio.to_thread(eng.test_arduino_input, nargout=0)
        logger.info("Test completed successfully")
        
    except Exception as e:
        logger.error(f"Error during test: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_input()) 