import json
from typing import Any, Dict
import asyncio
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from .config import BaseTopicActionMapping


class KafkaConsumerRunner:
    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        mapping_cls: type[BaseTopicActionMapping],
    ):
        self.mapping_cls = mapping_cls
        self._bootstrap_servers = bootstrap_servers
        self._group_id = group_id

    async def start(self):
        topics = list(self.mapping_cls.get_topics())

        backoff = 1
        while True:
            consumer = AIOKafkaConsumer(
                *topics,
                bootstrap_servers=self._bootstrap_servers,
                group_id=self._group_id,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                enable_auto_commit=True,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000,
                max_poll_interval_ms=300000,
                auto_offset_reset="earliest",
            )

            try:
                print("starting kafka consumer group=%s topics=%s" % (self._group_id, topics))
                await consumer.start()
                backoff = 1

                async for msg in consumer:
                    try:
                        # msg.topic -> str, msg.value -> Dict[str, Any]
                        await self.handle_message(msg.topic, msg.value)
                    except Exception:
                        print("error handling message from topic=%s" % msg.topic)

            except asyncio.CancelledError:
                # graceful shutdown requested
                print("consumer task cancelled, stopping consumer group=%s" % self._group_id)
                try:
                    await consumer.stop()
                except Exception:
                    print("error stopping consumer during cancellation")
                raise
            except KafkaError as ke:
                # broker/coordinator related errors (including UnknownMemberId)
                print("Kafka error in consumer group=%s: %s" % (self._group_id, ke))
            except Exception:
                print("unexpected error in consumer loop for group=%s" % self._group_id)
            finally:
                try:
                    await consumer.stop()
                except Exception:
                    print("failed to stop consumer for group=%s" % self._group_id)

            # backoff and retry creating a new consumer to rejoin the group
            print("will restart consumer for group=%s after %s seconds" % (self._group_id, backoff))
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30)

    async def handle_message(self, topic: str, message: Dict[str, Any]):
        meta = message.get("meta", {}) if isinstance(message, dict) else {}
        payload = message.get("payload", {}) if isinstance(message, dict) else {}

        processor_cls = self.mapping_cls.get_processor(topic, meta)

        if not processor_cls:
            # no processor found; log and continue
            print("No processor for topic=%s meta=%s" % (topic, meta))
            return

        processor = processor_cls()
        await processor.run(payload, meta)
