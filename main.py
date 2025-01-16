import multiprocessing
from discord_bot import run_bot
from oauth_server import run_server
import redis

def start_bot():
    redis_client = redis.StrictRedis(host='127.0.0.1', port=7001, db=0, decode_responses=True)
    run_bot(redis_client)

def start_oauth_server():
    redis_client = redis.StrictRedis(host='127.0.0.1', port=7001, db=0, decode_responses=True)
    run_server(redis_client)

if __name__ == "__main__":
    # Set the start method to 'spawn' to avoid issues with pickling
    multiprocessing.set_start_method('spawn')

    # Create multiprocessing Process for bot and server
    bot_process = multiprocessing.Process(target=start_bot)
    oauth_server_process = multiprocessing.Process(target=start_oauth_server)

    # Start both processes
    bot_process.start()
    oauth_server_process.start()

    # Ensure both processes run concurrently
    bot_process.join()
    oauth_server_process.join()
