import argparse
import subprocess
import sys
import signal
import os


import asyncio
from loguru import logger


logger.remove()
logger.add(sys.stderr, format="<cyan>{time:YYYY-MM-DD HH:mm:ss.SSS ZZ}</> <blue> - PID {process} - </> <green>{level}:</> <lvl>{message}</>")

async def launch_webserver(port):
    """Run a subprocess and print its output."""
    process = await asyncio.create_subprocess_shell(
        f"python videoserver.py {port}",
        stdout=asyncio.subprocess.PIPE,
        stderr=None,
    )

    logger.info(f"Launched Videoserver on Port {port} with PID: {process.pid}")

    # Wait until the subprocess exits (or is killed)
    returncode = await process.wait()
    logger.info(f"Videoserver on Port {port} exited with code {returncode}")

async def main(port):
    # Start all web servers
    tasks = [launch_webserver(initial_port + i) for i in range(num_servers)]

    # Keep the servers running
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch n webservers on consecutive ports.")
    parser.add_argument(
        "-n", "--num-servers",
        type=int,
        help="The number of servers to launch",
        default=1
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        help="The port number to use (e.g., 8000)",
        default=8000
    )


    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Validate the port number
    initial_port = args.port
    num_servers = args.num_servers
    if initial_port < 1024 or initial_port > 65535:
        print("Error: Port number must be in the interval [1024, 65535]", file=sys.stderr)
        sys.exit(1)
    
    asyncio.run(main(initial_port))

    