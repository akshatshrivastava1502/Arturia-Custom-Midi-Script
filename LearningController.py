import midi
import channels
import mixer
import transport
import ui

from LearningDisplayService import LearningDisplayService
from LearningMixerControls import LearningMixerControls
from LearningTransportControls import LearningTransportControls
from LearningConfig import (
    MASTER_VOL,
    PLUGIN_OPEN_CC,
    WID_BROWSER,
    WID_CHANNEL_RACK,
)


class LearningController:
    def __init__(self):
        self.display_service = LearningDisplayService()
        self.mixer_controls = LearningMixerControls()
        self.transport_controls = LearningTransportControls()
        self.state = {
            "channel": -1,
            "plugin": "",
            "playing": False,
            "recording": False,
            "loop": False,
            "metronome": False,
            "snap": -1,
            "focus_browser": False,
            "focus_channel_rack": False,
        }

    def on_init(self):
        print("Custom MIDI Script Loaded ✅")
        self.display_service.show_welcome()
        self.display_service.sync_main_page(activate=True)
        self.display_service.show_plugin_for_selected(expires=2000)

    def on_idle(self):
        self.display_service.refresh()

    def on_channel_change(self):
        self.display_service.sync_main_page(activate=True)
        self.display_service.show_plugin_for_selected(expires=2500)

    def on_refresh(self, flags):
        _ = flags
        selected = channels.selectedChannel()
        plugin_name = self.display_service.plugin_name_for_channel(selected)
        playing = transport.isPlaying() != 0
        recording = transport.isRecording()
        loop_enabled = ui.isLoopRecEnabled()
        metronome_enabled = ui.isMetronomeEnabled()
        snap_mode = ui.getSnapMode()
        focus_browser = ui.getFocused(WID_BROWSER)
        focus_channel_rack = ui.getFocused(WID_CHANNEL_RACK)

        self.display_service.sync_main_page(activate=False)

        if selected != self.state["channel"] or plugin_name != self.state["plugin"]:
            self.display_service.show_plugin_for_selected(expires=2500)

        if playing != self.state["playing"]:
            self.display_service.show_transport_state()

        if recording != self.state["recording"]:
            self.display_service.show_record_state()

        if loop_enabled != self.state["loop"]:
            self.display_service.show_loop_state()

        if metronome_enabled != self.state["metronome"]:
            self.display_service.show_metronome_state()

        if snap_mode != self.state["snap"]:
            self.display_service.show_snap_mode()

        if focus_browser and not self.state["focus_browser"]:
            self.display_service.show_browser_focus()

        if focus_channel_rack and not self.state["focus_channel_rack"]:
            self.display_service.show_channel_rack_focus()

        self.state["channel"] = selected
        self.state["plugin"] = plugin_name
        self.state["playing"] = playing
        self.state["recording"] = recording
        self.state["loop"] = loop_enabled
        self.state["metronome"] = metronome_enabled
        self.state["snap"] = snap_mode
        self.state["focus_browser"] = focus_browser
        self.state["focus_channel_rack"] = focus_channel_rack

    def on_midi_msg(self, event):
        if event.status == midi.MIDI_PITCHBEND:
            value = (event.data2 << 7) | event.data1
            normalized = value * 127.0 / 16383.0
            print("Pitch Bend:", normalized)
            return

        print("MIDI Message Received:", event.data1, event.data2)

        if self.mixer_controls.handle(event, self.display_service):
            return

        if event.data1 == MASTER_VOL:
            mixer.setTrackVolume(0, self._scale_to_volume(event.data2))
            self.display_service.show_master_volume(event.data2)
            event.handled = True
            return

        if self.transport_controls.handle(event, self.display_service):
            return

        if event.data1 == PLUGIN_OPEN_CC and event.data2 > 0:
            channels.showEditor(channels.channelNumber())
            self.display_service.show_plugin_for_selected(expires=2500)
            event.handled = True

    @staticmethod
    def _scale_to_volume(value):
        return (value * 101.5 / 127.0) / 127.0

