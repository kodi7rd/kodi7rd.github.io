import xbmc, xbmcgui
from threading import Thread
from modules.MDbList import MDbListAPI
import json

logger = xbmc.log
empty_ratings = {
    "metascore": "",
    "tomatoMeter": "",
    "tomatoUserMeter": "",
    "tomatoImage": "",
    "imdbRating": "",
    "popularRating": "",
    "tmdbRating": "",
}


class RatingsService(xbmc.Monitor):
    def __init__(self):
        xbmc.Monitor.__init__(self)
        self.mdblist_api = MDbListAPI
        self.last_set_imdb_id = None
        self.window = xbmcgui.Window
        self.get_window_id = xbmcgui.getCurrentWindowId
        self.get_infolabel = xbmc.getInfoLabel
        self.get_visibility = xbmc.getCondVisibility

    def onNotification(self, sender, method, data):
        if sender == "xbmc":
            if method in ("GUI.OnScreensaverActivated", "System.OnSleep"):
                self.window(self.get_window_id()).setProperty("pause_services", "true")
                logger("###FENtastic: Device is Asleep, PAUSING Ratings Service", 1)
            elif method in ("GUI.OnScreensaverDeactivated", "System.OnWake"):
                self.window(self.get_window_id()).clearProperty("pause_services")
                logger("###FENtastic: Device is Awake, RESUMING Ratings Service", 1)

    def listitem_monitor(self):
        while not self.abortRequested():
            if (
                self.window(self.get_window_id()).getProperty("pause_services")
                == "true"
            ):
                self.waitForAbort(2)
                continue
            if xbmc.getSkinDir() != "skin.fentastic":
                self.waitForAbort(15)
                continue
            api_key = self.get_infolabel("Skin.String(mdblist_api_key)")

            # KODI-RD-IL
            if api_key == 'use_my_custom_list':
                MDBLIST_API_KEYS = {
                    "darksubsil1-api_key": "csq5pq5vhf4r1snagff7qukcu",
                    "darksubsil2-api_key": "m1azvroj6xgt6x05urkmd9m9u",
                    "darksubsil3-api_key": "dbm160enk1t0shknn3r2bh003",
                    "darksubsil4-api_key": "n5p3p7mvdb9tmdq49mrp59tdu",
                    "darksubsil5-api_key": "5608d5y1dkhogghe4ly4nkjr9",
                    "darksubsil6-api_key": "blgzz5pfmfb973mgy1lp4n3s8",
                    "darksubsil7-api_key": "9wcsvxj6gjv7io6p9pcqfeqbw",
                    "darksubsil8-api_key": "udrqs9ni2gdf6qvtnytnodrxt",
                    "darksubsil9-api_key": "j49h9i7aohe7g4pdpl4o5rp38",
                    "darksubsil10-api_key": "kq4ur9et7hceu2h0e00l2hw0j"
                }
                import random
                api_key = random.choice(list(MDBLIST_API_KEYS.values()))
            ############

            if not api_key:
                self.waitForAbort(10)
                continue
            if not self.get_visibility(
                "Window.IsVisible(videos) | Window.IsVisible(home) | Window.IsVisible(11121)"
            ):
                self.waitForAbort(2)
                continue
            if self.get_visibility("Container.Scrolling"):
                self.waitForAbort(0.2)
                continue
            if self.get_visibility("Skin.HasSetting(TrailerPlaying)"):
                self.waitForAbort(3)
                while xbmc.Player().isPlaying():
                    if self.waitForAbort(0.5):
                        break
                xbmc.executebuiltin("Skin.ToggleSetting(TrailerPlaying)")
                self.waitForAbort(0.2)
                continue
            imdb_id = self.get_infolabel("ListItem.IMDBNumber")
            set_property = self.window(self.get_window_id()).setProperty
            get_property = self.window(self.get_window_id()).getProperty
            cached_ratings = get_property(f"fentastic.cachedRatings.{imdb_id}")
            if not imdb_id or not imdb_id.startswith("tt"):
                for k, v in empty_ratings.items():
                    set_property("fentastic.%s" % k, v)
                self.last_set_imdb_id = None
                self.waitForAbort(0.2)
                continue
            if imdb_id == self.last_set_imdb_id:
                self.waitForAbort(0.2)
                continue
            if cached_ratings:
                result = json.loads(cached_ratings)
                for k, v in result.items():
                    set_property("fentastic.%s" % k, v)
                self.last_set_imdb_id = imdb_id
                self.waitForAbort(0.2)
                continue
            Thread(target=self.set_ratings, args=(api_key, imdb_id)).start()
            self.waitForAbort(0.2)

    def set_ratings(self, api_key, imdb_id):
        set_property = self.window(self.get_window_id()).setProperty
        result = self.mdblist_api().fetch_info({"imdb_id": imdb_id}, api_key)
        if result:
            set_property(f"fentastic.cachedRatings.{imdb_id}", json.dumps(result))
            for k, v in result.items():
                set_property("fentastic.%s" % k, v)


logger("###FENtastic: Ratings Service Started", 1)
RatingsService().listitem_monitor()
logger("###FENtastic: RatingsService Finished", 1)
