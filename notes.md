## Motion sensor scoring

This project expects Adafruit B2612 motion sensors with their signal output connected to micro:bit GPIO pins. Connect the sensor power and ground according to the sensor breakout's labeling, and connect each signal wire to the matching pin in `game.py`.

Set each sensor pin and its score in `game.py`:

```python
SENSOR_1 = pin0
SENSOR_1_SCORE = 10

SENSOR_2 = pin1
SENSOR_2_SCORE = 25

SENSORS = [
	(SENSOR_1, SENSOR_1_SCORE),
	(SENSOR_2, SENSOR_2_SCORE),
]
```

The loop uses the score paired with whichever sensor detects motion. Motion is counted when a sensor changes from inactive to active. `MOTION_COOLDOWN_MS` prevents one motion event from being counted again too quickly.

- Button A resets the score.
- Button B displays the current score.
