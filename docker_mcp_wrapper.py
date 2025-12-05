#!/usr/bin/env python3
"""
Wrapper script for Docker MCP gateway execution on Windows.
This script ensures proper execution of the Docker MCP gateway command.
"""

import sys
import subprocess
import os
import json
import signal

def signal_handler(sig, frame):
    """Handle interrupt signals."""
    print("Received interrupt signal, exiting...", file=sys.stderr)
    sys.exit(0)

def main():
    """Main function to execute the Docker MCP gateway."""
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Docker executable path
        docker_path = r"C:\Program Files\Docker\Docker\resources\bin\docker.exe"
        
        # Check if Docker executable exists
        if not os.path.exists(docker_path):
            print(f"Error: Docker executable not found at {docker_path}", file=sys.stderr)
            sys.exit(1)
        
        # Build the command
        cmd = [docker_path, "mcp", "gateway", "run"]
        
        # Add any additional arguments passed to this script
        cmd.extend(sys.argv[1:])
        
        print(f"Executing command: {' '.join(cmd)}", file=sys.stderr)
        
        # Execute the command
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Forward stdin, stdout, and stderr
        try:
            while True:
                # Check if process is still running
                if process.poll() is not None:
                    break
                    
                # Read from process stdout
                output = process.stdout.readline()
                if output:
                    print(output, end='', flush=True)
                
                # Read from process stderr
                error = process.stderr.readline()
                if error:
                    print(error, end='', file=sys.stderr, flush=True)
                    
                # Read from stdin and forward to process
                try:
                    stdin_input = sys.stdin.readline()
                    if stdin_input:
                        process.stdin.write(stdin_input)
                        process.stdin.flush()
                except EOFError:
                    # Stdin closed, break the loop
                    break
                    
        except KeyboardInterrupt:
            print("Interrupt received, terminating process...", file=sys.stderr)
            process.terminate()
            
        # Wait for the process to complete
        exit_code = process.wait()
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"Error executing Docker MCP gateway: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()