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
                logging.exception("Error generated responding to < {} >.".format(_input))
                print("An error occurred - check the logs. Reinitializing GZ.")
                gz_chat = Chat(config)

    except (EOFError, KeyboardInterrupt):
        print("Exiting...")
