import os
import signal
import json
from flask import Flask, request, jsonify
from threading import Thread
from pyngrok import ngrok
from database.supabase_client import SupabaseClient

class WebhookListener:
    """Manages webhook listener with graceful shutdown capabilities"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.server = None
        self.ngrok_tunnel = None
        self._setup_routes()
        self._configure_ngrok()

    def _configure_ngrok(self):
        """Configure ngrok tunnel"""
        ngrok.set_auth_token(os.getenv("NGROK_AUTH_TOKEN"))
        self.ngrok_tunnel = ngrok.connect(5000)
        print(f" * ngrok tunnel {self.ngrok_tunnel.public_url} -> http://127.0.0.1:5000")

    def _setup_routes(self):
        """Configure Flask routes"""
        @self.app.route('/', methods=['POST'])
        def handle_webhook():
            return self._process_webhook(request)

    def _process_webhook(self, request) -> tuple:
        """Process incoming webhook data"""
        try:
            data = request.get_json(silent=True) or {}
            
            # Process registration attempt
            if data.get('opcion') != 'no_registrado_en_el_padr_n':
                return jsonify({"message": "Not a registration attempt"}), 200

            # Database operations
            with SupabaseClient() as db_client:
                full_name = self._get_full_name(data)
                if not full_name:
                    return jsonify({"error": "Missing name fields"}), 400
                
                if db_client.check_existing_entry(full_name):
                    return jsonify({"message": "Entry exists"}), 200
                
                db_client.insert_registration(data)
                return jsonify({"message": "Registration added"}), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def _get_full_name(self, data: dict) -> Optional[str]:
        """Extract full name from data"""
        name_keys = [
            ('nombre', 'apellido paterno', 'apellido materno'),
            ('Nombre', 'Apellido_paterno', 'Apellido_materno')
        ]
        for keys in name_keys:
            if all(k in data for k in keys[:2]):
                parts = [data.get(k, '') for k in keys]
                return ' '.join(parts).strip()
        return None

    def start(self):
        """Start the listener in background thread"""
        self.server = Thread(target=lambda: self.app.run(host="0.0.0.0", port=5000))
        self.server.daemon = True
        self.server.start()
        print("Listener started")

    def stop(self):
        """Stop the listener and clean up resources"""
        if self.ngrok_tunnel:
            ngrok.disconnect(self.ngrok_tunnel.public_url)
        print("\nListener stopped gracefully")