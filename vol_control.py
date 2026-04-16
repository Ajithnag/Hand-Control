from __future__ import annotations

import ctypes
from ctypes import POINTER, cast

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class VolumeController:
    def __init__(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

    def get_volume(self) -> float:
        # returns 0.0 - 1.0
        level = self.volume.GetMasterVolumeLevelScalar()
        return float(level)

    def set_volume(self, value: float):
        value = max(0.0, min(1.0, float(value)))
        self.volume.SetMasterVolumeLevelScalar(value, None)

    def change_volume_relative(self, delta: float):
        current = self.get_volume()
        self.set_volume(current + delta)

    def toggle_mute(self):
        muted = self.volume.GetMute()
        self.volume.SetMute(0 if muted else 1, None)
