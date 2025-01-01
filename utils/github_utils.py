'''
This code is a modified version of the code provided by GitHub in the following link:
https://github.com/github-technology-partners/signature-verification
'''
from base64 import b64decode
import os
import requests
from ecdsa import VerifyingKey, BadSignatureError
from ecdsa.util import sigdecode_der
from hashlib import sha256


class GitHubHandler:

    def __init__(self, req: requests.Request):
        # Get the key identifier and signature from the request headers
        # headers' example:
        '''
        Host: localhost:3000
        User-Agent: Go-http-client/2.0
        Accept-Encoding: gzip
        X-Request-Id: 0730c8241dbd77371e913623eba114e6
        X-Real-Ip: 10.240.3.64
        X-Forwarded-Port: 443
        X-Forwarded-Scheme: https
        X-Original-Uri: /color
        X-Scheme: https
        Github-Public-Key-Identifier: 4fe6b016179b74078ade7581abf4e84fb398c6fae4fb973972235b84fcd70ca3
        Github-Public-Key-Signature: MEYCIQDxT7J8PrXZfA1p2jXVMLBmzG39pQugJ51QK/fxmv/QAAIhAORAu8grmgNfLuKFCKIdORRP/2ULtuFdtpQiGUgd3luD
        X-Github-Token: YOUR_TEMP_TOKEN
        X-Original-Proto: https
        X-Forwarded-Proto: https
        X-Forwarded-Host: 2npk0g6z-3000.asse.devtunnels.ms
        X-Forwarded-For: 10.240.3.64
        Proxy-Connection: Keep-Alive
        Content-Type: application/json
        Content-Length: 20
        '''
        self.request_url = f"{req.headers.get('X-Forwarded-Scheme')}://{req.headers.get('X-Forwarded-Host')}/skillset"
        self.key_identifier = req.headers.get('Github-Public-Key-Identifier')
        self.github_signature = req.headers.get('Github-Public-Key-Signature')
        self.github_token = req.headers.get('X-Github-Token')
        self.payload = req.data

    def verify_github_signature(self):
        if not self.github_signature:
            return False

        raw_sig = b64decode(self.github_signature)
        headers = {
            "Authorization": f"Bearer: {self.github_token}"
        }
        github_keys_uri = "https://api.github.com/meta/public_keys/copilot_api"
        key_resp = requests.get(github_keys_uri, headers=headers, timeout=5).json()
        for k in key_resp["public_keys"]:
            if k["key_identifier"] == self.key_identifier:
                public_key = k["key"]
                break
        else:
            raise ValueError("Public key not found")

        ecdsa_verifier = VerifyingKey.from_pem(string=public_key, hashfunc=sha256)
        try:
            ecdsa_verifier.verify(
                signature=raw_sig, data=self.payload, sigdecode=sigdecode_der
            )
            return True
        except (BadSignatureError, ValueError):
            return False

    def get_user_login(self, github_token=None):
        github_user_uri = 'https://api.github.com/user'
        headers = {
            'Authorization': f'Bearer {self.github_token or github_token}',
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        response = requests.get(github_user_uri, headers=headers)
        if response.status_code == 200:
            user_login = response.json()['login']
            return user_login
        else:
            return None
    



if __name__ == "__main__": 
    github_handler = GitHubHandler(req=requests.Request())
    user_login = github_handler.get_user_login(github_token='')
    print(user_login)