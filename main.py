import json

from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.list import TwoLineListItem

class Main(MDApp):
    data = {
        'Add Record': 'album'
    }

    def build(self):
        return Builder.load_file("main_page.kv")

    def on_start(self):
        with open("Records.json") as f:
            self.tracks_list = json.load(f)["record_collection"]["records"]

        for track in self.tracks_list:
            track = track["record"]
            self.root.ids.track_container.add_widget(
                TwoLineListItem(
                    text=f"{track['record']} - {track['num']}. {track['track']}",
                    secondary_text=f"{track['artist']}, {track['style']}, BPM={track['bpm']}"
                )
            )

    def callback(self, instance):
        if instance.icon == "album":
            return


Main().run()