
node1:
	rm -r /tmp/db
	mkdir -p /tmp/db/node1
	mkdir -p /tmp/db/registry
	icegridnode --Ice.Config=node1.config

copy_binaries:
	rm -r /tmp/Downloader
	mkdir -p /tmp/Downloader
	cp Factory.py /tmp/Downloader
	cp downloads_scheduler.py /tmp/Downloader
	cp downloads_scheduler0.py /tmp/Downloader
	cp work_queue.py /tmp/Downloader
	cp youtubedl.py /tmp/Downloader
	cp downloader.ice /tmp/Downloader
	cp SyncTimer.py /tmp/Downloader
	cp Monitor.py /tmp/Downloader

	icepatch2calc /tmp/Downloader

registry: node.config
	@if ! [ -d /tmp/db/registry ]; then mkdir -p /tmp/db/registry; fi
	icegridregistry --Ice.Config=node.config


run-factory:
	python3 Factory.py --Ice.Config=factory.config

run-monitor: icestorm.config synctimer.config
	python3 Monitor.py --Ice.Config=subscriber.config

start:  icebox.config icestorm.config
	@if ! [ -d db ]; then mkdir db; fi
	icebox --Ice.Config=icebox.config
	sleep 3
	icestormadmin --Ice.Config=icestorm.config -e "create EventsTopic"

run-synctimer: icestorm.config synctimer.config
	python3 SyncTimer.py --Ice.Config=synctimer.config
