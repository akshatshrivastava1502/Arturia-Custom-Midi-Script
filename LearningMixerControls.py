import channels
import mixer

from LearningConfig import (
    CHANNEL_CHANGER,
    NEXT_MIXER_CC,
    PREV_MIXER_CC,
    MIX1_CC,
    MIX2_CC,
    MIX3_CC,
    CHANNEL_ENABLER_CC,
    PAN1_CC,
    PAN2_CC,
    PAN3_CC,
)


class LearningMixerControls:
    def __init__(self):
        self.cur_channel = 1

    def handle(self, event, display_service):
        if event.data1 == CHANNEL_CHANGER:
            self._handle_channel_change(event, display_service)
            return True

        if event.data1 == CHANNEL_ENABLER_CC:
            self._handle_channel_enable(event, display_service)
            return True

        if event.data1 in [NEXT_MIXER_CC, PREV_MIXER_CC]:
            self._handle_mixer_bank_change(event, display_service)
            return True

        if event.data1 in [MIX1_CC, MIX2_CC, MIX3_CC]:
            self._handle_track_volume(event, display_service)
            return True

        if event.data1 in [PAN1_CC, PAN2_CC, PAN3_CC]:
            self._handle_track_pan(event, display_service)
            return True

        return False

    def _handle_channel_change(self, event, display_service):
        direction = 1 if event.data2 > 64 else -1
        current = channels.channelNumber()
        total = channels.channelCount()
        new_channel = (current + direction) % total
        channels.selectOneChannel(new_channel)

        print("Selected Channel:", channels.getChannelName(new_channel))
        display_service.sync_main_page(activate=True)
        display_service.show_plugin_for_selected(expires=2500)
        event.handled = True

    def _handle_channel_enable(self, event, display_service):
        if event.data2 > 0:
            channels.unmuteChannel(self.cur_channel)
            display_service.show_channel_mute(muted=False)
        else:
            channels.muteChannel(self.cur_channel)
            display_service.show_channel_mute(muted=True)
        event.handled = True

    def _handle_mixer_bank_change(self, event, display_service):
        if event.data2 <= 0:
            event.handled = True
            return

        total = max(1, mixer.trackCount())
        if event.data1 == NEXT_MIXER_CC:
            self.cur_channel = (self.cur_channel + 3) % total
        else:
            self.cur_channel = (self.cur_channel - 3) % total

        print("Selected Track:", mixer.getTrackName(self.cur_channel))
        self._select_track_triplet(self.cur_channel)
        display_service.show_track_select(self.cur_channel)
        event.handled = True

    def _handle_track_volume(self, event, display_service):
        track_offset = self._offset_for_mix_cc(event.data1)
        total = max(1, mixer.trackCount())
        track_idx = (self.cur_channel + track_offset) % total
        mixer.setTrackVolume(track_idx, self._scale_to_unit(event.data2))
        display_service.show_track_volume(track_idx, event.data2)
        event.handled = True

    def _handle_track_pan(self, event, display_service):
        track_offset = self._offset_for_pan_cc(event.data1)
        total = max(1, mixer.trackCount())
        track_idx = (self.cur_channel + track_offset) % total
        mixer.setTrackPan(track_idx, self._scale_to_pan(event.data2))
        display_service.show_track_pan(track_idx, event.data2)
        event.handled = True

    @staticmethod
    def _offset_for_mix_cc(cc):
        if cc == MIX1_CC:
            return 0
        if cc == MIX2_CC:
            return 1
        return 2

    @staticmethod
    def _offset_for_pan_cc(cc):
        if cc == PAN1_CC:
            return 0
        if cc == PAN2_CC:
            return 1
        return 2

    @staticmethod
    def _scale_to_pan(value):
        if value == 64:
            return 0.0
        return (2 * value / 127.0) - 1.0

    @staticmethod
    def _scale_to_unit(value):
        return value / 127.0

    @staticmethod
    def _select_track_triplet(base_track):
        total = max(1, mixer.trackCount())
        indexes = [base_track % total, (base_track + 1) % total, (base_track + 2) % total]
        mixer.deselectAll()
        for idx in indexes:
            mixer.selectTrack(idx)
