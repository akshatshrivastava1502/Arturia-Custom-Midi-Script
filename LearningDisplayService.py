import channels
import plugins
import transport
import ui
import patterns
import mixer
from LearningConfig import name
from CustomDisplay import (
    PagedDisplay,
    DISPLAY_TWO_LINES,
    DISPLAY_ENCODER,
    DISPLAY_FADER,
    DISPLAY_PICTO,
)


class LearningDisplayService:
    def __init__(self):
        self.paged_display = PagedDisplay()

    def refresh(self):
        self.paged_display.Refresh()

    def show_welcome(self):
        self.show("Welcome", name, "Connected", expires=1500)

    def show(self, page_name, line1, line2, page_type=DISPLAY_PICTO, value=0, expires=2000):
        self.paged_display.SetPageLines(
            page_name,
            page_type,
            value,
            line1=self._ascii_text(line1),
            line2=self._ascii_text(line2),
        )
        if expires is not None:
            self.paged_display.SetActivePage(page_name, expires=expires)
        else:
            self.paged_display.SetActivePage(page_name)

    def sync_main_page(self, activate=False):
        selected = channels.selectedChannel()
        pattern_name = patterns.getPatternName(patterns.patternNumber())
        if selected >= 0:
            line1 = "{}-{}".format(selected + 1, channels.getChannelName(selected))
        else:
            line1 = "No Selection"

        self.paged_display.SetPageLines("main", DISPLAY_PICTO, 0, line1=line1, line2=pattern_name)
        if activate:
            self.paged_display.SetActivePage("main")

    def plugin_name_for_channel(self, index):
        if index < 0:
            return "No Selection"
        if plugins.isValid(index):
            plugin_name = plugins.getPluginName(index)
            if plugin_name:
                return plugin_name
        return channels.getChannelName(index)

    def show_plugin_for_selected(self, expires=2500):
        selected = channels.selectedChannel()
        name = self.plugin_name_for_channel(selected)
        self.show("plugin", "Plugin", name, page_type=DISPLAY_TWO_LINES, expires=expires)

    def show_transport_state(self):
        if transport.isPlaying() != 0:
            self.show("play", "Play", transport.getSongPosHint(), expires=1500)
        else:
            self.show("pause", "Pause", transport.getSongPosHint(), expires=1500)

    def show_record_state(self):
        if transport.isRecording():
            self.show("record", "Record", "ON", expires=1500)
        else:
            self.show("record", "Record", "OFF", expires=1500)

    def show_loop_state(self):
        self.show("loop", "Loop Mode", "ON" if ui.isLoopRecEnabled() else "OFF", expires=1500)

    def show_metronome_state(self):
        self.show("metro", "Metronome", "ON" if ui.isMetronomeEnabled() else "OFF", expires=1500)

    def show_snap_mode(self):
        snap_mode = {
            0: "Line",
            1: "Cell",
            3: "None",
            4: "1/6 Step",
            5: "1/4 Step",
            6: "1/3 Step",
            7: "1/2 Step",
            8: "Step",
            9: "1/6 Beat",
            10: "1/4 Beat",
            11: "1/3 Beat",
            12: "1/2 Beat",
            13: "Beat",
            14: "Bar",
        }
        mode = ui.getSnapMode()
        self.show("snap", "Snap Mode", snap_mode.get(mode, str(mode)), expires=1500)

    def show_browser_focus(self):
        self.show("browser", "Window", "BROWSER", expires=1500)

    def show_channel_rack_focus(self):
        self.show("channelrack", "Window", "CHANNEL RACK", expires=1500)

    def show_master_volume(self, midi_value):
        master_pct = str(round(mixer.getTrackVolume(0) * 100)) + "%"
        self.show(
            "master_vol",
            "Volume - Master",
            master_pct,
            page_type=DISPLAY_ENCODER,
            value=int(midi_value * 100 / 127),
            expires=1200,
        )

    def show_channel_mute(self, muted):
        self.show("channel_mute", "Channel", "MUTED" if muted else "UNMUTED", expires=1200)

    def show_track_select(self, base_track):
        total = max(1, mixer.trackCount())
        self.show(
            "track_select",
            "Tracks {}-{}".format(base_track, (base_track + 2) % total),
            mixer.getTrackName(base_track),
            expires=1500,
        )

    def show_track_volume(self, track_idx, midi_value):
        self.show(
            "track_vol",
            "Volume - " + str(track_idx),
            str(round(mixer.getTrackVolume(track_idx) * 100)) + "%",
            page_type=DISPLAY_FADER,
            value=int(midi_value * 100 / 127),
            expires=1200,
        )

    def show_track_pan(self, track_idx, midi_value):
        self.show(
            "track_pan",
            "Pan - " + str(track_idx),
            str(round(mixer.getTrackPan(track_idx) * 100)) + "%",
            page_type=DISPLAY_ENCODER,
            value=int(midi_value * 100 / 127),
            expires=1200,
        )

    @staticmethod
    def _ascii_text(text):
        if text is None:
            return ""
        return "".join(ch if ord(ch) < 128 else "?" for ch in str(text))
