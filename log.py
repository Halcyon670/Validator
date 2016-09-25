import datetime

class Log:
    def writetolog(self, message):
        log = open('log.txt', 'a')
        log.write('\n' + str(datetime.datetime.now()) + ': ' + message)
        log.close()