# Implement the default Matplotlib key bindings.
import time

from genius_bot_v2 import App
from youtube_download import YouTubeDownloader


class Controller:
    app = None
    ytd = None
    def __init__(self):
        print("Initialized")
        # self.num_cores = multiprocessing.cpu_count()
        self.num_cores = 2
        self.app = App()
        print('Now we can continue running code while mainloop runs!')
        self.ytd = YouTubeDownloader()

    def setYouTubeDownloader(self):
        start = time.process_time()
        # youtube_connector.open_file()
        list = self.app.get_links()
        self.ytd.append_link('https://www.youtube.com/watch?v=Xq-knHXSKYY')
        # youtube_connector.get_channel_videos('UCXcnHuosOLaKOGU0qQoYzfA')
        print("Youtube Links: ", self.ytd.get_link())
        print("Length Youtube Links: ", len(self.ytd.get_link()))
        # youtube_connector.download_hd_videos_parallel()
        self.ytd.download_hd_videos()
        print("Executed Seconds: ", (time.process_time() - start))
        # youtube_connector.download_audio()

main()
