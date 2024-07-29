from avito.core import AvitoCore
import logging
from httpx import AsyncClient, HTTPStatusError
from utils import AvitoProfile
from typing import Any

logging.basicConfig(level=logging.INFO)

class AvitoUser(AvitoCore):
    def __init__(self):
        super().__init__()

    async def get_profile(self):
        async with AsyncClient() as client:
            url = 'https://api.avito.ru/core/v1/accounts/self'
            
            response = await client.get(url, headers={'Authorization': f'Bearer {self.auth_cert}'})

            if response.status_code == 200:
                return AvitoProfile(**response.json())
            else:
                raise HTTPStatusError
            
    async def get_balance(self):
        profile = await self.get_profile()
        async with AsyncClient() as client:
            url = f'https://api.avito.ru/core/v1/accounts/{profile.id}/balance/'
            response = await client.get(url, headers={'Authorization': f'Bearer {self.auth_cert}'})

            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPStatusError

            

if __name__ == "__main__": 
    import asyncio
    user = AvitoUser()
    asyncio.run(user.authenticate())
    asyncio.run(user.get_profile())
    asyncio.run(user.get_balance())