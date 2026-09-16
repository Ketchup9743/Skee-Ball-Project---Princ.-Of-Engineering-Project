# pyright: reportMissingImports=false, reportUndefinedVariable=false
from microbit import *


SENSOR_1 = pin0
SENSOR_1_SCORE = 10

SENSOR_2 = pin1
SENSOR_2_SCORE = 25

SENSOR_3 = pin2
SENSOR_3_SCORE = 50

SENSORS = [
	(SENSOR_1, SENSOR_1_SCORE),
	(SENSOR_2, SENSOR_2_SCORE),
	(SENSOR_3, SENSOR_3_SCORE),
]

MOTION_COOLDOWN_MS = 1000


score = 0
last_motion_time = [0] * len(SENSORS)
sensor_was_active = [False] * len(SENSORS)


def show_score():
	display.show(str(score), wait=False)


def reset_game():
	global score
	score = 0
	for index in range(len(SENSORS)):
		sensor_was_active[index] = False
		last_motion_time[index] = running_time()
	print("RESET")
	show_score()


reset_game()

while True:
	now = running_time()

	for index, (sensor_pin, points) in enumerate(SENSORS):
		motion_detected = sensor_pin.read_digital() == 1
		new_motion = motion_detected and not sensor_was_active[index]
		cooldown_finished = now - last_motion_time[index] >= MOTION_COOLDOWN_MS

		if new_motion and cooldown_finished:
			score += points
			last_motion_time[index] = now
			print("SCORE_EVENT,{},{}".format(index + 1, points))
			show_score()

		sensor_was_active[index] = motion_detected

	if button_a.was_pressed():
		reset_game()
	elif button_b.was_pressed():
		show_score()

	sleep(20)
