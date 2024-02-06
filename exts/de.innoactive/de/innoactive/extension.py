import omni.ext
import omni.ui as ui
from omni.ui import color as cl
import omni.kit
import subprocess
import os
import webbrowser
import threading
from pxr import Usd
import omni.usd
from urllib.parse import quote

LABEL_WIDTH = 120
FIELD_WIDTH = 230

HEIGHT = 24

SPACING = 4

MODES = ("browser", "VR", "local")
MODES_TECHNICAL = ("cloud/browser", "cloud/standalone", "local/windows")

# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print("[de.innoactive] some_public_function was called with x: ", x)
    return x ** x


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class DeInnoactiveExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.

    def copy_to_clipboard(self, text):
        try:
            if os.name == 'nt':  # For Windows
                subprocess.run('clip', universal_newlines=True, input=text, shell=True)
            elif os.name == 'posix':
                if os.system("which pbcopy") == 0:  # macOS has pbcopy
                    subprocess.run('pbcopy', universal_newlines=True, input=text)
                elif os.system("which xclip") == 0 or os.system("which xsel") == 0:  # Linux has xclip or xsel
                    subprocess.run('xclip -selection clipboard', universal_newlines=True, input=text, shell=True)
                else:
                    print("Clipboard utilities pbcopy, xclip, or xsel not found.")
                    return False
            else:
                print("Unsupported OS.")
                return False
            print("Text copied successfully.")
            return True
        except Exception as e:
            print(f"Failed to copy text: {e}")
            return False

    def set_notification(self, value):
        self._notification_label.text = value
        def delete_notification():
            self._notification_label.text = ""

        timer = threading.Timer(5, delete_notification)
        timer.start()
        
    def update_sharing_link(self):
        args = quote(self._usd_url_model.as_string)
        self._sharing_url_model.as_string = self._base_url_model.as_string + "/apps/" + self._app_id_model.as_string + "/launch/" + self._mode_str_model.as_string + "?args=" + args
        self._sharing_url_model_label.text = self._sharing_url_model.as_string

    def on_value_changed(self, item_model):
        self.update_sharing_link()
        pass

    def on_item_changed(self, item_model, item):
        value_model = item_model.get_item_value_model(item)
        current_index = value_model.as_int
        self._mode_str_model.as_string = MODES_TECHNICAL[current_index]

        self.update_sharing_link()

    def get_current_usd_file(self):
        # Implement logic to fetch the currently opened USD file path
        stage = omni.usd.get_context().get_stage()
        rootLayer = stage.GetRootLayer()
        file_path = rootLayer.realPath if rootLayer else ""
        if file_path.startswith("omniverse://"):
            #self.set_notification(f"USD file URL: {file_path}")
            return file_path
        else:
            #self.set_notification("The USD file URL does not start with 'omniverse://'.")
            return ""
        
    def copy_url(self):
        # Copy the generated link to clipboard
        self.copy_to_clipboard(self._sharing_url_model.as_string)
        self.set_notification("Link copied to clipboard.")

    def open_url(self):
        # Open URL in web browser
        webbrowser.open_new_tab(self._sharing_url_model.as_string)
        self.set_notification("Sharing URL opened in default webbrowser.")

    def on_shutdown(self):
        print("[de.innoactive] de innoactive shutdown")

    def on_startup(self, ext_id):
        print("Innoactive startup")

        self._base_url = "https://portal.innoactive.io"
        self._app_id = 1501  # Default app ID, to be provided
        self._usd_file = self.get_current_usd_file()  # Implement this method
        self._mode = "browser"  # Default to browser stream
        self._generated_link = ""

        self._window = ui.Window("Innoactive Portal", width=600, height=300)
        with self._window.frame:
            with ui.VStack(spacing=10, height=0):
                with ui.HStack():
                    ui.Label("Base Url", name="base_url", width=LABEL_WIDTH, height=HEIGHT)
                    self._base_url_model = ui.SimpleStringModel()
                    self._base_url_model.as_string = self._base_url
                    ui.StringField(model=self._base_url_model, height=HEIGHT, word_wrap=True)
                    self._base_url_model_changed = self._base_url_model.subscribe_value_changed_fn(self.on_value_changed)
                
                with ui.HStack():
                    ui.Label("App ID", name="app_id", width=LABEL_WIDTH, height=HEIGHT)
                    self._app_id_model = ui.SimpleIntModel()
                    self._app_id_model.as_int = self._app_id
                    ui.IntField(model=self._app_id_model, height=HEIGHT)
                    self._app_id_model_changed = self._app_id_model.subscribe_value_changed_fn(self.on_value_changed)
                
                with ui.HStack():
                    ui.Label("Streaming Mode", name="mode", width=LABEL_WIDTH, height=HEIGHT)
                    self._mode_str_model = ui.SimpleStringModel()
                    self._mode_str_model.as_string = self._mode
                    self._mode_model = ui.ComboBox(0, *MODES).model
                    self._mode_model_changed = self._mode_model.subscribe_item_changed_fn(self.on_item_changed)
                
                with ui.HStack():
                    ui.Label("USD Url", name="usd_url", width=LABEL_WIDTH, height=HEIGHT)
                    self._usd_url_model = ui.SimpleStringModel()
                    self._usd_url_model.as_string = self._usd_file
                    ui.StringField(model=self._usd_url_model, height=HEIGHT, word_wrap=True)
                    self._usd_url_model_changed = self._usd_url_model.subscribe_value_changed_fn(self.on_value_changed)
                
                with ui.HStack():
                    ui.Label("Sharing Url", name="sharing_url", width=LABEL_WIDTH, height=HEIGHT)
                    self._sharing_url_model = ui.SimpleStringModel()
                    self._sharing_url_model_label = ui.Label("", word_wrap=True, alignment=ui.Alignment.TOP)
                
                with ui.HStack():
                    ui.Spacer( width=LABEL_WIDTH)
                    ui.Button("Copy", clicked_fn=self.copy_url, width=60, height=HEIGHT)
                    ui.Button("Test", clicked_fn=self.open_url, width=60, height=HEIGHT)
                
                with ui.HStack(style={"Label": {"color": cl("#058ef8")}}):
                    ui.Spacer( width=LABEL_WIDTH)
                    self._notification_label = ui.Label("", name="notification", height=HEIGHT)

        self.update_sharing_link()
