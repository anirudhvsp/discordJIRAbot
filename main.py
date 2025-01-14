import multiprocessing
from discord_bot import run_bot
from oauth_server import run_server

def start_bot(user_tokens):
    run_bot(user_tokens)

def start_oauth_server(user_tokens):
    run_server(user_tokens)

if __name__ == "__main__":
    # Create a multiprocessing Manager to share the user_tokens dictionary
    with multiprocessing.Manager() as manager:
        # Create a shared dictionary for user tokens
        user_tokens = manager.dict()

        # Create multiprocessing Process for bot and server
        bot_process = multiprocessing.Process(target=start_bot, args=(user_tokens,))
        oauth_server_process = multiprocessing.Process(target=start_oauth_server, args=(user_tokens,))

        # Start both processes
        bot_process.start()
        oauth_server_process.start()

        # Ensure both processes run concurrently
        bot_process.join()
        oauth_server_process.join()
