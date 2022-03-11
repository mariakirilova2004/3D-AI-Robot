import google.assistant.library

from aiy.assistant import device_helpers

class Assistant(google.assistant.library.Assistant):
    """Client for the Google Assistant Library.

    Similar to google.assistant.library.Assistant, but handles device
    registration.
    """

    def __init__(self, credentials):
        self._credentials = credentials
        self._model_id = device_helpers.register_model_id(credentials)

        super().__init__(credentials, self._model_id)

    def start(self):
        events = super().start()

        device_helpers.register_device_id(
            self._credentials, self._model_id, self.device_id, "SDK_LIBRARY")

        return events
