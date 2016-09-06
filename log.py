import datetime

class Log:
    def writetolog(self, message):
        log = open('log.txt', 'w')
        log.write(str(datetime.datetime.now()) + ': ' + message)
        log.close()

    def destroylog(self):
        log = open('log.txt', 'w')
        log.truncate()
        log.close()
