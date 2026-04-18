# Learning FL Studio MIDI Script

This project is a custom FL Studio MIDI controller script for a hardware device with buttons, knobs, mixer controls, and an LCD screen. It maps MIDI messages to common FL Studio actions and sends live text feedback back to the controller display.

## What it does

- Controls transport actions like Play and Record.
- Moves between channels and mixer tracks.
- Adjusts track volume and pan.
- Opens the selected plugin editor.
- Shows live feedback on the controller display for the selected channel, plugin, pattern, transport state, snap mode, and focus changes.

## Project files

| File | Purpose |
| --- | --- |
| device_Learning.py | FL Studio entry point. FL Studio calls these functions when the script loads, receives MIDI, refreshes, or changes channels. |
| LearningController.py | Main coordinator for MIDI input, state tracking, and display updates. |
| LearningConfig.py | All MIDI CC numbers and basic script settings. This is the main file to edit when your controller uses different MIDI messages. |
| LearningMixerControls.py | Handles mixer bank navigation, channel mute, volume, and pan control. |
| LearningTransportControls.py | Handles Play and Record buttons. |
| LearningDisplayService.py | Builds the text shown on the controller display. |
| CustomDisplay.py | Low-level display and SysEx helper code for the LCD. |

## Setup

### 1. Put the script in FL Studio's MIDI script folder

This project is already structured like an FL Studio hardware script. Keep the folder inside FL Studio's Hardware scripts location so FL Studio can load it.

### 2. Open FL Studio MIDI settings

In FL Studio, open Options, then MIDI Settings.

### 3. Select your controller input and output

Choose your hardware device as the input port. If your controller has a display or sends feedback, choose the matching output port too.

### 4. Select the Learning script

Assign this script as the controller type for the device. After that, reload or restart FL Studio if needed.

### 5. Test the controls

Move the knobs and press the buttons on the controller. The script should respond immediately and show status messages on the display.

## How to configure the script

Most controller-specific settings live in LearningConfig.py.

### MIDI control assignments

Each constant is a MIDI Control Change number used by the script.

| Setting | Used for |
| --- | --- |
| MASTER_VOL | Master track volume knob |
| BUTTON_CC | Reserved for a button input not currently used in the script |
| CHANNEL_CHANGER | Moves to the next or previous channel depending on knob direction |
| PLAY_CC | Starts playback |
| RECORD_CC | Starts recording |
| NEXT_MIXER_CC | Moves the mixer bank forward by 3 tracks |
| PREV_MIXER_CC | Moves the mixer bank backward by 3 tracks |
| MIX1_CC | Adjusts the first track volume in the current mixer bank |
| MIX2_CC | Adjusts the second track volume in the current mixer bank |
| MIX3_CC | Adjusts the third track volume in the current mixer bank |
| CHANNEL_ENABLER_CC | Mutes or unmutes the currently selected channel |
| PAN1_CC | Adjusts pan for the first track in the current mixer bank |
| PAN2_CC | Adjusts pan for the second track in the current mixer bank |
| PAN3_CC | Adjusts pan for the third track in the current mixer bank |
| PLUGIN_OPEN_CC | Opens the selected channel's plugin editor |

If your controller sends different CC numbers, change these values to match your hardware.

### Display name

The name setting in LearningConfig.py is shown in the welcome message on the controller display. Change it to your own device or project name.

### Display text and SysEx output

CustomDisplay.py controls how text is sent to the LCD screen. If your hardware uses a different manufacturer header, update the SysEx header inside send_to_device().

Important display notes:

- Text is treated as ASCII. Non-ASCII characters are replaced.
- Temporary messages expire after a timeout and then return to the main page.
- The display supports pages for normal text, encoder bars, fader bars, scrolling text, and play/record status icons.

### FL Studio focus checks

WID_CHANNEL_RACK and WID_BROWSER are used to detect when FL Studio focus changes to the Browser or Channel Rack. If you adapt the script to a different workflow, you can adjust these window IDs in LearningConfig.py.

## Typical control behavior

- Turning the channel changer moves the selected channel up or down.
- The play and record buttons control FL Studio transport.
- Mixer bank buttons move through groups of three tracks at a time.
- The three volume and pan knobs control those three tracks in the current bank.
- The mute button toggles the currently selected channel.
- The plugin open button opens the selected channel editor.

## Customizing for a new controller

If you are using different hardware, start with these changes:

1. Update the CC values in LearningConfig.py.
2. Update the SysEx manufacturer header in CustomDisplay.py.
3. Change the welcome name in LearningConfig.py.
4. Adjust any display messages in LearningDisplayService.py.
5. Test each control one by one in FL Studio.

## Troubleshooting

- If nothing responds, confirm the correct MIDI input is selected in FL Studio.
- If the display does not update, check the SysEx header in CustomDisplay.py.
- If a control triggers the wrong action, correct the matching CC value in LearningConfig.py.
- If text looks wrong on the display, verify the controller supports ASCII text and the expected page type.

## Notes for beginners

This script is meant to be edited from the top down:

1. Start with LearningConfig.py for hardware mapping.
2. Move to LearningTransportControls.py and LearningMixerControls.py if you want to change behavior.
3. Edit LearningDisplayService.py if you want different text on the LCD.
4. Edit CustomDisplay.py only if your screen protocol or device header is different.

If you only need to remap buttons or knobs, you usually only need LearningConfig.py.