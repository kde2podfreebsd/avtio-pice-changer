import dataclasses
import enum 
import os
from typing import List
from dotenv import load_dotenv
import httpx

load_dotenv()

DB_HOST = os.environ.get("POSTGRES_HOST")
DB_PORT = os.environ.get("POSTGRES_PORT")
DB_NAME = os.environ.get("POSTGRES_DB")
DB_USER = os.environ.get("POSTGRES_USER")
DB_PASS = os.environ.get("POSTGRES_PASSWORD")

async def get_current_btc_price() -> float:
    url = 'https://garantex.org/api/v2/depth?market=btcrub'
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        return float(data['asks'][0]['price'])

# AvtioItemStatus
class ItemStatus(enum.Enum):
    ACTIVE = "active"
    REMOVED = "removed"
    OLD = "old"
    BLOCKED = "blocked"
    REJECTED = "rejected"

# Avtio Item
@dataclasses.dataclass(frozen=True)
class Avitoitem:
    avito_id: int
    address: str
    category: str
    price: float
    status: ItemStatus
    title: str
    url: str 
    quote_status: bool

# Avtio Profile User
########################################
@dataclasses.dataclass(frozen=True)
class AvitoProfile:
    email: str
    id: int
    name: str
    phone: str
    profile_url: str

# Avtio Chats
########################################
@dataclasses.dataclass(frozen=True)
class Location:
    title: str
    lat: float
    lon: float


@dataclasses.dataclass(frozen=True)
class ImageSizes:
    x140: str


@dataclasses.dataclass(frozen=True)
class Images:
    main: ImageSizes
    count: int


@dataclasses.dataclass(frozen=True)
class Value:
    id: int
    title: str
    user_id: int
    images: Images
    status_id: int
    price_string: str
    url: str
    location: Location


@dataclasses.dataclass(frozen=True)
class Context:
    type: str
    value: Value


@dataclasses.dataclass(frozen=True)
class AvatarImages:
    x24: str
    x36: str
    x48: str
    x64: str
    x72: str
    x96: str
    x128: str
    x192: str
    x256: str


@dataclasses.dataclass(frozen=True)
class Avatar:
    default: str
    images: AvatarImages


@dataclasses.dataclass(frozen=True)
class PublicUserProfile:
    user_id: int
    item_id: int
    avatar: Avatar
    url: str


@dataclasses.dataclass(frozen=True)
class User:
    id: int
    name: str
    parsing_allowed: bool
    public_user_profile: PublicUserProfile


@dataclasses.dataclass(frozen=True)
class Content:
    text: str


@dataclasses.dataclass(frozen=True)
class LastMessage:
    id: str
    author_id: int
    created: int
    content: Content
    type: str
    direction: str
    read: int = None
    delivered: int = None


@dataclasses.dataclass(frozen=True)
class Chat:
    id: str
    context: Context
    created: int
    updated: int
    users: List[User]
    last_message: LastMessage


@dataclasses.dataclass(frozen=True)
class Meta:
    has_more: bool


@dataclasses.dataclass(frozen=True)
class ChatsInfo:
    chats: List[Chat]
    meta: Meta

########################################

basedir = os.path.abspath(os.path.dirname(__file__))
db_sqlite_path = os.path.join(basedir, 'db.sqlite')