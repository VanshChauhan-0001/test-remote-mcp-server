from fastmcp import FastMCP
import json
import random

mcp = FastMCP('First Remote Server Radha')

#tool to add two numbers
@mcp.tool
def add(a: int, b: int) -> int:
    '''This tool add two numbers
    Args: 
        a: First Number
        b: Second Number

    Returns: 
        Sum of a and b
    
    '''
    return a + b

#tool generate a random number
@mcp.tool
def get_random_number(start: int, end: int)-> int:
    '''This tool generates a random number between a specific range
        Args: 
            start: starting Number
            end: ending number
            
        return: 
            a number between start and end '''
    return random.randint(start, end)

#Resource: Server Information
@mcp.resource("info://server")
def server_info()-> str:
    '''get information about this server.'''
    info = {
        'name': 'simple calculator server',
        'version': '1.0.0',
        'description': 'a basic mcp server with math tools',
        'tools': ['add', 'get_random_number'],
        'author': 'Radha'
    }
    return json.dumps(info, indent=2)

#start the server
if __name__ =="__main__":
    mcp.run(transport='http', host = "0.0.0.0", port = 8000)