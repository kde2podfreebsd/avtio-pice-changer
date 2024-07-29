from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from ..models.quote import Quote
from sqlalchemy.ext.asyncio import AsyncSession
from utils import Avitoitem, get_current_btc_price

class QuoteDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_ads(self, items: List[Avitoitem]) -> bool:
        try:
            async with self.db_session() as session:
                async with session.begin():
                    btc_price = await get_current_btc_price()
                    existing_ids = {row.avito_id for row in await session.execute(select(Quote.avito_id))}
                    incoming_ids = {item.avito_id for item in items}

                    ids_to_delete = existing_ids - incoming_ids
                    if ids_to_delete:
                        await session.execute(select(Quote).filter(Quote.avito_id.in_(ids_to_delete)).delete(synchronize_session=False))

                    for item in items:
                        price_ratio = item.price / btc_price
                        if item.avito_id not in existing_ids:
                            new_quote = Quote(
                                avito_id=item.avito_id,
                                address=item.address,
                                category=item.category,
                                rub_price=item.price,
                                price_ratio=price_ratio,
                                status=item.status.value,
                                title=item.title,
                                url=item.url,
                                last_time_update=datetime.now()
                            )
                            session.add(new_quote)
                await session.commit()
            return True
        except IntegrityError as e:
            print(f"Error creating ads: {e}")
            return False

    async def update_prices(self) -> bool:
        try:
            async with self.db_session() as session:
                async with session.begin():
                    new_btc_price = await get_current_btc_price()
                    quotes = await session.execute(select(Quote.avito_id, Quote.price_ratio))
                    
                    for avito_id, price_ratio in quotes:
                        new_rub_price = new_btc_price * price_ratio
                        await session.execute(
                            select(Quote).filter(Quote.avito_id == avito_id).update(
                                {Quote.rub_price: new_rub_price, Quote.last_time_update: datetime.now()},
                                synchronize_session=False
                            )
                        )
                await session.commit()
            return True
        except IntegrityError as e:
            print(f"Error updating BTC price: {e}")
            return False

    async def update_price(self, avito_id: int, new_price: float) -> bool:
        try:
            async with self.db_session() as session:
                async with session.begin():
                    await session.execute(
                        select(Quote).filter(Quote.avito_id == avito_id).update(
                            {Quote.rub_price: new_price, Quote.last_time_update: datetime.now()},
                            synchronize_session=False
                        )
                    )
                await session.commit()
            return True
        except IntegrityError as e:
            print(f"Error updating price: {e}")
            return False

    async def update_quotes_status(self, avito_id: int) -> bool:
        try:
            async with self.db_session() as session:
                async with session.begin():
                    quote = await session.execute(select(Quote).filter(Quote.avito_id == avito_id))
                    current_status = quote.scalar().quote_status
                    new_status = not current_status
                    await session.execute(
                        select(Quote).filter(Quote.avito_id == avito_id).update(
                            {Quote.quote_status: new_status},
                            synchronize_session=False
                        )
                    )
                await session.commit()
            return True
        except IntegrityError as e:
            print(f"Error updating quote status: {e}")
            return False

    async def get_rub_price(self, avito_id: int) -> Optional[float]:
        try:
            async with self.db_session() as session:
                quote = await session.execute(select(Quote.rub_price).filter(Quote.avito_id == avito_id))
                return quote.scalar()
        except IntegrityError as e:
            print(f"Error getting RUB price: {e}")
            return None

    async def get_all_ads(self) -> List[Quote]:
        try:
            async with self.db_session() as session:
                result = await session.execute(select(Quote))
                return result.scalars().all()
        except IntegrityError as e:
            print(f"Error getting all ads: {e}")
            return []

    async def get_ads_by_status(self, status: bool) -> List[Quote]:
        try:
            async with self.db_session() as session:
                result = await session.execute(select(Quote).filter(Quote.quote_status == status))
                return result.scalars().all()
        except IntegrityError as e:
            print(f"Error getting ads by status: {e}")
            return []

    async def get_ad_by_avito_id(self, avito_id: int) -> Optional[Quote]:
        try:
            async with self.db_session() as session:
                result = await session.execute(select(Quote).filter(Quote.avito_id == avito_id))
                return result.scalar()
        except IntegrityError as e:
            print(f"Error getting ad by avito id: {e}")
            return None
