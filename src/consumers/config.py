from typing import Any, Dict

class BaseTopicActionMapping:
    _FUNCTIONS: Dict[str, Any] = {}

    @classmethod
    def get_processor(cls, topic: str, meta: Dict[str, Any]):
        try:
            event = meta["event"]
            return (
                cls._FUNCTIONS
                .get(topic, {})
                .get(event["name"], {})
                .get(str(event["version"]), {})
                .get(event["type"])
            )
        except Exception:
            return None

    @classmethod
    def get_topics(cls):
        return cls._FUNCTIONS.keys()


