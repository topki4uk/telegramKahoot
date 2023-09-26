import time
import threading


def start(n, resp):
    t_start = time.time()
    current_t = time.time()

    while int(current_t - t_start) < n:
        current_t = time.time()

    resp.append(True)


def main():
    lst = []
    thread = threading.Thread(target=start, args=(4, lst))
    thread.start()

    for i in range(10):
        print('joy')
        time.sleep(1)

        if lst:
            print('ok')
            break


if __name__ == '__main__':
    main()
