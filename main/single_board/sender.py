import cv2
import time
from hand_tracking_module import HandDetector
from client import connect_to_server, send_object_message
from dataclasses import dataclass
import collections
import matplotlib.pyplot as plt

# SETTINGS
SEND_TIME_INFO = True
COLLECT_FPS_STAT = True
MEASURE_TIME = True


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
    if COLLECT_FPS_STAT:
        fps_val = collections.deque(maxlen=10000)

    if MEASURE_TIME:
        time_val = collections.deque(maxlen=10000)

    prev_time = 0
    curr_time = 0
    cap = cv2.VideoCapture(0)
    detector = HandDetector(max_hands=1, detection_con=0.7)

    client_socket = connect_to_server('RoboPies')

    # Actions specific variables
    player_action = ''
    was_shot = False
    was_changed = False

    while True:
        success, img = cap.read()
        img_height, img_width, _ = img.shape
        img = cv2.flip(img, 1)
        if MEASURE_TIME:
            start = time.perf_counter_ns()
        img = detector.find_hands(img)
        landmark_positions, bbox = detector.find_position_and_bbox(img, draw=True)
        if MEASURE_TIME:
            stop = round((time.perf_counter_ns() - start)/1_000_000, 2)
            time_val.append(stop)
        img = HandDetector.draw_grid(img, img_height, img_width)

        interpreted_movement = ''

        if len(landmark_positions) != 0:
            # Check mode - clenched fist = interpret gestures, opened hand = ignore gestures
            fingers = detector.fingers_up()
            if sum(fingers) != 5:
                # Interpret gestures
                # Movement
                interpreted_movement = interpret_hand_movement(bbox, img_width, img_height)

                # Actions
                # Pointing finger up - one shot
                if fingers[1] == 1 and not was_shot:
                    player_action = 'shoot'
                    was_shot = True

                # Middle finger up - weapon change
                elif fingers[2] == 1 and not was_changed:
                    player_action = 'change'
                    was_changed = True

                # Reset the action
                else:
                    player_action = ''
                    if fingers[1] != 1:
                        was_shot = False
                    if fingers[2] != 1:
                        was_changed = False

            # Sending orders to the server
            message_to_send = {'move': interpreted_movement, 'action': player_action}
            if SEND_TIME_INFO:
                message_to_send['time'] = time.time_ns()
            send_object_message(client_socket, message_to_send)

        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        if COLLECT_FPS_STAT:
            fps_val.append(fps)
        prev_time = curr_time
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), thickness=3)

        cv2.imshow('Frame', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            if COLLECT_FPS_STAT:
                print(f'Average FPS: {round(sum(fps_val)/len(fps_val), 2)}')
                plt.plot(fps_val)
                plt.ylabel('FPS')
                plt.show()
                plt.hist(fps_val)
                plt.xlabel('FPS')
                plt.show()
            if MEASURE_TIME:
                print(f'Average time the neural network takes to process 1 frame: {round(sum(time_val)/len(time_val), 2)}')
                plt.plot(time_val)
                plt.ylabel('Time in ms')
                plt.show()
                plt.hist(time_val)
                plt.xlabel('Time in ms')
                plt.show()
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
