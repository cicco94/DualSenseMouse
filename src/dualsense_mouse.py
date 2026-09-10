import pygame
import time
from pynput import keyboard
import ctypes


MOUSE_SPEED = 7.0
DEAD_ZONE = 0.08
UPDATE_TIME = 0.004

SPEED_STEP = 1.0
MIN_MOUSE_SPEED = 0.1
MAX_MOUSE_SPEED = 100.0


# ============================================================
# WINDOWS MOUSE INPUT
# ============================================================

user32 = ctypes.windll.user32

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("mi", MOUSEINPUT)
    ]


def send_mouse_event(flags, dx=0, dy=0):

    extra = ctypes.c_ulong(0)

    mouse_input = MOUSEINPUT(
        dx,
        dy,
        0,
        flags,
        0,
        ctypes.pointer(extra)
    )

    input_data = INPUT(
        0,
        mouse_input
    )

    user32.SendInput(
        1,
        ctypes.byref(input_data),
        ctypes.sizeof(INPUT)
    )


def mouse_move(dx, dy):

    send_mouse_event(
        MOUSEEVENTF_MOVE,
        dx,
        dy
    )


def mouse_left_down():

    send_mouse_event(
        MOUSEEVENTF_LEFTDOWN
    )


def mouse_left_up():

    send_mouse_event(
        MOUSEEVENTF_LEFTUP
    )


def mouse_right_down():

    send_mouse_event(
        MOUSEEVENTF_RIGHTDOWN
    )


def mouse_right_up():

    send_mouse_event(
        MOUSEEVENTF_RIGHTUP
    )


# ============================================================
# INITIALIZATION
# ============================================================

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("DualSense not found")
    time.sleep(3)
    raise SystemExit

joystick = None

for i in range(pygame.joystick.get_count()):
    test = pygame.joystick.Joystick(i)
    test.init()

    name = test.get_name()
    print(f"Controller found: {name}")

    if "DualSense" in name or "Wireless Controller" in name:
        joystick = test
        break

if joystick is None:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

print()
print("==========================================")
print("        DualSense as Mouse")
print("==========================================")
print()
print(f"Controller: {joystick.get_name()}")
print()
print("Left Stick -> Mouse")
print("X              -> Left Click / Drag&Drop")
print("O              -> Right Click / Drag&Drop")
print("PS             -> Exit")
print()
print("Keyboard:")
print("S + UP     -> Increase Mouse Speed")
print("S + DOWN   -> Decrease Mouse Speed")
print()
print(f"Mouse Speed: {MOUSE_SPEED:.1f}")
print()


# ============================================================
# KEYBOARD SPEED CONTROL
# ============================================================

s_pressed = False


def on_key_press(key):

    global s_pressed
    global MOUSE_SPEED

    # S pressed
    if key == keyboard.KeyCode.from_char("s"):
        s_pressed = True

        return

    # S + UP
    if key == keyboard.Key.up and s_pressed:

        MOUSE_SPEED = min(
            MAX_MOUSE_SPEED,
            MOUSE_SPEED + SPEED_STEP
        )

        print(f"Mouse Speed: {MOUSE_SPEED:.1f}")

        return

    # S + DOWN
    if key == keyboard.Key.down and s_pressed:

        MOUSE_SPEED = max(
            MIN_MOUSE_SPEED,
            MOUSE_SPEED - SPEED_STEP
        )

        print(f"Mouse Speed: {MOUSE_SPEED:.1f}")

        return


def on_key_release(key):

    global s_pressed

    if key == keyboard.KeyCode.from_char("s"):
        s_pressed = False


keyboard_listener = keyboard.Listener(
    on_press=on_key_press,
    on_release=on_key_release
)

keyboard_listener.start()


def dead_zone(value):
    if abs(value) < DEAD_ZONE:
        return 0.0

    if value > 0:
        return (value - DEAD_ZONE) / (1.0 - DEAD_ZONE)

    return (value + DEAD_ZONE) / (1.0 - DEAD_ZONE)


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


cross_down = False
circle_down = False
running = True

try:
    while running:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            # ------------------------------------------------
            # ON-PRESS BUTTONS
            # ------------------------------------------------

            elif event.type == pygame.JOYBUTTONDOWN:

                # X / Cross
                if event.button == 0:

                    if not cross_down:
                        mouse_left_down()
                        cross_down = True

                # O / Circle
                elif event.button == 1:

                    if not circle_down:
                        mouse_right_down()
                        circle_down = True

                # PS / Home
                elif event.button in (5, 16, 10):

                    running = False

            # ------------------------------------------------
            # ON-RELEASE BUTTONS
            # ------------------------------------------------

            elif event.type == pygame.JOYBUTTONUP:

                # X / Cross
                if event.button == 0:

                    if cross_down:
                        mouse_left_up()
                        cross_down = False

                # O / Circle
                elif event.button == 1:

                    if circle_down:
                        mouse_right_up()
                        circle_down = False

        # ----------------------------------------------------
        # LEFT STICK
        # ----------------------------------------------------

        if joystick.get_numaxes() >= 2:

            x = joystick.get_axis(0)
            y = joystick.get_axis(1)

            x = dead_zone(x)
            y = dead_zone(y)

            x = x * abs(x)
            y = y * abs(y)

            dx = x * MOUSE_SPEED
            dy = y * MOUSE_SPEED

            if abs(dx) > 0.01 or abs(dy) > 0.01:
                mouse_move(
                    round(dx),
                    round(dy)
                )

        time.sleep(UPDATE_TIME)


finally:

    # --------------------------------------------------------
    # GRACEFUL SHUTDOWN
    # --------------------------------------------------------
    #
    # Release buttons when app is closed
    #

    if cross_down:
        mouse_left_up()

    if circle_down:
        mouse_right_up()

    # Stop keyboard listener
    keyboard_listener.stop()

    pygame.quit()

    print("DualSenseMouse closed")
