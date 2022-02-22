import json
import time

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.utils import platform


# TODO:
# - Deploy on android
# ----- MVP ----------
# - Remove a track
# - Modify a track
# - Add parameter page (set what file is used for the DB)
# - Sort tracks by record
# - Sort tracks by any attribute
# - Filter tracks by any attribute
# - List of tracks


class RecordDB():
    def __init__(self, db_file):
        self.db_file = db_file
        self.track_list = self.load()
        for t in self.track_list:
            t["comment"] = ''

    def load(self):
        with open(self.db_file) as f:
            track_list = json.load(f)["tracks_db"]
        return track_list

    def print_db(self):
        for track in self.track_list:
            print(track)

    def add(self, track):
        # Set new id (actually epoch time of creation)
        raw_time = int(time.time())
        track["id"] = raw_time
        # Set time of change
        track["lastChange"] = raw_time
        # Add track
        self.track_list.append(track)
        # Save db in file
        self.save()

    def save(self):
        db_dict = {"tracks_db": self.track_list}
        with open(self.db_file, "w") as f:
            json.dump(db_dict, f)


class MainPage(Screen):

    def __init__(self, db, **kwargs):
        super(MainPage, self).__init__()
        self.db = db
        self.displayed_ids = []
        self.update_list()

    def update_list(self):
        # Add new items
        for track in self.db.track_list:
            if track["id"] not in self.displayed_ids:
                style_str = ', '.join(track["style"])
                self.ids.track_container.add_widget(
                    TwoLineListItem(
                        text=f"{track['record']} - {track['num']}. {track['track']}",
                        secondary_text=f"{track['artist']}, {style_str}, BPM={track['bpm']}"
                    )
                )
                self.displayed_ids.append(track["id"])

        # Sort


class AddTrackPage(Screen):
    confirm_dialog = None

    def __init__(self, app, **kwargs):
        super(AddTrackPage, self).__init__()
        self.app = app

    def add_track(self):
        """ Called when pushing the 'ADD' button. 
            Ask for confirmation and sends the new track to the main app to be
            added.
        """
        # Create list of style, adding only non-empty styles
        style_list = []
        if self.ids.style1.text != '':
            style_list.append(self.ids.style1.text)
        if self.ids.style2.text != '':
            style_list.append(self.ids.style2.text)
        if self.ids.style3.text != '':
            style_list.append(self.ids.style3.text)
        # Create new track dictionary entry
        new_track = {
            "record": self.ids.record_name.text,
            "num": self.ids.track_num.text,
            "track": self.ids.track_name.text,
            "artist": self.ids.artist.text,
            "style": style_list,
            "bpm": self.ids.bpm.text,
            "comment": self.ids.comment.text
        }
        # Create the string to display in the confirm dialog
        style_str = ', '.join(new_track["style"])
        track_str = "Record: {}\nTrack #: {}\nTrack name:{}\nArtist: {}\nStyle: {}\nBPM: {}\nComment: {}".format(
            new_track["record"], new_track["num"], new_track["track"], 
            new_track["artist"], style_str, new_track["bpm"], 
            new_track["comment"]
        )
        # Create and open dialog
        self.confirm_dialog = MDDialog(
            title="Confirm adding this track ?",
            text=track_str,
            buttons=[
                MDFlatButton(
                    text="Confirm",
                    theme_text_color="Custom",
                    text_color=[1, 0.77, 0, 1],
                    on_release=lambda *args: self.send_new_track(
                                                    new_track, *args)
                ),
                MDFlatButton(
                    text="Cancel",
                    on_release=self.close_dialog
                )
            ]
        )
        self.confirm_dialog.open()

    def close_dialog(self, *args):
        self.confirm_dialog.dismiss()

    def send_new_track(self, new_track, *args):
        self.confirm_dialog.dismiss()
        self.app.add_new_track(new_track)



class RecordDBApp(MDApp):
    data = {
        'Add Record': 'album'
    }

    def __init__(self):
        super(RecordDBApp, self).__init__()
        # DB
        self.db = RecordDB("Records.json")
        self.db.print_db()
        # Screen manager and pages
        self.sm = ScreenManager(transition=NoTransition())
        # Pages
        self.main_page = None
        self.add_track_page = None

    def build(self):
        Builder.load_file("main_page.kv")
        return self.sm

    def on_start(self):
        self.main_page = MainPage(self.db, name="main_page")
        self.add_track_page = AddTrackPage(self, name="add_track_page")
        self.sm.add_widget(self.main_page)
        self.sm.add_widget(self.add_track_page)
        self.sm.current = "main_page"

    def callback(self, instance):
        # Main page: add record button -> go to add record page
        if instance.icon == "album":
            self.sm.current = "add_track_page"
        # Add record page: back button -> go to main page
        if instance.icon == "arrow-left":
            self.sm.current = "main_page"

    def add_new_track(self, new_track):
        # Add track to db
        self.db.add(new_track)
        # Update main page list
        self.main_page.update_list()
        # Go to main page
        self.sm.current = "main_page"


if __name__ == "__main__":
    # add the following just under the imports
    if platform == "android":
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

    RecordDBApp().run()