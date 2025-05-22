import asyncio
import logging
from main import runMatlabCode, eng

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    try:
        # Change to the correct directory
        eng.cd(r'C:\Users\luckywenfeng\Desktop\sucess_code_version3')
        
        # Run the MATLAB script
        logger.info("Running MATLAB script...")
        await asyncio.to_thread(eng.eval, "run_arduino_system")
        logger.info("Script executed successfully")
        
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 