from typing import Any, Dict
from producer import Producer


class Topic:
    def __init__(self, name: str, producer: Producer):
        self.name = name
        self._producer = producer

    async def publish(self, message: Dict[str, Any]):
        await self._producer.send(self.name, message)
