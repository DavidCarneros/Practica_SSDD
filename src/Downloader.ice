module DownloaderSlice {


  sequence<string> SongsList;
  interface Downloader {
    ["amd"] string download(string url);
    SongsList getSongsList();
  };

  enum Status {Pending, InProgress, Done, Error};
    struct ClipData {
      string URL;
      string clipName;
      string endpointIP;
      Status status;
    };

  interface ProgressTopic {

    void notify(ClipData clipData);
  };

  interface SyncTopic {
    void requestSync();
    void notify(SongsList songsList);
  };

  interface DownloaderFactory {
    Downloader* make(string name);
  };


};
