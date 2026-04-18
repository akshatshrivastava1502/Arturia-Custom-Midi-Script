"""
Custom Controller Display Module
Based on MiniLab3 display implementation
Adapted for custom MIDI controller with LCD display screen
"""

import time
import device
import transport

# Display page types
DISPLAY_DEFAULT = 1      # Default screen
DISPLAY_TWO_LINES = 2    # Two lines screen
DISPLAY_ENCODER = 3      # Encoder/knob screen with bar
DISPLAY_FADER = 4        # Fader screen with bar
DISPLAY_SCROLL = 5       # Scrolling text screen
DISPLAY_PICTO = 10       # Picture/status screen

# Status indicators for picto display
PLAY_STATUS = [0x00, 0x02]
REC_STATUS = [0x00, 0x03]


def send_to_device(data):
    """
    Send SysEx data to the custom controller device.
    Adjust the SysEx header bytes [0xF0, 0x00, 0x20, 0x6B, 0x7F, 0x42] 
    to match your controller's manufacturer ID.
    
    :param data: bytes to send to device
    """
    device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x6B, 0x7F, 0x42]) + data + bytes([0xF7]))


class CustomDisplay:
    """
    Manages text display on custom MIDI controller with scrolling support.
    Handles two lines of up to 16 characters each, with automatic scrolling for longer text.
    """
    
    def __init__(self):
        # Persistent text lines (max 32 chars, will scroll if necessary)
        self._line1 = ' '
        self._line2 = ' '
        self._page_type = DISPLAY_TWO_LINES
        
        # Ephemeral text that expires after timeout
        self._ephemeral_line1 = ' '
        self._ephemeral_line2 = ' '
        self._expiration_time_ms = 0
        
        # Scrolling offset positions
        self._line1_display_offset = 0
        self._line2_display_offset = 0
        
        # Timing for scrolling updates
        self._last_update_ms = self.time_ms()
        self._scroll_interval_ms = 1000  # Update scroll position every 1 second
        
        # Cache the last sent payload to avoid redundant updates
        self._last_payload = bytes()
    
    @staticmethod
    def time_ms():
        """Get current time in milliseconds."""
        return time.monotonic() * 1000
    
    def _get_line_src(self, line):
        """
        Validate that line contains only ASCII characters.
        Replace non-ASCII with "..Undefined text.."
        
        :param line: str to validate
        :return: str (either original or error message)
        """
        is_ascii = True
        for char in line:
            if ord(char) not in range(0, 128):
                is_ascii = False
                break
        
        return line if is_ascii else "..Undefined text.."
    
    def _get_line1_bytes(self):
        """Get line 1 as bytes, handling scrolling and ephemeral text."""
        start_pos = self._line1_display_offset
        end_pos = start_pos + 31
        
        line_src = self._get_line_src(self._line1)
        if self._expiration_time_ms > self.time_ms():
            line_src = self._get_line_src(self._ephemeral_line1)
        
        return bytearray(line_src[start_pos:end_pos], 'ascii')
    
    def _get_line2_bytes(self):
        """Get line 2 as bytes, handling scrolling and ephemeral text."""
        start_pos = self._line2_display_offset
        end_pos = start_pos + 31
        
        line_src = self._get_line_src(self._line2)
        if self._expiration_time_ms > self.time_ms():
            line_src = self._get_line_src(self._ephemeral_line2)
        
        return bytearray(line_src[start_pos:end_pos], 'ascii')
    
    def _get_new_offset(self, start_pos, line_src):
        """Calculate new scroll position for next update."""
        end_pos = start_pos + 31
        if end_pos >= len(line_src) or len(line_src) <= 16:
            return 0  # Reset to beginning if at end or short enough to fit
        else:
            return start_pos + 1  # Scroll by 1 character
    
    def _update_scroll_pos(self):
        """Update scroll positions based on elapsed time."""
        current_time_ms = self.time_ms()
        if current_time_ms >= self._scroll_interval_ms + self._last_update_ms:
            self._line1_display_offset = self._get_new_offset(
                self._line1_display_offset, 
                self._get_line_src(self._line1)
            )
            self._line2_display_offset = self._get_new_offset(
                self._line2_display_offset, 
                self._get_line_src(self._line2)
            )
            self._last_update_ms = current_time_ms
    
    def _refresh_display(self, page_type, value):
        """
        Build and send the display update to the device.
        
        :param page_type: Display type (see DISPLAY_* constants)
        :param value: Value for encoders/faders (0-100)
        """
        data_control = bytes([])
        data_string = bytes([0x04, 0x02, 0x60])
        data_line1 = bytes([0x01]) + self._get_line1_bytes() + bytes([0x00])
        data_line2 = bytes([0x02]) + self._get_line2_bytes() + bytes([0x00])
        
        # Build control bytes based on page type
        if page_type == DISPLAY_DEFAULT:
            # Default screen - no extra controls
            data_control = bytes([])
        
        elif page_type == DISPLAY_TWO_LINES:
            # Two lines screen
            data_control = bytes([0x1F, 0x02, 0x01, 0x00])
        
        elif page_type == DISPLAY_ENCODER:
            # Encoder with bar visualization
            scaled_value = int(int(value) * 127 / 100)
            data_control = bytes([0x1F, 0x03, 0x01, scaled_value, 0x00, 0x00])
        
        elif page_type == DISPLAY_FADER:
            # Fader with bar visualization
            scaled_value = int(int(value) * 127 / 100)
            data_control = bytes([0x1F, 0x04, 0x01, scaled_value, 0x00, 0x00])
        
        elif page_type == DISPLAY_SCROLL:
            # Scrolling text screen
            data_control = bytes([0x1F, 0x05, 0x01, 0x00, 0x00, 0x00])
        
        elif page_type == DISPLAY_PICTO:
            # Picture/indicator screen (e.g., play/rec status)
            data_control = bytes([
                0x1F,
                0x07,
                0x01,
                REC_STATUS[transport.isRecording()],
                PLAY_STATUS[transport.isPlaying() != 0],
                0x01,
                0x00,
            ])
        
        # Combine all data
        string = data_string + data_control + data_line1 + data_line2
        
        # Only send if payload changed to reduce MIDI traffic
        if self._last_payload != string:
            send_to_device(string)
            self._last_payload = string
    
    def SetLines(self, page_type, value, line1=None, line2=None, expires=None):
        """
        Update display text and page type.
        
        :param page_type: Display type (see DISPLAY_* constants)
        :param value: Control value for encoders/faders (0-100)
        :param line1: First line text (leave None to keep current)
        :param line2: Second line text (leave None to keep current)
        :param expires: Milliseconds until this text expires (for temporary messages)
        :return: self (for method chaining)
        """
        if expires is None:
            # Persistent text update
            if line1 is not None:
                self._line1 = line1
                self._line1_display_offset = 0
            if line2 is not None:
                self._line2 = line2
                self._line2_display_offset = 0
        else:
            # Ephemeral text that will auto-clear
            self._expiration_time_ms = self.time_ms() + expires
            if line1 is not None:
                self._ephemeral_line1 = line1
            if line2 is not None:
                self._ephemeral_line2 = line2
        
        self._refresh_display(page_type, value)
        return self
    
    def Refresh(self, page_type=None, value=0):
        """
        Refresh display with scrolling text support.
        Call periodically in your MIDI loop to update scrolling.
        
        :param page_type: Display type (use None to keep current)
        :param value: Control value (0-100)
        :return: self (for method chaining)
        """
        self._update_scroll_pos()
        if page_type is not None:
            self._page_type = page_type
        self._refresh_display(self._page_type, value)
        return self
    
    def ResetScroll(self):
        """Reset scroll position to beginning of both lines."""
        self._line1_display_offset = 0
        self._line2_display_offset = 0
    
    def Clear(self):
        """Clear both display lines."""
        self.SetLines(DISPLAY_TWO_LINES, 0, line1=' ', line2=' ')
        self.ResetScroll()


class PagedDisplay:
    """
    Manages multiple named display pages with automatic switching.
    Allows you to define reusable screens and switch between them.
    """
    
    def __init__(self):
        self._display = CustomDisplay()
        self._pages = {}  # Dictionary: page_name -> {'type': int, 'value': int, 'line1': str, 'line2': str}
        self._active_page = None
        self._ephemeral_page = None
        self._page_expiration_time_ms = 0
        self._page_type = DISPLAY_TWO_LINES
        self._value = 0
    
    def SetPageLines(self, page_name, page_type=DISPLAY_TWO_LINES, value=0, line1=None, line2=None):
        """
        Define or update a display page.
        
        :param page_name: Unique page identifier (string)
        :param page_type: Display type (see DISPLAY_* constants)
        :param value: Control value (0-100)
        :param line1: First line text
        :param line2: Second line text
        """
        self._pages[page_name] = {
            'type': page_type,
            'value': value,
            'line1': line1 if line1 is not None else ' ',
            'line2': line2 if line2 is not None else ' '
        }
        
        # Update display if this page is active
        if self._active_page == page_name:
            self._update_display()
    
    def SetActivePage(self, page_name, expires=None):
        """
        Switch to a display page.
        
        :param page_name: Page to activate
        :param expires: Optional expiration time in ms (for temporary overlays)
        """
        if page_name not in self._pages:
            return

        if expires is not None:
            self._ephemeral_page = page_name
            self._page_expiration_time_ms = CustomDisplay.time_ms() + expires
        else:
            self._active_page = page_name
        self._update_display()
    
    def _update_display(self):
        """Internal: update display with current page content."""
        now_ms = CustomDisplay.time_ms()
        page_name = self._active_page
        if self._ephemeral_page is not None and now_ms < self._page_expiration_time_ms:
            page_name = self._ephemeral_page

        if page_name in self._pages:
            page = self._pages[page_name]
            self._page_type = page['type']
            self._value = page['value']
            self._display.SetLines(
                self._page_type,
                self._value,
                line1=page['line1'],
                line2=page['line2']
            )
    
    def Refresh(self):
        """Refresh display (call periodically for scrolling support)."""
        self._update_display()
        self._display.Refresh(self._page_type, self._value)
