import time
import threading
import concurrent.futures


def do_something(seconds):
    print(f'Sleeping {seconds} second(s)...')
    time.sleep(seconds)
    return f'Done sleeping {seconds} second(s)...'


def new_way():
    start = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        secs = [5, 4, 3, 2, 1]
        results = executor.map(do_something, secs)

        for result in results:
            print(result)

    finish = time.perf_counter()

    print(f'Finished in {round(finish - start, 2)} second(s)')


def old_way():
    start = time.perf_counter()

    threads = []

    for _ in range(10):
        t = threading.Thread(target=do_something, args=[1.5])
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()

    finish = time.perf_counter()

    print(f'Finished in {round(finish-start, 2)} second(s)')


if __name__ == '__main__':
    # old_way()
    new_way()