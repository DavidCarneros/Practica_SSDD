
all:

clean:
	$(RM) *~
	$(RM) -r db

registry: ./config/node1.config
	@if ! [ -d /tmp/db/registry ]; then mkdir -p /tmp/db/registry; fi
	icegridregistry --Ice.Config=./config/node1.config

start:  ./config/icebox.config ./config/icestorm.config
	@if ! [ -d ./config/db ]; then mkdir ./config/db; fi
	icebox --Ice.Config=./config/icebox.config
	sleep 3
	icestormadmin --Ice.Config=./config/icestorm.config -e "create EventsTopic"

stop: ./config/icestorm.config
	icestormadmin --Ice.Config=./config/icestorm.config -e "destroy EventsTopic"
	killall icebox

run-synctimer: ./config/icestorm.config ./config/synctimer.config
	python3 SyncTimer.py --Ice.Config=./config/synctimer.config

run-monitor: ./config/icestorm.config ./config/synctimer.config
	python3 monitor.py --Ice.Config=./config/subscriber.config

run-server: ./config/icestorm.config ./config/server.config
	python3 Server.py --Ice.Config=./config/server1.config

clientSubs: ./config/client.config
	python3 Client_Subs.py "DownloaderServer1 -t -e 1.1 @ DownloaderAdapter1" --Ice.Config=./config/client.config

clientDesc: ./config/client.config
	python3 Client_desc.py "DownloaderServer1 -t -e 1.1 @ DownloaderAdapter1" --Ice.Config=./config/client.config

client: ./config/client.config
	python3 Client.py "DownloaderServer1 -t -e 1.1 @ DownloaderAdapter1" --Ice.Config=./config/client.config

clientIU: ./config/client.config
	python3 ClientInterfaz.py "DownloaderServer1 -t -e 1.1 @ DownloaderAdapter1" --Ice.Config=./config/client.config

ClientInterfaz: ./config/client.config
	python3 MainWindow.py "DownloaderServer1 -t -e 1.1 @ DownloaderAdapter1" --Ice.Config=./config/client.config
