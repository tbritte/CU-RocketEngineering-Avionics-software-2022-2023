import pandas as pd
import time

class Logger():
    def __init__(self):
        self.START_TIME = time.time()
    
    def log_data(file_name, data):
        with open(file_name, 'w', newline='') as log:
            log_writer = csv.writer(log, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            log_writer.writerow()