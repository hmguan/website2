
from hdfs import Client




def main():
   client = Client("http://hadoop100:50070")
   print(client)
   print(client.status("/",strict=True))

   print('-----------------------------')
   print(client.list("/user/stefan"))

if __name__ == "__main__":
    main()
