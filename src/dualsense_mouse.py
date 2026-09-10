import pygame
import time
from pynput.mouse import Controller, Button

MOUSE_SPEED = 8
DEADZONE = 0.08
UPDATE_TIME = 0.004

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


def deadzone(value):
    if abs(value) < DEADZONE:
        return 0.0

    if value > 0:
        return (value - DEADZONE) / (1.0 - DEADZONE)

    return (value + DEADZONE) / (1.0 - DEADZONE)


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

            x = deadzone(x)
            y = deadzone(y)

            # Curva leggermente più morbida
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

    pygame.quit()

    print("DualSenseMouse closed")
