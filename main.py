import json
import time

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.utils import platform

# if platform == "android":
#     from android.permissions import request_permissions, Permission
#     request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])


# TODO:
# - Deploy on android
# ----- MVP ----------
# - Duplicate and modify track
# - Regrouper par record
# - Sort tracks by record
# - Sort tracks by any attribute
# - Filter tracks by any attribute
# - List of tracks
# - Transitions between tracks
# - Add parameter page (set what file is used for the DB)


class RecordDB():
    def __init__(self, db_file):
        self.db_file = db_file
        self.track_dict = self.load()

    def load(self):
        with open(self.db_file) as f:
            track_dict = json.load(f)["tracks_db"]
        return track_dict

    def print_db(self):
        for id, track in self.track_dict.items():
            print(id, track)

    def add(self, track, track_id=None):
        raw_time = int(time.time())
        # Set new id (actually epoch time of creation)
        if track_id is None:
            track["id"] = raw_time
        else:
            track["id"] = track_id
        # Set time of change
        track["lastChange"] = raw_time
        # Add track
        self.track_dict[track["id"]] = track
        # Save db in file
        self.save()

    def delete(self, track_id):
        del self.track_dict[track_id]
        self.save()

    def save(self):
        db_dict = {"tracks_db": self.track_dict}
        with open(self.db_file, "w") as f:
            json.dump(db_dict, f)


class MainPage(Screen):
    track_dialog = None
    confirm_delete_dialog = None

    def __init__(self, app, db, **kwargs):
        super(MainPage, self).__init__()
        self.app = app
        self.db = db
        # self.displayed_ids = []
        self.update_list()

    def update_list(self):
        self.ids.track_container.clear_widgets()
        # Add new items
        for id, track in self.db.track_dict.items():
            # if id not in self.displayed_ids:
            style_str = ', '.join(track["style"])
            item = TwoLineListItem(
                text=f"{track['record']} - {track['num']}. {track['track']}",
                secondary_text=f"{track['artist']}, {style_str}, BPM={track['bpm']}, Key={track['key']}, Power={track['power']}, RPM={track['rpm']}",
                on_release=self.open_track_dialog
            )
            self.ids.track_container.add_widget(item)
            self.ids.track_container.ids[id] = item

        # Sort

    def open_track_dialog(self, list_item):
        # Find id of track
        for id in self.ids.track_container.ids:
            if self.ids.track_container.ids[id] == list_item:
                track = self.db.track_dict[id]
                break
        # Create the string to display in the confirm dialog
        style_str = ', '.join(track["style"])
        track_str = "Record: {}\nTrack #: {}\nTrack name:{}\nArtist: {}\nStyle: {}\nBPM: {}\nKey: {}\nPower: {}\nRPM: {}\nComment: {}".format(
            track["record"], track["num"], track["track"], track["artist"], 
            style_str, track["bpm"], track["key"], track["power"], 
            track["rpm"], track["comment"]
        )
        # Open dialog
        self.track_dialog = MDDialog(
            title="Track information",
            text=track_str,
            buttons=[
                MDFlatButton(
                    text="Modify",
                    theme_text_color="Custom",
                    text_color=[1, 0.77, 0, 1],
                    on_release=lambda *args: self.send_track_to_mod(id, *args)
                ),
                MDFlatButton(
                    text="Delete",
                    theme_text_color="Custom",
                    text_color=[1, 0, 0, 1],
                    on_release=lambda *args: self.confirm_delete(id, track_str, *args)
                ),
                MDFlatButton(
                    text="Close",
                    on_release=self.close_track_dialog
                )
            ]
        )
        self.track_dialog.open()

    def send_track_to_mod(self, id, *args):
        self.track_dialog.dismiss()
        self.app.mod_track(id)

    def confirm_delete(self, id, track_str, *args):
        # Open dialog
        self.confirm_delete_dialog = MDDialog(
            title="Confirm deleting this track ?",
            text=track_str,
            buttons=[
                MDFlatButton(
                    text="YES Delete",
                    theme_text_color="Custom",
                    text_color=[1, 0, 0, 1],
                    on_release=lambda *args: self.delete_track(id, *args)
                ),
                MDFlatButton(
                    text="Close",
                    on_release=self.close_delete_dialog
                )
            ]
        )
        self.confirm_delete_dialog.open()

    def delete_track(self, id, *args):
        self.confirm_delete_dialog.dismiss()
        self.track_dialog.dismiss()
        self.db.delete(id)
        self.update_list()

    def close_track_dialog(self, *args):
        self.track_dialog.dismiss()

    def close_delete_dialog(self, *args):
        self.confirm_delete_dialog.dismiss()



class AddTrackPage(Screen):
    confirm_dialog = None
    current_id = None

    def __init__(self, app, **kwargs):
        super(AddTrackPage, self).__init__()
        self.app = app
        self.set_track_info()

    def add_track(self):
        """ Called when pushing the 'ADD' button. 
            Ask for confirmation and sends the new track to the main app to be
            added.
            If id is specified, the page will modify an existing track.
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
            "key": self.ids.key.text,
            "power": self.ids.power.text,
            "rpm": self.ids.rpm.text,
            "comment": self.ids.comment.text
        }
        # Create the string to display in the confirm dialog
        style_str = ', '.join(new_track["style"])
        track_str = "Record: {}\nTrack #: {}\nTrack name:{}\nArtist: {}\nStyle: {}\nBPM: {}\nKey: {}\nPower: {}\nRPM: {}\nComment: {}".format(
            new_track["record"], new_track["num"], new_track["track"], 
            new_track["artist"], style_str, new_track["bpm"], new_track["key"],
            new_track["power"], new_track["rpm"], new_track["comment"]
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
        self.app.add_new_track(new_track, self.current_id)

    def set_track_info(self, track=None):
        styles = ["", "", ""]
        if track is not None:
            self.current_id = track["id"]
            for i in range(len(track["style"])):
                styles[i] = track["style"][i]
        self.ids.record_name.text = track["record"] if track is not None else ""
        self.ids.track_num.text = track["num"] if track is not None else ""
        self.ids.track_name.text = track["track"] if track is not None else ""
        self.ids.artist.text = track["artist"] if track is not None else ""
        self.ids.style1.text = styles[0]
        self.ids.style2.text = styles[1]
        self.ids.style3.text = styles[2]
        self.ids.bpm.text = track["bpm"] if track is not None else ""
        self.ids.key.text = track["key"] if track is not None else ""
        self.ids.power.text = track["power"] if track is not None else ""
        self.ids.rpm.text = track["rpm"] if track is not None else ""
        self.ids.comment.text = track["comment"] if track is not None else ""


class RecordDBApp(MDApp):
    # Buttons on Floating Action Dial
    data = {
        'Add Record': 'album'
    }

    def __init__(self):
        super(RecordDBApp, self).__init__()
        # DB
        self.db = RecordDB("TEST_DB.json")
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
        self.main_page = MainPage(self, self.db, name="main_page")
        self.add_track_page = AddTrackPage(self, name="add_track_page")
        self.sm.add_widget(self.main_page)
        self.sm.add_widget(self.add_track_page)
        self.sm.current = "main_page"

    def callback(self, instance):
        # Main page: add record button -> go to add record page
        if instance.icon == "album":
            self.add_track_page.current_id = None
            self.sm.current = "add_track_page"
        # Add record page: back button -> go to main page
        if instance.icon == "arrow-left":
            self.sm.current = "main_page"

    def add_new_track(self, new_track, track_id):
        print("Add track", track_id, new_track)
        # Add track to db
        self.db.add(new_track, track_id)
        # Update main page list
        self.main_page.update_list()
        # Go to main page
        self.sm.current = "main_page"

    def mod_track(self, track_id):
        print("Mod track", track_id)
        self.add_track_page.set_track_info(self.db.track_dict[track_id])
        self.sm.current = "add_track_page"


if __name__ == "__main__":
    RecordDBApp().run()