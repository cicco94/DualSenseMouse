import pygame
import time

from pynput.mouse import Controller, Button
from pynput import keyboard

# ============================================================
# SETTINGS
# ============================================================

MOUSE_SPEED = 8.0
DEAD_ZONE = 0.08
UPDATE_TIME = 0.004

SPEED_STEP = 1.0
MIN_MOUSE_SPEED = 0.1
MAX_MOUSE_SPEED = 100.0

# ============================================================
# INITIALIZATION
# ============================================================

pygame.init()
pygame.joystick.init()
mouse = Controller()

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

# ============================================================
# INFORMATION
# ============================================================

print()
print("==========================================")
print("        DualSense as Mouse")
print("==========================================")
print()
print(f"Controller: {joystick.get_name()}")
print()
print("Left Stick -> Mouse")
print("X          -> Left Click / Drag&Drop")
print("O          -> Right Click / Drag&Drop")
print("PS         -> Exit")
print()
print("Keyboard:")
print("S + UP     -> Increase Mouse Speed")
print("S + DOWN   -> Decrease Mouse Speed")
print()
print(f"Mouse Speed: {MOUSE_SPEED:.1f}")
print()


# ============================================================
# FUNCTIONS
# ============================================================

def dead_zone(value):
    if abs(value) < DEAD_ZONE:
        return 0.0

    if value > 0:
        return (value - DEAD_ZONE) / (1.0 - DEAD_ZONE)

    return (value + DEAD_ZONE) / (1.0 - DEAD_ZONE)


def clamp(value, minimum, maximum):
    return max(
        minimum,
        min(value, maximum)
    )


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
                        mouse.press(Button.left)
                        cross_down = True

                # O / Circle
                elif event.button == 1:

                    if not circle_down:
                        mouse.press(Button.right)
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
                        mouse.release(Button.left)
                        cross_down = False

                # O / Circle
                elif event.button == 1:

                    if circle_down:
                        mouse.release(Button.right)
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
                mouse.move(
                    int(dx),
                    int(dy)
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
        mouse.release(Button.left)

    if circle_down:
        mouse.release(Button.right)

    # Stop keyboard listener
    keyboard_listener.stop()

    pygame.quit()

    print("DualSenseMouse closed")
