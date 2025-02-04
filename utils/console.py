import time
from pathlib import Path
from typing import Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.style import Style
from rich.text import Text
from rich.theme import Theme

# Define custom theme
custom_theme = Theme({
    "success": "bold green",
    "error": "bold red",
    "info": "bold blue",
    "warning": "bold yellow",
    "prompt": "bold cyan",
    "header": "bold magenta",
})

# Create console instance
console = Console(theme=custom_theme)

def display_header():
    """Display the application header"""
    header = Text("""
KOBO FORM AUTOMATION 
    """, style="header")
    console.print(header)
    console.print(Panel("KoboToolbox Form Management v1.0", style="info"))

def typewriter_print(text: str, style: str = "default", speed: float = 0.03, end_delay: float = 0.5):
    """Print text with typewriter effect"""
    with console.capture() as capture:
        console.print(text, style=style, end="")
    captured = capture.get()
    
    with console:
        for char in captured:
            console.print(char, style=style, end="")
            time.sleep(speed)
    time.sleep(end_delay)
    console.print()

def validate_api_token(token: str) -> bool:
    """Validate API token format"""
    return len(token) == 40 and token.isalnum()

def validate_asset_uid(uid: str) -> bool:
    """Validate Asset UID format"""
    return len(uid) == 22 and uid.isalnum()

def get_credentials() -> Optional[Tuple[str, str]]:
    """Retrieve stored credentials"""
    cred_file = Path("credentials.txt")
    try:
        if not cred_file.exists():
            return None
        return cred_file.read_text().splitlines()[:2]
    except Exception as e:
        console.print(f"Error reading credentials: {e}", style="error")
        return None

def save_credentials(api_token: str, asset_uid: str):
    """Save credentials securely"""
    try:
        with open('credentials.txt', 'w') as f:
            f.write(f"{api_token}\n{asset_uid}")
        console.print("Credentials securely saved", style="success")
    except Exception as e:
        console.print(f"Failed to save credentials: {e}", style="error")

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
        console.print("Invalid UID - must be 8 alphanumeric characters", style="error")
    
    return api_token, asset_uid