import threading
import time
test = 1
def function_that_downloads():
    global test
    while True:
        test += 1
        time.sleep(1)
    
def my_inline_function():
    download_thread = threading.Thread(target=function_that_downloads, name="Downloader")
    download_thread.start()
    print("hello")
    time.sleep(10)
    print(test)
    
my_inline_function()