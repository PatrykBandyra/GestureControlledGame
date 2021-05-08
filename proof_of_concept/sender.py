import cv2
import time
from hand_tracking_module import HandDetector
from client import connect_to_server, send_string_message, send_object_message


def main():
    prev_time = 0
    curr_time = 0
    cap = cv2.VideoCapture(0)
    detector = HandDetector(max_hands=1, detection_con=0.7)

    client_socket = connect_to_server('RoboPies')

    while True:
        success, img = cap.read()
        img = detector.find_hands(img)
        landmark_positions = detector.find_position(img, draw=False)
        if len(landmark_positions) != 0:
            print(landmark_positions[4])
            # send_string_message(client_socket, str(landmark_positions[4]))
            send_object_message(client_socket, {'landmarks': landmark_positions[4], 'time': time.time()})

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