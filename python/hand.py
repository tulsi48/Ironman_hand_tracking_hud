import cv2
import mediapipe as mp
import math
import socket
import json

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("ERROR: Webcam not accessible")
    exit()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

def distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def angle_between(p1, p2):
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    return math.degrees(math.atan2(dy, dx))

PINCH_NONE, PINCH_START, PINCH_HOLD = 0, 1, 2
pinch_state = PINCH_NONE

PINCH_THRESHOLD = 0.045
RELEASE_THRESHOLD = 0.060
STABLE_FRAMES = 5
pinch_counter = 0
release_counter = 0

cursor_x, cursor_y = 0.5, 0.5

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UNITY_ADDR = ("127.0.0.1", 5052)

print("Hand tracking + UDP started")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        hand = result.multi_hand_landmarks[0]
        lm = hand.landmark

        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        thumb = lm[4]
        index = lm[8]
        middle = lm[12]

        angle = angle_between(index, middle)
        tilt = middle.y - index.y      # 👈 NEW
        d = distance(thumb, index)

        if d < PINCH_THRESHOLD:
            pinch_counter += 1
            release_counter = 0
        elif d > RELEASE_THRESHOLD:
            release_counter += 1
            pinch_counter = 0
        else:
            pinch_counter = 0
            release_counter = 0

        if pinch_state == PINCH_NONE and pinch_counter >= STABLE_FRAMES:
            pinch_state = PINCH_START
        elif pinch_state in (PINCH_START, PINCH_HOLD) and pinch_counter >= STABLE_FRAMES:
            pinch_state = PINCH_HOLD
        elif pinch_state != PINCH_NONE and release_counter >= STABLE_FRAMES:
            pinch_state = PINCH_NONE

        if pinch_state == PINCH_HOLD:
            cursor_x, cursor_y = index.x, index.y

        data = {
            "x": cursor_x,
            "y": cursor_y,
            "z": d,
            "angle": angle,
            "tilt": tilt,
            "pinch": pinch_state == PINCH_HOLD
        }

        sock.sendto(json.dumps(data).encode(), UNITY_ADDR)
        print(data)

        h, w, _ = frame.shape
        cv2.circle(frame, (int(cursor_x*w), int(cursor_y*h)), 10, (0,255,255), -1)

    cv2.imshow("Hand Tracking", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
