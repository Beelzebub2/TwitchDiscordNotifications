import datetime
import os
import subprocess
import sys
import tempfile
import time
import tkinter
import customtkinter
from Functions import Json_config_hanldler, others, Sql_handler
import screeninfo
from CTkMessagebox import CTkMessagebox
import Utilities.custom_decorators
from tkinter import filedialog, RIGHT, CENTER, LEFT
from PIL import Image
import pywinstyles


def get_monitor_from_coord(x, y):
    monitors = screeninfo.get_monitors()

    for m in reversed(monitors):
        if m.x <= x <= m.width + m.x and m.y <= y <= m.height + m.y:
            return m
    return monitors[0]


customtkinter.set_default_color_theme("blue")


class MyApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.cwd = os.getcwd()
        self.chj = Json_config_hanldler.JsonConfigHandler(
            os.path.join(self.cwd, "UI\\config.json"))
        self.ch = Sql_handler.SQLiteHandler("data.db")
        self.config_window()

        self.load_ui()

    def config_window(self):
        self.title(
            f'TwitchdiscordNotifications UI {self.chj.get_version()}')
        WIDTH = 1280
        HEIGHT = 720
        self.attributes("-topmost", True)
        self.minsize(WIDTH, HEIGHT)
        self.maxsize(WIDTH, HEIGHT)
        self.bind("<Escape>", lambda e: self.unsaved_changes())
        self.protocol("WM_DELETE_WINDOW", self.unsaved_changes)
        current_screen = get_monitor_from_coord(self.winfo_x(), self.winfo_y())
        screen_width = current_screen.width
        screen_height = current_screen.height
        x_cord = int((screen_width / 2) - (WIDTH / 2))
        y_cord = int((screen_height / 2) - (HEIGHT / 2))
        self.geometry("{}x{}+{}+{}".format(WIDTH, HEIGHT, x_cord, y_cord))
        pywinstyles.apply_style(self, "acrylic")

    def load_ui(self):
        self.render_images()
        self.render_main_frames()
        self.render_main_buttons()
        self.show_bot_page()

    def render_main_frames(self):
        self.left_frame = customtkinter.CTkFrame(
            self, width=250, height=725, fg_color="#2B2B2B")
        self.left_frame.pack()
        self.left_frame.place(anchor="w", relx=0.0,
                              rely=0.5, relwidth=0.2, relheight=1.1)

        self.icon_frame = customtkinter.CTkFrame(
            self.left_frame, width=200, height=155)
        self.icon_frame.pack(expand=True)
        self.icon_frame.place(anchor="n", relx=0.5, rely=0,
                              relwidth=1, relheight=0.261)

        self.panel_icon = customtkinter.CTkLabel(
            self.icon_frame, image=self.icon_img, text=""
        )
        self.panel_icon.place(relx=0.5, rely=0.6, anchor=CENTER)

    def render_images(self):
        self.icon_img = customtkinter.CTkImage(
            light_image=Image.open(
                f"{self.cwd}/UI/banner.png"),
            dark_image=Image.open(
                f"{self.cwd}/UI/banner.png"),
            size=(240, 140))

    def render_main_buttons(self):
        self.logs_page_button = customtkinter.CTkButton(self.left_frame, width=200,
                                                        height=50,
                                                        border_width=0,
                                                        corner_radius=8,
                                                        hover=True,
                                                        text="Logs",
                                                        command=self.show_logs_page)
        self.logs_page_button.place(relx=0.5, rely=0.42, anchor=CENTER)

        self.settings_page_button = customtkinter.CTkButton(self.left_frame, width=200,
                                                            height=50,
                                                            border_width=0,
                                                            corner_radius=8,
                                                            hover=True,
                                                            text="Bot",
                                                            command=self.show_bot_page)
        self.settings_page_button.place(relx=0.5, rely=0.32, anchor=CENTER)

    @Utilities.custom_decorators.run_in_thread
    def exit(self, message=None, save_changes=None):
        if not hasattr(self, "exit_program"):
            self.exit_program = CTkMessagebox(
                title="Exit",
                message="Are you sure you want to exit?" if not message else message,
                icon="question",
                option_1="Yes",
                option_2="No",
                option_3=None if not save_changes else save_changes,
                option_focus="Yes",
                justify="center",
            )
            answer = self.exit_program.get()
            match answer:
                case "Yes":
                    self.quit()
                    sys.exit(0)
                case "Exit and save":
                    self.save_entry_value()
                    self.quit()
                    sys.exit(0)
                case "No":
                    self.exit_program.destroy()
                    del self.exit_program
                case None:
                    self.exit_program.destroy()
                    del self.exit_program

    def show_logs_page(self):
        try:
            self.bot_page_frame.destroy()
            del self.bot_page_frame
        except AttributeError:
            pass
        if hasattr(self, "settings_page_frame"):
            self.bot_page_frame.destroy()
        self.logs_page_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="#242424")
        self.logs_page_frame.pack()
        self.logs_page_frame.place(
            anchor="w", relx=0.2, rely=0, relwidth=0.8, relheight=2.0)

    def show_bot_page(self):
        if not hasattr(self, "bot_page_frame"):
            try:
                self.logs_page_frame.destroy()
                del self.logs_page_frame
            except AttributeError:
                pass

            self.bot_page_frame = customtkinter.CTkFrame(
                self, corner_radius=0, fg_color="#242424")
            self.bot_page_frame.pack()
            self.bot_page_frame.place(
                anchor="w", relx=0.2, rely=0, relwidth=0.8, relheight=2.0)
            self.miscellaneous_settings()
            self.bot_settings()
            self.bot_status()
            self.is_bot_online()

    def bot_status(self):
        self.bot_status_title = customtkinter.CTkLabel(
            self.status_frame, text="Bot Status ", text_color="#FEF9EC", font=('Twitch Gothic', 16, 'bold'), anchor="center")
        self.bot_status_title.place(relx=0.35, rely=0.05)

        self.bot_status_value = customtkinter.CTkLabel(
            self.status_frame, text="Checking...", text_color="#fbff00", font=('Twitch Gothic', 14, 'bold'), anchor="center")
        self.bot_status_value.place(relx=0.4, rely=0.2)

        self.is_on_label = customtkinter.CTkLabel(
            self.status_frame, text="Currently: ", text_color="#FEF9EC", font=('Twitch Gothic', 14, 'bold'), anchor="center")
        self.is_on_label.place(relx=0.1, rely=0.2)

        self.uptime_value = customtkinter.CTkLabel(
            self.status_frame, text="Checking...", text_color="#fbff00", font=('Twitch Gothic', 14, 'bold'), anchor="center")
        self.uptime_value.place(relx=0.4, rely=0.4)

        self.uptime_label = customtkinter.CTkLabel(
            self.status_frame, text="Uptime: ", text_color="#FEF9EC", font=('Twitch Gothic', 14, 'bold'), anchor="center")
        self.uptime_label.place(relx=0.1, rely=0.4)

        self.start_bot_button = customtkinter.CTkButton(self.status_frame, width=80,
                                                        border_width=0,
                                                        corner_radius=8,
                                                        hover=True,
                                                        text="Start Bot",
                                                        fg_color="#08cc56",
                                                        hover_color="#036323",
                                                        command=self.start_bot)
        self.start_bot_button.place(relx=0.35, rely=0.78, anchor=CENTER)

        self.stop_bot_button = customtkinter.CTkButton(self.status_frame, width=80,
                                                       border_width=0,
                                                       corner_radius=8,
                                                       hover=True,
                                                       hover_color="#983500",
                                                       text="Stop Bot",
                                                       fg_color="#f05f11",
                                                       command=self.stop_bot)
        self.stop_bot_button.place(relx=0.65, rely=0.78, anchor=CENTER)

    def bot_settings(self):
        self.bot_settings_frame = customtkinter.CTkFrame(
            self.bot_page_frame, corner_radius=20, fg_color="#756F8B")
        self.bot_settings_frame.pack()
        self.bot_settings_frame.place(
            anchor="w", relx=0.05, rely=0.58, relwidth=0.28, relheight=0.1)

        self.status_frame = customtkinter.CTkFrame(
            self.bot_page_frame, corner_radius=20, fg_color="#756F8B")
        self.status_frame.pack()
        self.status_frame.place(
            anchor="w", relx=0.05, rely=0.7, relwidth=0.28, relheight=0.1)

        self.debug_switch = customtkinter.CTkSwitch(
            master=self.bot_settings_frame,
            text="Debug mode",
            command=self.debug_switch_handler,
            font=('Twitch Gothic', 12, 'bold')
        )
        self.auto_update_switch = customtkinter.CTkSwitch(
            master=self.bot_settings_frame,
            text="Auto updates",
            command=self.autoupdate_switch_handler,
            font=('Twitch Gothic', 12, 'bold')
        )
        self.bot_settings_title = customtkinter.CTkLabel(
            self.bot_settings_frame, text="Features Settings", text_color="#FEF9EC", font=('Twitch Gothic', 18, 'bold'), anchor="center")
        self.bot_settings_title.place(relx=0.25, rely=0.05)

        self.debug_switch.place(relx=0.05, rely=0.36)
        self.debug_switch.select() if self.chj.get_debug(
        ) == 1 else self.debug_switch.deselect()
        self.auto_update_switch.place(relx=0.05, rely=0.56)
        self.auto_update_switch.select() if self.chj.get_autoupdates(
        ) == 1 else self.auto_update_switch.deselect()
        self.debug_switch.configure(button_color="#08cc56" if self.chj.get_debug(
        ) else "#ff0000")
        self.auto_update_switch.configure(
            button_color="#08cc56" if self.chj.get_autoupdates(
            ) else "#ff0000")
        self.debug_switch.configure(button_hover_color="#036323" if self.chj.get_debug(
        ) else "#983500")
        self.auto_update_switch.configure(
            button_hover_color="#036323" if self.chj.get_autoupdates(
            ) else "#983500")

    def miscellaneous_settings(self):
        self.miscellaneous_frame = customtkinter.CTkFrame(
            self.bot_page_frame, corner_radius=20, fg_color="#756F8B")
        self.miscellaneous_frame.pack()
        self.miscellaneous_frame.place(
            anchor="w", relx=0.35, rely=0.58, relwidth=0.28, relheight=0.1)

        self.max_lines_entry = customtkinter.CTkEntry(
            self.miscellaneous_frame, placeholder_text="Logrint Max Lines", width=80)
        self.max_lines_entry.place(relx=0.5, rely=0.3)
        self.max_lines_entry.insert(0, self.chj.get_max_lines())
        self.max_lines_entry.configure(validate="key", validatecommand=(
            self.register(self.is_numeric_input), "%P"))

        self.prefix_entry = customtkinter.CTkEntry(
            self.miscellaneous_frame, placeholder_text="Default Prefix", width=80)
        self.prefix_entry.place(relx=0.4, rely=0.5)
        self.prefix_entry.insert(0, self.chj.get_prefix())
        self.miscellaneous_title = customtkinter.CTkLabel(
            self.miscellaneous_frame, text="Miscellaneous", text_color="#FEF9EC", font=('Twitch Gothic', 18, 'bold'), anchor="center")
        self.miscellaneous_title.place(relx=0.28, rely=0.05)

        self.log_print_label = customtkinter.CTkLabel(
            self.miscellaneous_frame, text="Logprint Max lines:", text_color="#FEF9EC", font=('Twitch Gothic', 12, 'bold'))
        self.log_print_label.place(relx=0.1, rely=0.3)
        self.prefix_label = customtkinter.CTkLabel(
            self.miscellaneous_frame, text="Default Prefix:", text_color="#FEF9EC", font=('Twitch Gothic', 12, 'bold'))
        self.prefix_label.place(relx=0.1, rely=0.5)
        self.save_button = customtkinter.CTkButton(
            self.miscellaneous_frame, text="Save", fg_color="#08cc56", hover_color="#036323", command=self.save_entry_value, width=80)
        self.save_button.place(relx=0.35, rely=0.75)

    def debug_switch_handler(self):
        self.chj.set_debug(self.debug_switch.get() == 1)
        self.debug_switch.configure(button_color="#08cc56" if self.chj.get_debug(
        ) else "#ff0000")
        self.debug_switch.configure(button_hover_color="#036323" if self.chj.get_debug(
        ) else "#983500")

    def autoupdate_switch_handler(self):
        self.chj.set_autoupdates(self.auto_update_switch.get() == 1)
        self.auto_update_switch.configure(
            button_color="#08cc56" if self.chj.get_autoupdates(
            ) else "#ff0000")
        self.auto_update_switch.configure(
            button_hover_color="#036323" if self.chj.get_autoupdates(
            ) else "#983500")

    def is_numeric_input(self, P):
        if P.isdigit() or (P == "" and len(P) == 0):
            return True
        else:
            return False

    def save_entry_value(self):
        self.prefix_entry_value = self.prefix_entry.get()
        self.max_lines_entry_value = self.max_lines_entry.get()
        self.chj.set_max_lines(int(self.max_lines_entry_value))
        self.chj.set_prefix(self.prefix_entry_value)

    def heart_beat_checker(self):
        temp_dir = tempfile.gettempdir()
        heartbeat_file_path = os.path.join(
            temp_dir, "TwitchDiscordNotifications\\heartbeat.txt")
        with open(heartbeat_file_path, "r") as heartbeat_file:
            last_heartbeat = float(heartbeat_file.read())

        return time.time() - last_heartbeat <= 3

    def unsaved_changes(self):
        prefix_value = self.prefix_entry.get()
        chj_prefix_value = self.chj.get_prefix()
        max_lines_value = self.max_lines_entry.get()
        chj_max_lines_value = self.chj.get_max_lines()
        if prefix_value != chj_prefix_value or max_lines_value != str(chj_max_lines_value):
            self.exit(
                "You have unsaved changes do you still wish to exit?", "Exit and save")
        else:
            self.exit()

    def update_bot_status_label(self):
        if hasattr(self, "bot_status_value"):
            current_text = self.bot_status_value.cget("text")
            is_online = self.heart_beat_checker()

            if is_online and current_text != "ON":
                self.bot_status_value.configure(
                    text="ON", text_color="#00ff00")
            elif not is_online and current_text != "OFF":
                self.bot_status_value.configure(
                    text="OFF", text_color="#ff0000")
        if hasattr(self, "uptime_value"):
            current_text = self.uptime_value.cget("text")
            if is_online:
                variables = others.unpickle_variable()
                date_format = variables["date_format"]
                current_time = datetime.datetime.now()
                start_time = datetime.datetime.strptime(
                    self.chj.get_time(), date_format)
                uptime = current_time - start_time
                uptime = str(uptime).split(".")[0]
                self.uptime_value.configure(
                    text=str(uptime), text_color="#00ff00")
            elif not is_online and current_text != "Bot offline":
                self.uptime_value.configure(
                    text="Bot offline", text_color="#ff0000")

    def start_bot(self):
        if not self.heart_beat_checker():
            script_path = f'{self.cwd}\\main.py'

            try:
                subprocess.Popen(
                    ['start', 'cmd', '/k', 'python', script_path], shell=True)
                print("Bot started in a new console window.")
            except Exception as e:
                print(f"Failed to start the bot: {e}")
        else:
            print("Bot is already running.")

    @Utilities.custom_decorators.run_in_thread
    def stop_bot(self):
        if self.heart_beat_checker():
            pid = self.chj.get_pid()
            try:
                os.kill(pid, 9)
                print(f"Process with PID {pid} has been terminated.")
            except ProcessLookupError:
                print(f"Process with PID {pid} not found.")
            except PermissionError:
                print(
                    f"You don't have permission to terminate the process with PID {pid}.")

    @Utilities.custom_decorators.run_in_thread
    def is_bot_online(self):
        while True:
            self.update_bot_status_label()
            time.sleep(1)

    # TODO logs page
    # TODO Allow .env changes from UI
    # TODO Buttons to go to the default data.db and restarted_data.json location
    # TODO Allow the change of the default locations


if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
