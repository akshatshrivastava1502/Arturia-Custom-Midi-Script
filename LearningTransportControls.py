import transport

from LearningConfig import PLAY_CC, RECORD_CC


class LearningTransportControls:
    def handle(self, event, display_service):
        if event.data1 == PLAY_CC:
            self._handle_play(event, display_service)
            return True

        if event.data1 == RECORD_CC:
            self._handle_record(event, display_service)
            return True

        return False

    @staticmethod
    def _handle_play(event, display_service):
        if event.data2 > 0:
            transport.start()
            display_service.show_transport_state()
        event.handled = True

    @staticmethod
    def _handle_record(event, display_service):
        if event.data2 > 0:
            transport.record()
            display_service.show_record_state()
        event.handled = True
