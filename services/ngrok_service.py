from pyngrok import ngrok
import os

class NgrokService:
    """Manages ngrok tunnel configuration"""
    
    @staticmethod
    def initialize():
        """Initialize ngrok with auth token"""
        ngrok.set_auth_token(os.getenv("NGROK_AUTH_TOKEN"))
    
    @staticmethod
    def get_public_url(port: int):
        """Create and return ngrok tunnel"""
        return ngrok.connect(port).public_url