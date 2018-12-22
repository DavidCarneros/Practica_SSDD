
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
	cp work_queue.py /tmp/Downloader
	cp youtubedl.py /tmp/Downloader
	cp downloader.ice /tmp/Downloader
	cp SyncTimer.py /tmp/Downloader

	icepatch2calc /tmp/Downloader
