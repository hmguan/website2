
#from hdfs import Client

from db.db_blackbox import blackbox_manager
from datetime import datetime

def main():



   blackbox_manager.remove_temps(5)

if __name__ == "__main__":
    main()
