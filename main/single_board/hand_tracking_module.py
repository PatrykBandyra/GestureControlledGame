import cv2
import mediapipe as mp


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

            x_min, x_max = min(x_list), max(x_list)
            y_min, y_max = min(y_list), max(y_list)
            bbox = x_min, y_min, x_max, y_max

            if draw:
                # hand
                cv2.rectangle(img, (bbox[0]-20, bbox[1]-20), (bbox[2]+20, bbox[3]+20), (0, 255, 0), 2)
                cv2.circle(img, ((x_max-x_min)//2+x_min, (y_max-y_min)//2+y_min), 30, (255, 0, 0), cv2.FILLED)

        return self.landmark_positions, bbox

    def fingers_up(self):
        fingers = []

        # thumb
        if self.landmark_positions[self.tip_ids[0]][1] < self.landmark_positions[self.tip_ids[0] - 1][1]:
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

    @staticmethod
    def draw_grid(img, img_height, img_width):

        # Vertical lines
        cv2.line(img, (img_width//3, 0), (img_width//3, img_height), (0, 0, 255), 1)
        cv2.line(img, ((img_width//3)*2, 0), ((img_width//3)*2, img_height), (0, 0, 255), 1)

        # Horizontal lines
        cv2.line(img, (0, img_height//3), (img_width, img_height//3), (0, 0, 255), 1)
        cv2.line(img, (0, (img_height//3)*2), (img_width, (img_height//3)*2), (0, 0, 255), 1)

        return img
