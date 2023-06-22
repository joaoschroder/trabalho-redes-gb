"""
Name: João Pedro Schroder
Date: 22/06/2023
"""

from threading import Thread
from time import sleep
from random import randint
import signal
import sys

# - Define medium
# - Define transmitters
# - Method for transmitters
#   1. Check if the medium is clear to transmit (sensing) -> Random time
#   1.1 If the medium is clear, transmit data to it (sleep 1 second to simulate the transmission and set medium to occupied)
#   1.2 If the medium is occupied, repeat step 1
#   1.3 If the medium has collision (more than one transmitter with same waiting time), run backoff_algorithm
#   1.3.1 Generate a random value between 1 and 32 to wait
#   1.3.1.1 If a value was already picked, increment by one
#   1.3.1.2 If the value reaches 32, repeat 1.3.1
#   1.3.2 Repeat step 1
# PLUS -> At the end of the system, print a report

has_collision = True
medium = False
transmitters = []


class Transmitter(Thread):
    def __init__(self, id, sensing):
        Thread.__init__(self)
        self.id = id
        self.sensing = sensing
        self.backoff_value = 0
        self.total_collisions = 0
        self.total_successful_transmissions = 0
        self.total_occupied = 0

    def run(self):
        global medium
        global has_collision

        while True:
            # Sensing
            print(
                f"T({self.id}) - Sensing... (has_collision = {has_collision} / medium = {medium})"
            )
            sleep(self.sensing)

            # Check if has collision
            if has_collision:
                self.total_collisions += 1
                print(f"T({self.id}) - Medium occupied - Collision")
                self.backoff()
            elif not medium:
                medium = True
                self.total_successful_transmissions += 1
                self.backoff_value = 0  # Reseting the backoff_value
                print(f"T({self.id}) - Transmitting")
                sleep(2)
                print(f"T({self.id}) - Transmission completed")
                medium = False
            else:
                self.total_occupied += 1
                print(f"T({self.id}) - Medium occupied - Someone is transmitting")
                self.backoff()

    def backoff(self):
        if self.backoff_value == 0 or self.backoff_value == 33:
            self.backoff_value = randint(2, 33)
        else:
            self.backoff_value += 1

        print(f"T({self.id}) - Waiting 2^{self.backoff_value} seconds...")
        sleep(self.backoff_value)


def collision_generator():
    global has_collision
    global transmitters

    while True:
        seen = set()
        for t in transmitters:
            time_sum = t.sensing + t.backoff_value
            if time_sum in seen and not has_collision:
                has_collision = True
                sleep(2)
                has_collision = False
                break
            else:
                has_collision = False
                seen.add(time_sum)


def generate_report(transmitters):
    total_transmissions = sum(
        (t.total_collisions + t.total_successful_transmissions + t.total_occupied)
        for t in transmitters
    )
    total_collisions = sum(t.total_collisions for t in transmitters)
    total_occupied = sum(t.total_occupied for t in transmitters)
    total_successful_transmissions = sum(
        t.total_successful_transmissions for t in transmitters
    )

    print("----------------------------- REPORT ---------------------------")
    print(f"Total transmissions: {total_transmissions}")
    print(f"Total collisions: {total_collisions}")
    print(f"Total of times waited because the medium was occupied: {total_occupied}")
    print(f"Total successful transmissions: {total_successful_transmissions}")
    print("---------------------------------------------------------------")


def signal_handler(signal, frame):
    print("\nSimulation stopped by user.")
    generate_report(transmitters)
    sys.exit(0)


def start():
    global transmitters

    collision = Thread(target=collision_generator)
    collision.start()

    num_transmitters = 4

    for i in range(1, num_transmitters + 1):
        transmitter = Transmitter(i, randint(1, 6))
        transmitters.append(transmitter)
        transmitter.start()

    signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    start()
