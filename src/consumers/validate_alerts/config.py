from consumers.config import BaseTopicActionMapping
from consumers.validate_alerts.consumer import ValidateAlertsHandler
from kafka_client import KAFKA_TOPICS


class ValidateAlertsTopics:
    Validate = KAFKA_TOPICS.get("alert_validator")


class ValidateAlertsJobs:
    Validate = "validate_alerts"


class ValidateAlertsAction:
    Validate = "validate"

class ValidateAlertsTopicActionMapping(BaseTopicActionMapping):
    _FUNCTIONS = {
        ValidateAlertsTopics.Validate: {
            ValidateAlertsJobs.Validate: {
                "v1.0": {
                    ValidateAlertsAction.Validate: ValidateAlertsHandler
                }
            }
        }
    }