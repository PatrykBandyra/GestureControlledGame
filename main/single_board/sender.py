import cv2
import time
from hand_tracking_module import HandDetector
from client import connect_to_server, send_object_message
from dataclasses import dataclass


@dataclass
class MovementField:
    x: float
    y: float
    width: float
    height: float
    movement: str

    def point_in_rect(self, point):
        p_x, p_y = point
        if self.x < p_x < self.x + self.width:
            if self.y < p_y < self.y + self.height:
                return True
        return False


def interpret_hand_movement(bbox, img_width, img_height):
    movement_fields = generate_movement_fields(img_width, img_height)

    # Movement
    x_min, y_min, x_max, y_max = bbox
    hand_center = (x_max - x_min) // 2 + x_min, (y_max - y_min) // 2 + y_min

    interpreted_movement = ''
    for mf in movement_fields:
        if mf.point_in_rect(hand_center):
            interpreted_movement = mf.movement
            break

    return interpreted_movement


def generate_movement_fields(img_width, img_height):
    return [MovementField(0, 0, img_width / 3, img_height / 3, 'up-left'),
            MovementField(img_width / 3, 0, img_width / 3, img_height / 3, 'up'),
            MovementField((img_width / 3) * 2, 0, img_width / 3, img_height / 3, 'up-right'),
            MovementField(0, img_height / 3, img_width / 3, img_height / 3, 'left'),
            MovementField(img_width / 3, img_height / 3, img_width / 3, img_height / 3, 'stand'),
            MovementField((img_width / 3) * 2, img_height / 3, img_width / 3, img_height / 3, 'right'),
            MovementField(0, (img_height / 3) * 2, img_width / 3, img_height / 3, 'down-left'),
            MovementField(img_width / 3, (img_height / 3) * 2, img_width / 3, img_height / 3, 'down'),
            MovementField((img_width / 3) * 2, (img_height / 3) * 2, img_width / 3, img_height / 3, 'down-right')]


def main():
    prev_time = 0
    curr_time = 0
    cap = cv2.VideoCapture(0)
    detector = HandDetector(max_hands=1, detection_con=0.7)

    client_socket = connect_to_server('RoboPies')

    player_action = ''

    while True:
        success, img = cap.read()
        img_height, img_width, _ = img.shape
        img = cv2.flip(img, 1)
        img = detector.find_hands(img)
        landmark_positions, bbox = detector.find_position_and_bbox(img, draw=True)
        img = HandDetector.draw_grid(img, img_height, img_width)
        if len(landmark_positions) != 0:
            # Check mode - clenched fist = interpret gestures, opened hand = ignore gestures
            fingers = detector.fingers_up()
            if sum(fingers) != 5:
                # Interpret gestures
                # Movement
                interpreted_movement = interpret_hand_movement(bbox, img_width, img_height)
                print(interpreted_movement)

                # Actions
                # Thumb up - one shot
                if fingers[0] == 1 and player_action != 'shoot':    ### bug????
                    player_action = 'shoot'

                ### elif ... for more actions

                # If no action - reset
                else:
                    player_action = ''
            print(player_action)

            # 'move': '...', 'action: '...', 'time': '...''
            send_object_message(client_socket, {'landmarks': landmark_positions[4], 'time': time.time()})

        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), thickness=3)

        ########################################################################################################################
        # Delete if board without screen and keyboard
        cv2.imshow('Frame', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


########################################################################################################################

if __name__ == '__main__':
    main()
