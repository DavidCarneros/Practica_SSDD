
all:

clean:
	$(RM) *~
	$(RM) -r db

registry: node1.config
	@if ! [ -d /tmp/db/registry ]; then mkdir -p /tmp/db/registry; fi
	icegridregistry --Ice.Config=node1.config

start:  icebox.config icestorm.config
	@if ! [ -d db ]; then mkdir db; fi
	icebox --Ice.Config=icebox.config
	sleep 3
	icestormadmin --Ice.Config=icestorm.config -e "create EventsTopic"

stop: icestorm.config
	icestormadmin --Ice.Config=icestorm.config -e "destroy EventsTopic"
	killall icebox

run-synctimer: icestorm.config synctimer.config
	python3 SyncTimer.py --Ice.Config=synctimer.config

run-monitorSync: icestorm.config synctimer.config
	python3 monitorSyncTopic.py --Ice.Config=subscriber.config

run-server: icestorm.config server.config
	python3 Server.py --Ice.Config=server.config

run-server1: icestorm.config server.config
	python3 Server_1adapter.py --Ice.Config=server.config

run-publisher1:  icestorm.config server1.config
	python3 Server.py --Ice.Config=server1.config

run-publisher2: icestorm.config server2.config
	python3 Server.py --Ice.Config=server2.config

client1: client.config
	python3 Client.py --Ice.Config=client.config "printer1 -t -e 1.1 @ PrinterAdapter1"

client2: client.config
	python3 Client.py --Ice.Config=client.config "printer2 -t -e 1.1 @ PrinterAdapter2"
