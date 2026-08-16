#!/usr/bin/env python3
"""
Script para obter Refresh Token do Salesforce com PKCE
"""
import webbrowser
import time
import urllib.parse
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import hashlib
import base64
import secrets

# PREENCHA AQUI COM SEUS VALORES:
CONSUMER_KEY = "3MVG9vtcvGoeH2bjjoBRXWHirj6fo...."
CONSUMER_SECRET = "97FE711D7F40A390190B..."

SALESFORCE_INSTANCE = "https://login.salesforce.com"
CALLBACK_URL = "http://localhost:8000/callback"
PORT = 8000

authorization_code = None
server = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global authorization_code

        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)

        if 'code' in params:
            authorization_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = "<html><body><h1>Autorizacao OK!</h1><p>Feche esta janela.</p></body></html>"
            self.wfile.write(html.encode('utf-8'))
        elif 'error' in params:
            error = params['error'][0]
            desc = params.get('error_description', [''])[0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = f"<html><body><h1>Erro: {error}</h1><p>{desc}</p></body></html>"
            self.wfile.write(html.encode('utf-8'))

    def log_message(self, format, *args):
        pass

def generate_pkce():
    """Gera code_verifier e code_challenge para PKCE"""
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode('utf-8').rstrip('=')
    return code_verifier, code_challenge

def get_refresh_token():
    global authorization_code, server

    print("=" * 70)
    print("SALESFORCE REFRESH TOKEN GENERATOR (com PKCE)")
    print("=" * 70)

    # Gerar PKCE
    code_verifier, code_challenge = generate_pkce()
    print("\n[PKCE] Gerando code_verifier e code_challenge...")

    auth_url = f"{SALESFORCE_INSTANCE}/services/oauth2/authorize"
    params = {
        'client_id': CONSUMER_KEY,
        'redirect_uri': CALLBACK_URL,
        'response_type': 'code',
        'scope': 'api refresh_token openid',
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }

    full_url = auth_url + "?" + urllib.parse.urlencode(params)

    print("[1] Abrindo navegador...")

    server = HTTPServer(('localhost', PORT), CallbackHandler)
    print("[2] Aguardando autorizacao...")

    webbrowser.open(full_url)
    print("[3] Navegador aberto! Autorize no Salesforce.\n")

    timeout = 300
    start = time.time()

    while authorization_code is None:
        server.handle_request()
        if time.time() - start > timeout:
            print("ERRO: Timeout de 5 minutos")
            sys.exit(1)

    print("[4] Codigo recebido! Obtendo tokens...")

    token_url = f"{SALESFORCE_INSTANCE}/services/oauth2/token"
    payload = {
        'grant_type': 'authorization_code',
        'client_id': CONSUMER_KEY,
        'client_secret': CONSUMER_SECRET,
        'redirect_uri': CALLBACK_URL,
        'code': authorization_code,
        'code_verifier': code_verifier
    }

    try:
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        tokens = response.json()

        print("\n" + "=" * 70)
        print("CREDENCIAIS PARA GITHUB:")
        print("=" * 70)
        print(f"\nSF_CLIENT_ID:\n  {CONSUMER_KEY}")
        print(f"\nSF_CLIENT_SECRET:\n  {CONSUMER_SECRET}")
        print(f"\nSF_REFRESH_TOKEN:\n  {tokens['refresh_token']}")
        print("\n" + "=" * 70)
        print("\nCopie os 3 valores acima para GitHub Secrets!")

    except Exception as e:
        print(f"ERRO: {str(e)}")
        if 'response' in locals():
            print(f"Response: {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        get_refresh_token()
    except KeyboardInterrupt:
        print("\nCancelado")
        sys.exit(1)
    finally:
        if server:
            server.shutdown()
