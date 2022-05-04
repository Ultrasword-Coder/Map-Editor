import os
import json


from engine.globals import *
from engine import state, user_input, filehandler

from . import SideBar, Editor, WindowObject, art
from .globals import *

class ProjectWorld:
    def __init__(self):
        """Creates the project world"""
        self.state = WindowObject.WindowObjectManager()
        # set state current
        state.push_state(self.state)

        # add all the objects
        self.all_container = WindowObject.WindowObject(0, 0, 1, 1)
        self.all_container.set_background_color(Theme.BACKGROUND)

        self.sidebar_container = self.all_container.create_child(0.005, 0.01, 0.38, 0.995, SideBar.SideBarContainer)
        self.sidebar_container.set_secondary_color(Theme.SECONDARY)
        art.set_current_sidebar(self.sidebar_container)

        self.editor = self.all_container.create_child(0.385, 0.01, 0.995, 0.995, Editor.Editor)
        self.editor.set_background_color(Theme.SECONDARY)
        art.set_current_editor(self.editor)

        self.load_from_config_json()

    # --------------- load from config.json --------------- #
    def load_from_config_json(self):
        """Load from config json"""
        # load from config.json located in root directory
        if not os.path.exists(CONFIG_PATH):
            # create config
            with open(CONFIG_PATH, 'w') as file:
                json.dump({"startup-files": []}, file)
                file.close()
        else:
            with open(CONFIG_PATH, 'r') as file:
                data = json.load(file)
                file.close()
            for file in data[CONFIG_FILES_ARRAY]:
                self.sidebar_container.file_dragged(file)
    
    def file_dragged(self, file):
        """Check if file was dropped in either editor or sidebar"""
        if self.sidebar_container.is_hovering():
            # sidebar drag
            self.sidebar_container.file_dragged(file)
        elif self.editor.is_hovering():
            self.editor.file_dragged(file)