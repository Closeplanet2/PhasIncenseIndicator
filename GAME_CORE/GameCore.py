from CORES.TkinterController import TkinterController, DestructionStage
from CORES.InputController import InputController
from CORES.MongoController import MongoController
from GAME_CORE.GameSettings import GameSettings
from GAME_CORE.UserData import UserData
import time

class GameCore:
    def __init__(self):
        self.GameSettings = GameSettings()
        self.UserData = UserData(
            url="mongodb+srv://Admin1234:fl6UGVNw04hxF7s6@phasincenseindicator.2wltjib.mongodb.net/?retryWrites=true&w=majority",
            db_name="PhasIncenseIndicator"
        )
        self.TkinterController = TkinterController(debug_info=GameSettings.debug_info)
        self.InputController = InputController(debug_info=GameSettings.debug_info)
        self.InputController.listen_for_keyboard(on_press=self.callback_on_press, on_release=self.callback_on_release)
        self.entered_name = ""
        self.entered_session_code = ""
        self.DatabaseUsername = None
        self.DatabaseSessionCode = None
        self.create_window()

    def create_window(self):
        self.TkinterController.create_window(
            function_thread_callback=self.function_thread_callback,
            wh=self.GameSettings.window_height, ww=self.GameSettings.window_width,
            wt=self.GameSettings.window_title, bg=self.GameSettings.window_background_color,
            update_gui_per_second=self.GameSettings.update_gui_per_second
        )

        self.TkinterController.add_callback_function(self.callback_create_smudge_images)
        self.TkinterController.add_callback_function(self.TkinterController.destroy_widgets)

        self.TkinterController.add_label(
            text="Enter Username:", bg="#64FAFF", fg="#000000", w=int(self.GameSettings.window_width / 11), h=1, x_pos=0, y_pos=0,
            destroy_status=DestructionStage.DONT_DESTROY
        )

        self.TkinterController.add_entry_field(
            placeholder_text="", callback_function=self.callback_username_input_field,
            pos_x=0, pos_y=30, width=36, destroy_status=DestructionStage.DONT_DESTROY
        )

        self.TkinterController.add_entry_field(
            placeholder_text="", callback_function=self.callback_session_code,
            pos_x=0, pos_y=60, width=36, destroy_status=DestructionStage.DONT_DESTROY
        )

        self.TkinterController.add_button(
            text="Reset Data", function_callback=self.callback_reset_data, thread_function=False, bg="#FF8181", fg="#000000",
            w=int(self.GameSettings.window_width / 11), h=1, x_pos=0, y_pos=90, destroy_status=DestructionStage.DONT_DESTROY
        )

        self.TkinterController.add_button(
            text="Smudge", function_callback=self.callback_died, thread_function=False, bg="#FF8181",
            fg="#000000",
            w=int(self.GameSettings.window_width / 11), h=1, x_pos=0, y_pos=130,
            destroy_status=DestructionStage.DONT_DESTROY
        )

        self.TkinterController.add_button(
            text="Died", function_callback=self.callback_used_smudge, thread_function=False, bg="#FF8181",
            fg="#000000",
            w=int(self.GameSettings.window_width / 11), h=1, x_pos=0, y_pos=170,
            destroy_status=DestructionStage.DONT_DESTROY
        )

        self.TkinterController.start_window()

    def function_thread_callback(self):
        pass

    def callback_create_smudge_images(self, current_window):
        if not self.is_signed_in(): return

        index = 0
        for user_data in self.UserData.return_all_user_data():
            if not user_data['SESSION_CODE'] == self.DatabaseSessionCode: continue
            card_image_player = f"IMAGES/ProfileImages/{user_data['USERNAME']}.png" if not user_data['DIED'] else f"IMAGES/ProfileImages/{user_data['USERNAME']}Dead.png"
            self.TkinterController.add_image_as_grid(
                card_image=card_image_player, w=150, h=150,
                pos_x=50, pos_y=220, offest_y=145, offset_x=155, numx=2, numy=4, index=index,
                destroy_status=DestructionStage.DELAYED_DESTROY
            )
            index += 1
            card_image_incense = "IMAGES/Incense.png" if not user_data['SMUDGED'] else "IMAGES/UsedIncense.png"
            self.TkinterController.add_image_as_grid(
                card_image=card_image_incense, w=150, h=150,
                pos_x=50, pos_y=220, offest_y=145, offset_x=155, numx=2, numy=4, index=index,
                destroy_status=DestructionStage.DELAYED_DESTROY
            )
            index += 1
        time.sleep(1 / self.GameSettings.update_gui_per_second)

    def callback_username_input_field(self, username):
        self.entered_name = str(username.get())

    def callback_session_code(self, session_code):
        self.entered_session_code = str(session_code.get())

    def callback_reset_data(self, thread_index=-1, args=None):
        self.DatabaseUsername = self.entered_name
        self.DatabaseSessionCode = self.entered_session_code
        user_account = self.UserData.return_user_data(username=self.DatabaseUsername, session_code=self.DatabaseSessionCode, wipe_data=True)
        self.UserData.save_user_data(self.DatabaseUsername, user_account)

    def callback_on_press(self, key):
        try:
            if key.char == '8':
                self.callback_used_smudge()
            elif key.char == '9':
                self.callback_died()
            elif key.char == '0':
                self.callback_reset_data()
        except AttributeError:
            pass

    def callback_on_release(self, key):
        pass

    def callback_used_smudge(self, thread_index=-1, args=None):
        if not self.is_signed_in(): return
        user_account = self.UserData.return_user_data(username=self.DatabaseUsername, session_code=self.DatabaseSessionCode, wipe_data=False)
        user_account["SMUDGED"] = True
        self.UserData.save_user_data(self.DatabaseUsername, user_account)

    def callback_died(self, thread_index=-1, args=None):
        if not self.is_signed_in(): return
        user_account = self.UserData.return_user_data(username=self.DatabaseUsername, session_code=self.DatabaseSessionCode, wipe_data=False)
        user_account["DIED"] = True
        self.UserData.save_user_data(self.DatabaseUsername, user_account)

    def is_signed_in(self):
        return not self.DatabaseUsername is None and not self.DatabaseSessionCode is None
