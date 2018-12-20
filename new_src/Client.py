#!/usr/bin/python3
''' '''
import sys
import cmd
import Ice

class Shell(cmd.Cmd):
    ''' '''
    Client = None
    prompt = 'Downloader > '

    def do_connect(self,line):
        '''Connect to proxy'''
        print(line)
        return

    def do_getListSongs(self,line):
        ''' '''
        return

    def do_add_download(self,line):
        ''' '''
        return

    def do_create_schedule(self,line):
        ''' '''
        return

    def do_exit(self,line):
        '''End program execution '''
        return True


class Client(Ice.Application):
    ''' Ice application cliente  '''
    def run(self,argv):
        Shell().cmdloop()
        return 0


if __name__ == '__main__':
    APP = Client()
    sys.exit(APP.main(sys.argv))
