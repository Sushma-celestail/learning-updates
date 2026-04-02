import logging

logging.basicConfig(
    filename='app.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def divide(a,b):
    try:
        return a/b
    except Exception as e:
        logging.error("something failed %s",str(e))
print(divide(10,30))


