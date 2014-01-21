from AVA4.BlackJackKnot import BlackJackKnot


__author__ = 'me'

if __name__ == '__main__':
    filename = './json_data'

    for num in range(8):
        l = BlackJackKnot(num, filename, 5)
        if num == 0:
            l.token = True
        l.start()
