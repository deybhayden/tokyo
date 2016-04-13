from godzillops.godzillops import Chat

gz_chat = Chat()

def main(quit="quit"):
    try:
        _input = ""
        while _input != quit:
            _input = quit
            try:
                _input = input("> ")
            except EOFError:
                print(_input)

            if _input:
                print(gz_chat.respond(_input))
    except KeyboardInterrupt:
        print(quit)
