import omni.ext
import omni.ui as ui
import omni.kit
import pyperclip  # Assume this is available for clipboard operations

LABEL_WIDTH = 120
FIELD_WIDTH = 230

HEIGHT = 24

SPACING = 4

MODES = ("browser", "VR")
MODES_TECHNICAL = ("browser", "standalone")

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

    def update_sharing_link(self):
        self._sharing_url_model.as_string = self._base_url_model.as_string + "/apps/" + self._app_id_model.as_string + "/launch/cloud/" + self._mode_str_model.as_string
        self._sharing_url_model_label.text = self._sharing_url_model.as_string

    def on_end_edit_string(self, item_model):
        self.update_sharing_link()
        pass

    def on_item_changed(self, item_model, item):
        value_model = item_model.get_item_value_model(item)
        current_index = value_model.as_int
        self._mode_str_model.as_string = MODES_TECHNICAL[current_index]

        self.update_sharing_link()

    def on_startup(self, ext_id):
        print("Innoactive startup")

        self._base_url = "https://portal.innoactive.io"
        self._app_id = 1501  # Default app ID, to be provided
        self._usd_file_link = self.get_current_usd_file()  # Implement this method
        self._mode = "browser"  # Default to browser stream
        self._generated_link = ""

        self._window = ui.Window("Innoactive Portal", width=400, height=400)
        with self._window.frame:
            with ui.VStack():
                with ui.HStack():
                    ui.Label("Base Url", name="base_url", width=LABEL_WIDTH, height=HEIGHT)
                    self._base_url_model = ui.SimpleStringModel()
                    self._base_url_model.as_string = self._base_url
                    ui.StringField(model=self._base_url_model, height=HEIGHT, word_wrap=True)
                    self._base_url_model_changed = self._base_url_model.subscribe_value_changed_fn(self.on_end_edit_string)
                ui.Spacer( height=10)
                
                with ui.HStack():
                    ui.Label("App ID", name="app_id", width=LABEL_WIDTH, height=HEIGHT)
                    self._app_id_model = ui.SimpleIntModel()
                    self._app_id_model.as_int = self._app_id
                    ui.IntField(model=self._app_id_model, height=HEIGHT)
                    self._app_id_model_changed = self._app_id_model.subscribe_value_changed_fn(self.on_end_edit_string)
                ui.Spacer( height=10)
                
                with ui.HStack():
                    ui.Label("Mode", name="mode", width=LABEL_WIDTH, height=HEIGHT)
                    self._mode_str_model = ui.SimpleStringModel()
                    self._mode_str_model.as_string = self._mode
                    self._mode_model = ui.ComboBox(0, *MODES).model
                    self._mode_model_changed = self._mode_model.subscribe_item_changed_fn(self.on_item_changed)
                ui.Spacer( height=10)
            
                with ui.HStack():
                    ui.Label("Sharing Url", name="sharing_url", width=LABEL_WIDTH, height=HEIGHT)
                    self._sharing_url_model = ui.SimpleStringModel()
                    self._sharing_url_model_label = ui.Label("", width=FIELD_WIDTH, word_wrap=True, alignment=ui.Alignment.TOP)
                
                with ui.HStack():
                    ui.Spacer( width=LABEL_WIDTH)
                    ui.Button("Copy Link", clicked_fn=self.copy_link_to_clipboard, width=LABEL_WIDTH, height=HEIGHT, alignment=ui.Alignment.RIGHT)
                
                ui.Spacer()
                
        self.update_sharing_link()

    def get_current_usd_file(self):
        # Implement logic to fetch the currently opened USD file path
        return "omniverse://localhost/Projects/Factory/Factory.usd"

    def generate_link(self):
        base_url = self._base_url_field.model.get_value()
        app_id = self._app_id_field.model.get_value()
        usd_file_link = self._usd_file_link_field.model.get_value()
        stream_type = self._stream_type_dropdown.model.get_item_value(self._stream_type_dropdown.model.get_value())

        # Validate USD file link
        if not usd_file_link.startswith("omniverse://"):
            self._generated_link_label.text = "Error: USD file link must start with omniverse://"
            return
        
        # Construct the deep link
        self._generated_link = f"{base_url}/app/{app_id}?file={usd_file_link}&mode={stream_type}"
        self._generated_link_label.text = f"Generated Link: {self._generated_link}"

    def copy_link_to_clipboard(self):
        # Copy the generated link to clipboard
        pyperclip.copy(self._generated_link)
        print("Link copied to clipboard.")

    def on_shutdown(self):
        print("[de.innoactive] de innoactive shutdown")
