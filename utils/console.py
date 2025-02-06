from pathlib import Path
from typing import Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from dotenv import load_dotenv
import keyring
import os

# Define custom theme
custom_theme = Theme({
    "success": "bold green",
    "error": "bold red",
    "info": "bold blue",
    "warning": "bold yellow",
    "prompt": "bold cyan",
    "header": "bold magenta",
})
load_dotenv()
# Create console instance
console = Console(theme=custom_theme)

def display_header():
    """Display the application header"""
    header = Text("""
\033[H\033[2J 


██╗  ██╗ ██████╗ ██████╗  ██████╗                                                    
██║ ██╔╝██╔═══██╗██╔══██╗██╔═══██╗                                                   
█████╔╝ ██║   ██║██████╔╝██║   ██║                                                   
██╔═██╗ ██║   ██║██╔══██╗██║   ██║                                                   
██║  ██╗╚██████╔╝██████╔╝╚██████╔╝                                                   
╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝                                                    
███████╗ ██████╗ ██████╗ ███╗   ███╗                                                 
██╔════╝██╔═══██╗██╔══██╗████╗ ████║                                                 
█████╗  ██║   ██║██████╔╝██╔████╔██║                                                 
██╔══╝  ██║   ██║██╔══██╗██║╚██╔╝██║                                                 
██║     ╚██████╔╝██║  ██║██║ ╚═╝ ██║                                                 
╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝                                                 
 █████╗ ██╗   ██╗████████╗ ██████╗ ███╗   ███╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
███████║██║   ██║   ██║   ██║   ██║██╔████╔██║███████║   ██║   ██║██║   ██║██╔██╗ ██║
██╔══██║██║   ██║   ██║   ██║   ██║██║╚██╔╝██║██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║ ╚═╝ ██║██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝

    """, style="header")
    console.print(header)
    console.print(Panel("KoboToolbox Form Management v1.0", style="info"))

def validate_api_token(token: str) -> bool:
    """Validate API token format"""
    return len(token) == 40 and token.isalnum()

def validate_asset_uid(uid: str) -> bool:
    """Validate Asset UID format"""
    return len(uid) == 22 and uid.isalnum()

def get_credentials() -> Optional[Tuple[str, str]]:
    """Retrieve credentials from system keyring"""
    try:
        api_token = keyring.get_password("kobo_toolbox", "api_token")
        asset_uid = keyring.get_password("kobo_toolbox", "asset_uid")
        return (api_token, asset_uid) if api_token and asset_uid else None
    except Exception as e:
        console.print(f"Credential retrieval failed: {e}", style="error")
        return None

def save_credentials(api_token: str, asset_uid: str):
    """Store credentials in system keyring"""
    try:
        keyring.set_password("kobo_toolbox", "api_token", api_token)
        keyring.set_password("kobo_toolbox", "asset_uid", asset_uid)
        console.print("Credentials securely stored in system keyring", style="success")
    except Exception as e:
        console.print(f"Failed to store credentials: {e}", style="error")

def login_prompt() -> Tuple[str, str]:
    """Handle login prompt"""
    console.print(Panel("Authentication Required", style="warning"))
    
    while True:
        api_token = console.input("[prompt]Enter your API Token:[/] ")
        if validate_api_token(api_token):
            break
        console.print("Invalid API token - must be 40 alphanumeric characters", style="error")
    
    console.print("\n[info]Project UID can be found in your form URL:")
    console.print("https://[domain].kobotoolbox.org/forms/[ASSET_UID]/", style="italic")
    
    while True:
        asset_uid = console.input("[prompt]Enter Project UID:[/] ")
        if validate_asset_uid(asset_uid):
            break
        console.print("Invalid UID - must be 22 alphanumeric characters", style="error")
    
    return api_token, asset_uid