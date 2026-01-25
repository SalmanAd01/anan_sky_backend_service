from kafka_client import KAFKA_TOPICS
from consumers.config import BaseTopicActionMapping
from consumers.external_source.consumer import FetchExternalSourceHandler


class FetchExternalTopics:
    Fetch = KAFKA_TOPICS.get("fetch_external_source")


class FetchExternalSourceJobs:
    Fetch = "fetch_external_source"


class FetchExternalSourceAction:
    Fetch = "fetch"



class FetchExternalSourceTopicActionMapping(BaseTopicActionMapping):
    _FUNCTIONS = {
        FetchExternalTopics.Fetch: {
            FetchExternalSourceJobs.Fetch: {
                "v1.0": {
                    FetchExternalSourceAction.Fetch: FetchExternalSourceHandler
                }
            }
        }
    }
