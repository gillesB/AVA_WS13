from LocalKnot import LocalKnot

__author__ = 'me'

if __name__ == '__main__':
    for num in range(8):
        l = LocalKnot(num)
        l.start()
        l.join()