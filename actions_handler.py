import ctypes
import os

user32 = ctypes.windll.user32
SW, SH = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

class ActionsHandler:
    def __init__(self):
        self.prev_x, self.prev_y = 0, 0
        self.smooth = 0.2

    def move_mouse(self, landmarks):
        # Index finger tip is landmark 8
        it = landmarks.landmark[8]
        tx, ty = int(it.x * SW), int(it.y * SH)
        cx = self.prev_x + (tx - self.prev_x) * self.smooth
        cy = self.prev_y + (ty - self.prev_y) * self.smooth
        user32.SetCursorPos(int(cx), int(cy))
        self.prev_x, self.prev_y = cx, cy

    def execute(self, action):
        # Mouse & Scroll
        if action == "pinch_click":
            user32.mouse_event(0x0002, 0, 0, 0, 0); user32.mouse_event(0x0004, 0, 0, 0, 0)
        elif action == "scroll_up": user32.mouse_event(0x0800, 0, 0, 120, 0)
        elif action == "scroll_down": user32.mouse_event(0x0800, 0, 0, -120, 0)
        
        # Volume & Media
        elif action == "vol_up": user32.keybd_event(0xAF, 0, 0, 0)
        elif action == "vol_down": user32.keybd_event(0xAE, 0, 0, 0)
        elif action == "play_pause": user32.keybd_event(0xB3, 0, 0, 0)
        
        # System & Tabs
        elif action == "screenshot":
            user32.keybd_event(0x5B, 0, 0, 0) # Win
            user32.keybd_event(0x2C, 0, 0, 0) # PrtSc
            user32.keybd_event(0x2C, 0, 2, 0)
            user32.keybd_event(0x5B, 0, 2, 0)
        elif action == "change_tabs":
            user32.keybd_event(0x12, 0, 0, 0) # Alt
            user32.keybd_event(0x09, 0, 0, 0) # Tab
            user32.keybd_event(0x09, 0, 2, 0)
            user32.keybd_event(0x12, 0, 2, 0)
        elif action == "close_tab":
            user32.keybd_event(0x11, 0, 0, 0) # Ctrl
            user32.keybd_event(0x57, 0, 0, 0) # W
            user32.keybd_event(0x57, 0, 2, 0)
            user32.keybd_event(0x11, 0, 2, 0)

        # Brightness (via PowerShell bridge)
        elif action == "brightness_up":
            os.system("powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness + 10)")
        elif action == "brightness_down":
            os.system("powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness - 10)")