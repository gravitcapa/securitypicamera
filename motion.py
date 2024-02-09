from gpiozero import MotionSensor
print("app started")
pir = MotionSensor(4)
while True:
    pir.wait_for_motion()
    print("You moved")
    pir.wait_for_no_motion()
    print("reset")