import threading
import time

# Hàm kiểm tra thời gian và ngắt hàm nếu cần
def timeout_function(func, timeout):
    result = None
    exception = None

    def target():
        nonlocal result, exception
        try:
            result = func()
        except Exception as e:
            exception = e

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        # Nếu thread vẫn còn sống sau thời gian quy định, ngắt nó
        raise TimeoutError("Hàm đã chạy quá thời gian quy định")
    elif exception:
        # Nếu có exception trong quá trình chạy hàm, ném lại exception
        raise exception
    else:
        return result

def my_function():
    time.sleep(10)  # Ví dụ: Đợi trong 10 giây

try:
    result = timeout_function(my_function, 5)  # Chạy hàm trong tối đa 5 giây
    print("Kết quả:", result)
except TimeoutError:
    print("Hàm đã bị ngắt do vượt quá thời gian")
