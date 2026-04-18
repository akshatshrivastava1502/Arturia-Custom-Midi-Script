# name=Learning

from LearningController import LearningController


_controller = LearningController()


def OnInit():
    _controller.on_init()


def OnMidiMsg(event):
    _controller.on_midi_msg(event)


def OnRefresh(flags):
    _controller.on_refresh(flags)


def OnIdle():
    _controller.on_idle()


def OnChannelChange():
    _controller.on_channel_change()