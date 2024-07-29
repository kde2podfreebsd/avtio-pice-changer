import os
import logging
from db import QuoteController
from dotenv import load_dotenv
from typing import Optional
from datetime import datetime
from httpx import AsyncClient
from utils import db_sqlite_path

logging.basicConfig(level=logging.INFO)

class AvitoCore:

    def __init__(self):
        load_dotenv()
        self.qc = QuoteController(db_path=db_sqlite_path)
        self._auth_cert: Optional[str] = None
        super().__init__()

    @property
    def auth_cert(self) -> Optional[str]:
        return self._auth_cert
    
    @auth_cert.setter
    def auth_cert(self, value: Optional[str]) -> None:
        self._auth_cert = value

    async def authenticate(self) -> datetime:
        async with AsyncClient() as client:
            data = {
                'grant_type': 'client_credentials',
                'client_id': f'{os.getenv("CLIENT_ID")}',
                'client_secret': f'{os.getenv("CLIENT_SECRET")}'
            }
            auth_token_url = 'https://api.avito.ru/token/'

            try:
                response = await client.post(auth_token_url, data=data)
                response.raise_for_status()
                self.auth_cert = response.json()['access_token']
                logging.info('Authentication successful')

                return True

            except Exception as e:
                logging.error('Failed to authenticate: %s', e)
                raise e