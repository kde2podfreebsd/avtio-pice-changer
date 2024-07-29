from avito.user import AvitoUser
import logging
from httpx import AsyncClient, HTTPStatusError
from utils import ChatsInfo

logging.basicConfig(level=logging.INFO)

class AvitoChats(AvitoUser):

    def __init__(self):
        super().__init__().__init__()
        self.chat_ids = list()

    async def get_chats(self):
        async with AsyncClient() as client:
            profile = await self.get_profile()
            url = f'https://api.avito.ru/messenger/v2/accounts/{profile.id}/chats'
            
            response = await client.get(url, headers={'Authorization': f'Bearer {self.auth_cert}'})

            if response.status_code == 200:
                data = response.json()
                chats = ChatsInfo(**data)
                self.chat_ids = [
                    {chat['id']: chat['users'][1]['name']}
                    for chat in chats.chats if chat['users']
                ]
                return chats
            else:
                raise HTTPStatusError(response=response)
            
            
if __name__ == "__main__":
    import asyncio
    chats = AvitoChats()
    asyncio.run(chats.authenticate())
    asyncio.run(chats.get_chats())
    print(chats.chat_ids)
