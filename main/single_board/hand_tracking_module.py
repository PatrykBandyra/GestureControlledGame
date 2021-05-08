import cv2
import mediapipe as mp
import time
import math


"""
TODO: Get rid of necessary methods.
"""


class HandDetector:
    def __init__(self, mode=False, max_hands=2, detection_con=0.5, track_con=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(self.mode, self.max_hands, self.detection_con, self.track_con)
        self.mp_draw = mp.solutions.drawing_utils

        self.tip_ids = [4, 8, 12, 16, 20]

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        return img

    def find_position(self, img, hand_num=0, draw=True):
        self.landmark_positions = []
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_num]

            for id, landmark in enumerate(my_hand.landmark):
                height, width, channels = img.shape
                cx, cy = int(landmark.x * width), int(landmark.y * height)
                self.landmark_positions.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        return self.landmark_positions

    def find_position_and_bbox(self, img, hand_num=0, draw=True):
        x_list = []
        y_list = []
        bbox = []
        self.landmark_positions = []
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_num]

            for id, landmark in enumerate(my_hand.landmark):
                height, width, channels = img.shape
                cx, cy = int(landmark.x * width), int(landmark.y * height)
                x_list.append(cx)
                y_list.append(cy)
                self.landmark_positions.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

            x_min, x_max = min(x_list), max(x_list)
            y_min, y_max = min(y_list), max(y_list)
            bbox = x_min, y_min, x_max, y_max

            if draw:
                cv2.rectangle(img, (bbox[0]-20, bbox[1]-20), (bbox[2]+20, bbox[3]+20), (0, 255, 0), 2)

        return self.landmark_positions, bbox

    def fingers_up(self):
        fingers = []

        # thumb
        if self.landmark_positions[self.tip_ids[0]][1] > self.landmark_positions[self.tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # other fingers
        for id in range(1, len(self.tip_ids)):
            if self.landmark_positions[self.tip_ids[id]][2] < self.landmark_positions[self.tip_ids[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def find_distance(self, p1, p2, img, draw=True):

        x1, y1 = self.landmark_positions[p1][1:]
        x2, y2 = self.landmark_positions[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]


def main():
    prev_time = 0
    curr_time = 0
    cap = cv2.VideoCapture(0)
    detector = HandDetector()

    while True:
        success, img = cap.read()
        img = detector.find_hands(img)
        landmark_positions = detector.find_position(img, draw=False)
        if len(landmark_positions) != 0:
            print(landmark_positions[4])

        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), thickness=3)

        cv2.imshow('Frame', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()