import datetime

class Log:
    def writetolog(self, message):
        log = open('log.txt', 'a')
        log.write(str(datetime.datetime.now()) + ': ' + message + '\n')
        log.close()
