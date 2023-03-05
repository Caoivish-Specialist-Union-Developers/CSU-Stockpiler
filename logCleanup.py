import datetime
import logging
import os
import time

def logSetupCleanup():
    if not os.path.exists("./logs"):
        os.makedirs("./logs")

    logfilename = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    logfilename = "logs/Stockpiler-log-" + logfilename + ".txt"
    logging.basicConfig(
        filename=logfilename,
        format="%(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    print("Log file created: " + logfilename)
    logging.info(str(datetime.datetime.now()) + " Log Created")


    def get_file_directory(file):
        return os.path.dirname(os.path.abspath(file))


    # Log cleanup of any contents of logs folder older than 7 days
    now = time.time()
    cutoff = now - (7 * 86400)
    files = os.listdir(os.path.join(get_file_directory(__file__), "logs"))
    file_path = os.path.join(get_file_directory(__file__), "logs/")
    for xfile in files:
        if os.path.isfile(str(file_path) + xfile):
            t = os.stat(str(file_path) + xfile)
            c = t.st_ctime
            if c < cutoff:
                os.remove(str(file_path) + xfile)
                logging.info(
                    str(datetime.datetime.now()) + " " + str(xfile) + " log file deleted"
                )
