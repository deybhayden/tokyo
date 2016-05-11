import logging

from godzillops import Chat


def main(config):
    gz_chat = Chat(config)
    try:
        _input = ""
        while True:
            _input = input("> ")
            responses = gz_chat.respond(_input)
            try:
                for response in responses:
                    if isinstance(response, str):
                        print(response)
            except:
                # clear any action started
                gz_chat.cancel()
                logging.exception("Error generated responding to < {} >.".format(_input))
                print("An error occurred - check the logs.")

    except (EOFError, KeyboardInterrupt):
        print("Exiting...")
