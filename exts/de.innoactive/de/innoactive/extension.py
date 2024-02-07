import omni.ext
import omni.ui as ui
from omni.ui import color as cl
import omni.kit
import carb
import subprocess
import os
import webbrowser
import threading
from pxr import Usd
import omni.usd
from urllib.parse import quote

LABEL_WIDTH = 120
FIELD_WIDTH = 230
BTN_SPACING = 5

HEIGHT = 24

SPACING = 4

MODES = ("browser", "VR", "local")
MODES_TECHNICAL = ("cloud/browser", "cloud/standalone", "local/windows")

APPS = ("Omniverse USD Composer 2023.2.3", "Omniverse USD Composer 2023.2.0")
APP_IDS = (3757, 1501)

settings = carb.settings.get_settings()

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

    def set_notification(self, value, label):
        self._notification_label.text = ""
        self._notification_label.visible = False
        self._warning_label.text = ""
        self._warning_label.visible = False
        
        label.text = value
        label.visible = True
        def delete_notification():
            label.text = ""
            label.visible = False

        timer = threading.Timer(5, delete_notification)
        timer.start()
    
    def is_sharable_usd(self, file_path):
        return file_path.startswith("omniverse://") or file_path.startswith("http://") or file_path.startswith("https://") # and not file_path.startswith("omniverse://localhost")
        
    def update_sharing_link(self):
        args = quote(self._usd_url_model.as_string, safe='')
        self._sharing_url_model.as_string = self._base_url_model.as_string + "/apps/" + self._app_id_model.as_string + "/launch/" + self._mode_str_model.as_string + "?args=" + args
        self._sharing_url_model_label.text = self._sharing_url_model.as_string

    def on_value_changed(self, item_model):
        self.update_sharing_link()
        self.save_settings()

    def on_usd_value_changed(self, item_model):
        self.update_sharing_link()
        self.save_settings()
    
    def on_mode_changed(self, item_model, item):
        value_model = item_model.get_item_value_model(item)
        current_index = value_model.as_int
        self._mode_str_model.as_string = MODES_TECHNICAL[current_index]

        self.update_sharing_link()
        self.save_settings()
    
    def on_app_changed(self, item_model, item):
        value_model = item_model.get_item_value_model(item)
        current_index = value_model.as_int
        self._app_id_model.as_int = APP_IDS[current_index]

        self.update_sharing_link()
        self.save_settings()

    def save_settings(self):
        settings.set("/persistent/exts/de/innoactive/baseUrl", self._base_url_model.as_string)
        settings.set("/persistent/exts/de/innoactive/renderMode", self._mode_str_model.as_string)
        settings.set("/persistent/exts/de/innoactive/appId", self._app_id_model.as_int)
        #print(f"self._app_id_model.as_int {self._app_id_model.as_int}")
        #id = settings.get("/de/innoactive/appId")
        #print(f"self._app_id_model.as_int saved {id}")
        
    def load_settings(self):
        self._base_url_model.as_string = settings.get("/persistent/exts/de/innoactive/baseUrl")
        self._mode_str_model.as_string = settings.get("/persistent/exts/de/innoactive/renderMode")
        self._app_id_model.as_int = settings.get("/persistent/exts/de/innoactive/appId")
        
        # Defaults
        if self._base_url_model.as_string == "":
            self._base_url_model.as_string = "https://company123.innoactive.io"
        
        if self._mode_str_model.as_string == "":
            self._mode_str_model.as_string = "cloud/standalone"
        
        if self._app_id_model.as_int == 0:
            self._app_id_model.as_int = 3757

        #id = APP_IDS.index(1501)
        #print(f"APP_IDS.index(1501) {id}")
        print("persistent settings are stored in: {}".format(settings.get("/app/userConfigPath")))
        #print(self._app_id_model.as_int)
        #value_model = self._app_model.get_item_value_model()
        #value_model.as_int = APP_IDS.index(self._app_id_model.as_int)
        #print(value_model.as_int)
        
                
    def clear_usd(self):
        # Clear USD file from field
        self._usd_url_model.as_string = ""

    def set_stage_usd(self):
        # Implement logic to fetch the currently opened USD file path
        stage = omni.usd.get_context().get_stage()
        rootLayer = stage.GetRootLayer()
        file_path = rootLayer.realPath if rootLayer else ""
        if self.is_sharable_usd(file_path):
           #self.set_notification(f"USD file URL: {file_path}")
            self._usd_url_model.as_string = file_path
        else:
            #self.set_notification("The USD file URL does not start with 'omniverse://'.")
            self._usd_url_model.as_string = ""
    
    def copy_url(self):
        # Copy the generated link to clipboard
        if not self._usd_url_model.as_string:
            self.set_notification("No USD file selected. Please select a valid omniverse:// or http(s):// USD file URL", self._warning_label)
        elif not self.is_sharable_usd(self._usd_url_model.as_string):
            self.set_notification("USD file is not shareable. Use omniverse:// or http(s):// format.", self._warning_label)
        else:
            self.copy_to_clipboard(self._sharing_url_model.as_string)
            self.set_notification("Sharing link copied to clipboard.", self._notification_label)
            

    def open_url(self):
        # Open URL in web browser
        if not self._usd_url_model.as_string:
            self.set_notification("No USD file selected. Please select a valid omniverse:// or http(s):// USD file URL", self._warning_label)
        elif not self.is_sharable_usd(self._usd_url_model.as_string):
            self.set_notification("USD link is not shareable. Use omniverse:// or http(s):// format.", self._warning_label)
        else:
            webbrowser.open_new_tab(self._sharing_url_model.as_string)
            self.set_notification("Sharing link opened in browser.", self._notification_label)

    def open_invite_url(self):
        # Open URL in web browser
        invite_url = self._base_url + "/control-panel/v2/users"
        webbrowser.open_new_tab(invite_url)
        
    def on_shutdown(self):
        print("[de.innoactive] de innoactive shutdown")

    def on_startup(self, ext_id):
        print("Innoactive startup")
        
        manager = omni.kit.app.get_app().get_extension_manager()
        ext_path = manager.get_extension_path_by_module("de.innoactive")
        
        self._window = ui.Window("Innoactive Portal", width=600, height=350)
        with self._window.frame:
            with ui.VStack(spacing=8, height=0):
                
                with ui.HStack(spacing=5):
                    img = ui.Image(height=40, alignment=ui.Alignment.RIGHT)
                    img.source_url = ext_path + "/data/innoactive_logo2.png" 
                    
                with ui.HStack(spacing=5):
                    ui.Label("USD file", name="usd_url", width=LABEL_WIDTH, height=HEIGHT, tooltip="Ensure the USD file is hosted on Nucleus and the user with whom you want to share access has permissions to access that file on Nucleus Server.")
                    self._usd_url_model = ui.SimpleStringModel()
                    self._usd_url_model.as_string = ""
                    ui.StringField(model=self._usd_url_model, height=HEIGHT, word_wrap=True)
                    self._usd_url_model_changed = self._usd_url_model.subscribe_value_changed_fn(self.on_usd_value_changed)
                    ui.Button("From Stage", clicked_fn=self.set_stage_usd, width=90, height=HEIGHT, tooltip="Use the currently loaded USD file from Stage")
                
                with ui.HStack(spacing=5):
                    ui.Label("Runtime", name="app", width=LABEL_WIDTH, height=HEIGHT, tooltip="Select the OV Kit runtime you want to use. You can upload your own runtimes, please contact Innoactive support.")
                    self._app_id_model = ui.SimpleStringModel()
                    self._app_id_model.as_int = settings.get("/persistent/exts/de/innoactive/appId")
                    self._app_model = ui.ComboBox(APP_IDS.index(self._app_id_model.as_int), *APPS).model
                    self._app_model_changed = self._app_model.subscribe_item_changed_fn(self.on_app_changed)
                
                with ui.HStack(spacing=5):
                    ui.Label("Streaming Mode", name="mode", width=LABEL_WIDTH, height=HEIGHT, tooltip="Select weather the link shall start a browser stream, VR stream or a locally rendered session")
                    self._mode_str_model = ui.SimpleStringModel()
                    self._mode_str_model.as_string = settings.get("/persistent/exts/de/innoactive/renderMode")
                    print("renderMode: " + self._mode_str_model.as_string)
                    self._mode_model = ui.ComboBox(MODES_TECHNICAL.index(self._mode_str_model.as_string), *MODES).model
                    self._mode_model_changed = self._mode_model.subscribe_item_changed_fn(self.on_mode_changed)
                
                with ui.HStack(spacing=5):
                    ui.Label("Base Url", name="base_url", width=LABEL_WIDTH, height=HEIGHT, tooltip="Set this to your match your Innoactive Portal cloud domain URL")
                    self._base_url_model = ui.SimpleStringModel()
                    self._base_url_model.as_string = settings.get("/persistent/exts/de/innoactive/baseUrl")
                    ui.StringField(model=self._base_url_model, height=HEIGHT, word_wrap=True)
                    self._base_url_model_changed = self._base_url_model.subscribe_value_changed_fn(self.on_value_changed)
        
                ui.Line()

                with ui.HStack(spacing=5):
                    ui.Label("Sharing URL", name="sharing_url", width=LABEL_WIDTH, height=HEIGHT, tooltip="Copy and share this link with a user. You need to invite the user to Innoactive Portal as well.")
                    self._sharing_url_model = ui.SimpleStringModel()
                    self._sharing_url_model_label = ui.Label("", word_wrap=True, alignment=ui.Alignment.TOP)
                
                with ui.HStack(spacing=5):
                    ui.Spacer( width=LABEL_WIDTH)
                    self.button_copy = ui.Button("Copy", clicked_fn=self.copy_url, width=60, height=HEIGHT, tooltip="Copy the sharing link to the clipboard")
                    self.button_test = ui.Button("Test", clicked_fn=self.open_url, width=60, height=HEIGHT, tooltip="Test the sharink link on your PC")
                    self.button_invite = ui.Button("Invite user", clicked_fn=self.open_invite_url, width=90, height=HEIGHT, tooltip="Invite a user to Innoactive Portal")
                    
                with ui.HStack(spacing=5, height=HEIGHT, style={"Notification": {"color": cl("#76b900")}, "Error": {"color": cl("#d48f09")}}):
                    ui.Spacer( width=LABEL_WIDTH)
                    with ui.VStack(spacing=8, height=0):
                        self._notification_label = ui.Label("", word_wrap=True, name="notification", height=HEIGHT, visible=False, style_type_name_override="Notification")
                        self._warning_label = ui.Label("", word_wrap=True, name="notification", height=HEIGHT, visible=False, style_type_name_override="Error")

        self.load_settings()
        self.update_sharing_link()
        self.set_stage_usd()
