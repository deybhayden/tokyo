from godzillops.godzillops import Chat


def main(config):
    gz_chat = Chat(config)
    try:
        _input = ""
        while True:
            _input = input("> ")

            if _input:
                responses = gz_chat.respond(_input)
                for response in responses:
                    print(response)

    except (EOFError, KeyboardInterrupt):
        print("Exiting...")
