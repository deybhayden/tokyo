from godzillops.godzillops import Chat


def main(config, quit="quit"):
    gz_chat = Chat(config)
    try:
        _input = ""
        while _input != quit:
            _input = quit
            try:
                _input = input("> ")
            except EOFError:
                print(_input)

            if _input:
                responses = gz_chat.respond(_input)
                for response in responses:
                    print(response)

    except KeyboardInterrupt:
        print(quit)
