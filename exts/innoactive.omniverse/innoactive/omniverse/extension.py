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
HEIGHT = 24
VSPACING = 8
HSPACING = 5


MODES = ("browser", "XR", "local")
MODES_TECHNICAL = ("cloud/browser", "cloud/standalone", "local/windows")

APPS = ("Omniverse USD Explorer", "Omniverse USD Composer", "Omniverse USD Streamer for AVP (XR only)")
APP_IDS = ("7b0b754a-b90b-4d3b-a043-d9a72f1e4d7f", "48d5be05-49af-41d3-a383-942ebc377c59", "0a7b7798-123e-4158-ad66-a09e255a2400")

DEFAULT_BASE_URL = "https://[yourcompany].innoactive.io"
DEFAULT_APP_ID = "7b0b754a-b90b-4d3b-a043-d9a72f1e4d7f"
DEFAULT_MODE = "cloud/browser"

settings = carb.settings.get_settings()

# Public functions
def get_sharing_link():
    print("[innoactive.omniverse] get_sharing_link ")
    return self._sharing_url_model.as_string
    
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
        args = quote("--usd "+self._usd_url_model.as_string, safe='')
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
        self._app_id_model.as_string = APP_IDS[current_index]

        self.update_sharing_link()
        self.save_settings()

    def save_settings(self):
        settings.set("/persistent/exts/de/innoactive/baseUrl", self._base_url_model.as_string)
        settings.set("/persistent/exts/de/innoactive/renderMode", self._mode_str_model.as_string)
        settings.set("/persistent/exts/de/innoactive/appId", self._app_id_model.as_string)
        
    def load_settings(self):
        try:
            self._base_url_model.as_string = settings.get("/persistent/exts/de/innoactive/baseUrl")
            self._mode_str_model.as_string = settings.get("/persistent/exts/de/innoactive/renderMode")
            self._app_id_model.as_string = settings.get("/persistent/exts/de/innoactive/appId")
        except Exception as e:
            self._base_url_model.as_string = DEFAULT_BASE_URL
            self._mode_str_model.as_string = DEFAULT_MODE
            self._app_id_model.as_string = DEFAULT_APP_ID
                
    def clear_usd(self):
        # Clear USD file from field
        self._usd_url_model.as_string = ""

        
    def set_stage_usd(self, at_autoload=False):
        # Implement logic to fetch the currently opened USD file path
        try:
            stage = omni.usd.get_context().get_stage()
            rootLayer = stage.GetRootLayer()
            file_path = rootLayer.realPath if rootLayer else ""
            if self.is_sharable_usd(file_path):
                self._usd_url_model.as_string = file_path
            else:
                if not at_autoload: 
                    self.set_notification("Please load a valid omniverse:// or http(s):// USD file URL to your stage.", self._warning_label)
                self._usd_url_model.as_string = ""
        except Exception as e:
            if not at_autoload: 
                self.set_notification("Please load a valid omniverse:// or http(s):// USD file URL to your stage.", self._warning_label)
            self._usd_url_model.as_string = ""
    
    def validate_form(self):
        if not self._usd_url_model.as_string:
            self.set_notification("No USD file selected. Please select a valid omniverse:// or http(s):// USD file URL", self._warning_label)
        elif not self.is_sharable_usd(self._usd_url_model.as_string):
            self.set_notification("USD file is not shareable. Use omniverse:// or http(s):// format.", self._warning_label)
        elif self._base_url_model.as_string == DEFAULT_BASE_URL:
            self.set_notification("Configure Base URL to match your organization's Innoactive Portal domain name.", self._warning_label)
        else:
            return True
        return False
    
    def copy_url(self):
        # Copy the generated link to clipboard
        if self.validate_form():
            self.copy_to_clipboard(self._sharing_url_model.as_string)
            self.set_notification("Sharing link copied to clipboard.", self._notification_label)
            

    def open_url(self):
        if self.validate_form():
            webbrowser.open_new_tab(self._sharing_url_model.as_string)
            self.set_notification("Sharing link opened in browser.", self._notification_label)

    def open_invite_url(self):
        if self.validate_form():
            invite_url = self._base_url_model.as_string + "/control-panel/v2/users"
            webbrowser.open_new_tab(invite_url)
    
    def on_shutdown(self):
        print("[innoactive.omniverse] shutdown")

    def on_startup(self, ext_id):
        print("Innoactive startup")
        
        manager = omni.kit.app.get_app().get_extension_manager()
        ext_path = manager.get_extension_path_by_module("innoactive.omniverse")
        
        self._window = ui.Window("Innoactive Portal", width=600, height=400)
        with self._window.frame:
            with ui.VStack(spacing=VSPACING, height=0):
                
                with ui.HStack(spacing=HSPACING):
                    img = ui.Image(height=80, alignment=ui.Alignment.RIGHT)
                    img.source_url = ext_path + "/data/innoactive_logo.png" 
                    
                with ui.HStack(spacing=HSPACING):
                    ui.Label("USD file", name="usd_url", width=LABEL_WIDTH, height=HEIGHT, tooltip="Ensure the USD file is hosted on Nucleus and the user with whom you want to share access has permissions to access that file on Nucleus Server.")
                    self._usd_url_model = ui.SimpleStringModel()
                    self._usd_url_model.as_string = ""
                    ui.StringField(model=self._usd_url_model, height=HEIGHT, word_wrap=True)
                    self._usd_url_model_changed = self._usd_url_model.subscribe_value_changed_fn(self.on_usd_value_changed)
                    ui.Button("From Stage", clicked_fn=self.set_stage_usd, width=90, height=HEIGHT, tooltip="Use the currently loaded USD file from Stage")
                
                with ui.HStack(spacing=HSPACING):
                    ui.Label("Runtime", name="app", width=LABEL_WIDTH, height=HEIGHT, tooltip="Select the OV Kit runtime you want to use. You can upload your own runtimes, please contact Innoactive support.")
                    self._app_id_model = ui.SimpleStringModel()
                    try:
                        self._app_id_model.as_string = settings.get("/persistent/exts/de/innoactive/appId")
                    except Exception as e:
                        self._app_id_model.as_string = DEFAULT_APP_ID
                    self._app_model = ui.ComboBox(APP_IDS.index(self._app_id_model.as_string), *APPS).model
                    self._app_model_changed = self._app_model.subscribe_item_changed_fn(self.on_app_changed)
                
                with ui.HStack(spacing=HSPACING):
                    ui.Label("Streaming Mode", name="mode", width=LABEL_WIDTH, height=HEIGHT, tooltip="Select weather the link shall start a browser stream, VR stream or a locally rendered session")
                    self._mode_str_model = ui.SimpleStringModel()
                    try:
                        self._mode_str_model.as_string = settings.get("/persistent/exts/de/innoactive/renderMode")
                    except Exception as e:
                         self._mode_str_model.as_string = DEFAULT_MODE
                    print("renderMode: " + self._mode_str_model.as_string)
                    self._mode_model = ui.ComboBox(MODES_TECHNICAL.index(self._mode_str_model.as_string), *MODES).model
                    self._mode_model_changed = self._mode_model.subscribe_item_changed_fn(self.on_mode_changed)
                
                with ui.HStack(spacing=HSPACING):
                    ui.Label("Base Url", name="base_url", width=LABEL_WIDTH, height=HEIGHT, tooltip="Set this to your match your Innoactive Portal cloud domain URL")
                    self._base_url_model = ui.SimpleStringModel()
                    try:
                        self._base_url_model.as_string = settings.get("/persistent/exts/de/innoactive/baseUrl")
                    except Exception as e:
                        self._base_url_model.as_string = DEFAULT_BASE_URL

                    ui.StringField(model=self._base_url_model, height=HEIGHT, word_wrap=True)
                    self._base_url_model_changed = self._base_url_model.subscribe_value_changed_fn(self.on_value_changed)
                
                ui.Line()

                with ui.HStack(spacing=HSPACING):
                    ui.Label("Sharing URL", name="sharing_url", width=LABEL_WIDTH, height=HEIGHT, tooltip="Copy and share this link with a user. You need to invite the user to Innoactive Portal as well.")
                    self._sharing_url_model = ui.SimpleStringModel()
                    self._sharing_url_model_label = ui.Label("", word_wrap=True, alignment=ui.Alignment.TOP)
                
                with ui.HStack(spacing=HSPACING):
                    ui.Spacer( width=LABEL_WIDTH)
                    self.button_copy = ui.Button("Copy", clicked_fn=self.copy_url, width=60, height=HEIGHT, tooltip="Copy the sharing link to the clipboard")
                    self.button_test = ui.Button("Test", clicked_fn=self.open_url, width=60, height=HEIGHT, tooltip="Test the sharink link on your PC")
                    self.button_invite = ui.Button("Invite user", clicked_fn=self.open_invite_url, width=90, height=HEIGHT, tooltip="Invite a user to Innoactive Portal")
                    
                with ui.HStack(spacing=HSPACING, style={"Notification": {"color": cl("#76b900")}, "Error": {"color": cl("#d48f09")}}):
                    ui.Spacer( width=LABEL_WIDTH)
                    with ui.VStack(spacing=0, height=0):
                        self._notification_label = ui.Label("", word_wrap=True, name="notification", height=HEIGHT, visible=False, style_type_name_override="Notification")
                        self._warning_label = ui.Label("", word_wrap=True, name="notification", height=HEIGHT, visible=False, style_type_name_override="Error")


        self.load_settings()
        self.update_sharing_link()
        self.set_stage_usd(at_autoload=True)
