import logging
import FreeSimpleGUI as sg
import numpy as np

from Constants import DEFAULT_ASCII_FILE
import webbrowser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # The matplot tk canvas

__all__ = ['View']


class View:
    """ Class for Main-GUI """
    logger = logging.getLogger().getChild(__name__)

    def __init__(self, title="", settings=None):
        View.logger.info('Started.')
        self.title = title
        self.settings_filename = ""
        self.settings = settings
        self.update_gui_settings()
        self.main_window = None
        self.result_window = None
        self.make_main_window()
        # self.make_result_window()
        View.logger.info('Finished.')
        return

    @staticmethod
    def read_all_windows():
        return sg.read_all_windows()

    def make_main_window(self):
        """ Define and creates main application window with PySimpleGUI """
        View.logger.info(f"{self.make_main_window.__doc__}")

        # ------ Menu Definition ------ #
        menu_def = [
            ["&Datei", ["&Beenden"]],
            ["&Hilfe", ["&Über", "&Einstellungen"]]
        ]

        # ------ GUI Definition ------ #
        file_types = (("Ascii-Dateien", "*.ascii"),
                      ("Text-Dateien", "*.txt"),
                      ("CSV-Dateien", "*.csv"),
                      ("Alle Dateien", "*.*"),)
        font = "Arial"
        font_size_title = 15
        default_text = DEFAULT_ASCII_FILE

        if self.settings:
            font = self.settings["GUI"]["font_family"]
            font_size_title = int(int(self.settings["GUI"]["font_size"]) * 1.4)
            if self.settings["GUI"]["last_file"] != "":
                default_text = self.settings["GUI"]["last_file"]

        header = sg.Text("Konvertierung von HPLC-MS-Rohdaten in x-y-Werte", font=(font, font_size_title),
                         expand_x=True, justification="c")

        source_file_layout = [
            [sg.Input(key="-IN-", s=40, enable_events=True,
                      readonly=True, expand_x=True,
                      default_text=default_text),
             sg.FileBrowse(button_text="Datei", s=14,
                           file_types=file_types)],
        ]

        source_file_frame = sg.Frame("Datei auswählen", source_file_layout, pad=(0, 10),
                                     key='-SOURCE_FRAME-', expand_x=True)

        mass_frame = [
            sg.Input(s=5, justification="r", key='-MASS-', enable_events=True, tooltip="Ganzzahlige Werte"),
            sg.T("Da", s=3, pad=0),
            sg.T("±", s=1),
            sg.Input("", s=4, pad=0, k="-MASS_INTERVAL-", readonly=True, tooltip="0.1 bis 16.0 Da einstellbar"),
            sg.T("Da", s=3, pad=0, key='-MASS_TEXT2-'),
            sg.B("🡄", pad=0, button_color="grey", k="-MASS_INTERVAL_DOWN-"),
            sg.B("🡆", pad=0, button_color="grey", k="-MASS_INTERVAL_UP-")
            ]

        time_frame = [
            sg.Input(s=5, justification="r", key="-TIME-", enable_events=True, tooltip="Ganzzahlige Werte"),
            sg.T("Min", s=3, pad=0),
            sg.T("±", s=1),
            sg.Input("", s=4, pad=0, k="-TIME_INTERVAL-", readonly=True, tooltip="0.1 bis 1.0 Min einstellbar"),
            sg.T("Min", s=3, pad=0, key="-TIME_TEXT2-"),
            sg.B("🡄", pad=0, button_color="grey", k="-TIME_INTERVAL_DOWN-"),
            sg.B("🡆", pad=0, button_color="grey", k="-TIME_INTERVAL_UP-")
            ]

        compute_layout = [
            [sg.Check("Verfolgen einer Massenspur", default=True, enable_events=True,
                      key="-MASS_TRACE-", s=30),
             sg.Frame(title="", layout=[mass_frame], key='-MASS_FRAME-', vertical_alignment="top", relief=sg.RELIEF_FLAT)],
            [sg.Check("Verfolgen eines Elutionszeitpunktes", default=True, enable_events=True,
                      key="-ELUTION_TIME_TRACE-", s=30),
             sg.Frame(title="", layout=[time_frame], key='-TIME_FRAME-', vertical_alignment="top", relief=sg.RELIEF_FLAT)],
            [sg.Check("Anzeige mit Matplotlib", default=False,
                      key="-MATPLOT-", s=30)],
            [sg.Check("Öffnen in Excel", default=False,
                      key="-EXCEL-", s=30)]
        ]

        compute_frame = sg.Frame("Optionale Parameter", compute_layout, pad=(0, 10), expand_x=True)

        layout = [
            [sg.Menu(menu_def, tearoff=False)],
            [header],
            [source_file_frame],
            [compute_frame],
            [sg.B("Auswertung starten", button_color="tomato", s=16, key='-START_BUTTON-',
                  bind_return_key=True, expand_x=True)],
            [sg.VPush()],
            [sg.Sizegrip()]
        ]
        self.main_window = sg.Window(title=self.title,
                                     layout=layout,
                                     finalize=True,
                                     grab_anywhere=True,
                                     resizable=True)
        self.main_window.set_min_size(self.main_window.size)
        return

    def make_settings_window(self, settings_filename=""):
        """
        Define and creates settings window with PySimpleGUI.
        Reads all settings from dict 'self.setting'.
        Default parameter 'settings_filename' is used for window title.
        """
        text = ' '.join([line.strip() for line in self.make_settings_window.__doc__.split('\n') if line != ''])
        View.logger.info(f"{text}")
        if self.settings:
            layout = []
            text_size = 25
            combo_size = 20
            input_size = 50
            current_theme = sg.theme()
            for section in self.settings.sections():
                layout.append([sg.Text(section)])
                for item in self.settings[section]:
                    if item == "theme":
                        layout.append([
                            sg.Text(item, s=text_size, justification="r"),
                            sg.Combo(values=sg.theme_list(), s=combo_size, key=f"-{item.upper()}-",
                                     default_value=current_theme,
                                     readonly=True,
                                     enable_events=True)], )
                    elif item == "font_size":
                        fonts = list(range(8, 19))
                        current_font_size = self.settings["GUI"]["font_size"]
                        layout.append([
                            sg.Text(item, s=text_size, justification="r"),
                            sg.Combo(values=fonts, s=combo_size, key=f"-{item.upper()}-",
                                     default_value=current_font_size,
                                     readonly=True,
                                     enable_events=True)])
                    elif item == "font_family":
                        fonts = sg.Text.fonts_installed_list()
                        current_font_family = self.settings["GUI"]["font_family"]
                        layout.append([
                            sg.Text(item, s=text_size, justification="r"),
                            sg.Combo(values=fonts, s=combo_size, key=f"-{item.upper()}-",
                                     default_value=current_font_family,
                                     readonly=True,
                                     enable_events=True)])
                    else:
                        if len(self.settings[section][item]) > input_size:
                            layout.append([
                                sg.Text(item, s=text_size, justification="r"),
                                sg.Multiline(self.settings[section][item], s=(input_size, 2), enable_events=True,
                                             expand_x=True, expand_y=True, justification='left',
                                             key=f"-{item.upper()}-")
                            ])
                        else:
                            layout.append([
                                sg.Text(item, s=text_size, justification="r"),
                                sg.Input(self.settings[section][item], s=input_size,
                                         key=f"-{item.upper()}-")
                            ])
                layout.append([sg.HSeparator()])

            scroll_column = sg.Column(layout=layout, scrollable=True, vertical_scroll_only=True,
                                      expand_x=True, expand_y=True, pad=(0, 0))
            win_layout = [
                [scroll_column],
                [sg.Push(), sg.Button("Speichern", s=20, bind_return_key=True), sg.Push(), sg.Sizegrip()]
            ]
            return sg.Window(f'Einstellungen "{settings_filename}"',
                             layout=win_layout, finalize=True, grab_anywhere=True,
                             use_custom_titlebar=True, modal=True, resizable=True)

    def settings_window(self) -> bool:
        """
        Shows setting window and manage user interactions
        :return True, if settings should be saved. False, if not:
        """
        View.logger.info(f'Anzeige des Settings-Windows *und* Auswertung der User-Interaktion.')
        window = self.make_settings_window(self.settings_filename)
        window.set_min_size(window.size)
        current_theme = self.settings['GUI']['THEME']
        current_font = self.settings['GUI']['FONT_FAMILY']
        current_font_size = self.settings['GUI']['FONT_SIZE']
        while True:
            event, values = window.read()
            if event == sg.WINDOW_CLOSED:
                return False
            if event == "Speichern":
                for section in self.settings.sections():
                    for item in self.settings[section]:
                        self.settings[section][item] = str(values[f"-{item.upper()}-"])
                window.close()
                return True
            # if the theme was changed, restart the window
            if event in ['-THEME-', '-FONT_SIZE-', '-FONT_FAMILY-']:
                self.settings['GUI']['THEME'] = str(values['-THEME-'])
                self.settings['GUI']['FONT_FAMILY'] = str(values['-FONT_FAMILY-'])
                self.settings['GUI']['FONT_SIZE'] = str(values['-FONT_SIZE-'])
                self.update_gui_settings()
                window.close()
                window = self.make_settings_window(self.settings_filename)
                self.settings['GUI']['THEME'] = current_theme
                self.settings['GUI']['FONT_FAMILY'] = current_font
                self.settings['GUI']['FONT_SIZE'] = current_font_size
                self.update_gui_settings()

    def about_window(self):
        """ Show a small modal 'About' window with contact information """
        View.logger.info(f'{self.about_window.__doc__}')
        window_title = "Über..."
        text = ["Anzeige von Massenspuren in HPLC-MS-Daten",
                "Nach Auswertung wird eine xlsx-Datei erzeugt und automatisch geöffnet.",
                "Dieses Programm darf frei verwendet und weiter gegeben werden.",
                "",
                ]
        layout = [[sg.T(self.title, font=("Arial", 15), text_color="red")]]

        for line in text:
            layout.append([sg.T(line)])
        layout.append([sg.T("Entwickelt von Datenanalyse Dr. Pecyna", font=("Arial", 15))])
        layout.append([sg.B("E-Mail", use_ttk_buttons=True,
                       expand_x=True,
                       key="-EMAIL-")])
        layout.append([sg.B("https://daten-entdecker.de", use_ttk_buttons=True,
                       expand_x=True,
                       key="-WEBSITE-")])
        choice, _ = sg.Window(window_title, layout=layout,
                              use_custom_titlebar=True,
                              modal=True,
                              grab_anywhere=True).read(close=True)
        if choice == "-WEBSITE-":
            webbrowser.open_new_tab(r'https://daten-entdecker.de')
        if choice == "-EMAIL-":
            webbrowser.open_new_tab(f"mailto:info@daten-entdecker.de?subject='Contact {self.title}'")
        return

    def make_result_window(self, filename="",
                           number_of_entries=0):
        """ Define and creates result window """
        View.logger.info(f"{self.make_result_window.__doc__}")

        # ------ Menu Definition ------ #
        menu_def = [
            ["&Datei", ["Öffnen in &Excel", "---", "&Beenden"]]]

        # ------ GUI Definition ------ #
        font = "Arial"
        font_size_title = 15

        if self.settings:
            font = self.settings["GUI"]["font_family"]
            font_size_title = int(int(self.settings["GUI"]["font_size"]) * 1.4)

        header = sg.Text(f"Auswertung",
                         expand_x=True, justification="c", font=(font, font_size_title))

        result1_layout = [
                         [sg.Canvas(key='-CANVAS1-', expand_x=True, expand_y=True)],
                         [sg.Button('Exit', key="-EXIT1-")]
                         ]

        result2_layout = [
                         [sg.Canvas(key='-CANVAS2-', expand_x=True, expand_y=True)],
                         [sg.Button('Exit', key="-EXIT2-")]
                         ]

        tab = sg.TabGroup([
            [sg.Tab('Counts per time', result1_layout, background_color='darkseagreen'),
             sg.Tab('Counts per mass', result2_layout, background_color='darkslateblue')]],
                          key='-TAB_GROUP-', expand_x=True, expand_y=True)

        layout = [
            [sg.Menu(menu_def, tearoff=False)],
            [header],
            [tab],
            # [sg.VPush()],
            [sg.StatusBar(f"Datei: {filename}\n"
                          f"Einträge: {number_of_entries} Zeilen"), sg.Sizegrip()]
        ]

        self.result_window = sg.Window(title='Auswertung',
                                       layout=layout,
                                       finalize=True,
                                       grab_anywhere=True,
                                       resizable=True,
                                       element_justification='right')
        # self.result_window.set_min_size(self.main_window.size)
        return

    @staticmethod
    def draw_figure(canvas, figure):
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        return figure_canvas_agg

    @staticmethod
    def move_up(window):
        screen_width, screen_height = window.get_screen_dimensions()
        win_width, win_height = window.size
        x, y = (screen_width - win_width) // 2, 0
        window.move(x, y)

    @staticmethod
    def move_up_left(window):
        screen_width, screen_height = window.get_screen_dimensions()
        win_width, win_height = window.size
        x, y = 0, 0
        window.move(x, y)

    def update_gui_settings(self):
        """ Update GUI settings from dict 'self.settings' passed during __init__ """
        if self.settings:
            View.logger.debug(f"{self.update_gui_settings.__doc__}")
            theme = self.settings["GUI"]["theme"]
            font_family = self.settings["GUI"]["font_family"]
            font_size = int(self.settings["GUI"]["font_size"])
            font_style = "normal"  # italic roman bold normal underline overstrike
            sg.theme(theme)
            sg.set_options(font=(font_family, font_size, font_style))
        return

    @staticmethod
    def not_implemented():
        View.logger.debug(f'Nicht-implementiert-Window wird angezeigt.')
        sg.popup_error("Funktion noch nicht implementiert.")
        return

    @staticmethod
    def popup(title, text):
        sg.popup(text, title=title)
        return

    def plot_canvas(self, matplot, summary, mass, mass_interval, mass_trace, time, time_interval, elution_time_trace, max_peaks):
        number_masses_per_time = summary.number_of_masses_per_time
        max_mass_per_time = summary.max_mass_per_time
        min_mass_per_time = summary.min_mass_per_time
        ion_masses = summary.ion_masses
        counts_per_mass = summary.total_counts_per_mass

        # fig1, (ax1, ax2) = plt.subplots(1, 2)
        fig1, (ax1) = plt.subplots()
        ax1.plot(summary.elution_times, summary.total_counts_per_time, color='blue', label='Total counts')
        if mass_trace:
            ax1.plot(summary.elution_times, mass_trace,
                     color='red',
                     label=f"Counts for mass trace {mass} ± {mass_interval} Da.")
        ax1.set_xlabel('Elution time [min]')
        ax1.set_ylabel('Counts')
        ax1.legend(loc='upper left', ncol=1)
        ax1.set_title('Counts per Time')

        # Make data to numpy-arrays for detected peaks
        x_max = np.array([value[0] for value in max_peaks])
        y_max = np.array([value[1] for value in max_peaks])
        ax1.scatter(x_max, y_max, color='green', label='Maxima')
        ax1.legend(loc='upper left', ncol=1)
        # ax1.scatter(x_min, y_min, color='red')

        fig2, ax2 = plt.subplots()
        ax2.plot(summary.ion_masses, summary.total_counts_per_mass,
                 color='blue', label='Summed up total counts')
        if elution_time_trace:
            ax2.plot(summary.ion_masses, elution_time_trace, color='orange',
                     label=f"Counts for minute trace {time} ± {time_interval} min.")
        ax2.set_xlabel('Ion masses [Da]')
        ax2.set_ylabel('Counts')
        ax2.legend(loc='upper left', ncol=1)
        ax2.set_title('Counts per Mass')
        """
        if matplot:
            plt.show()
        else:
            self.draw_figure(self.result_window['-CANVAS1-'].TKCanvas, fig1)
            self.draw_figure(self.result_window['-CANVAS2-'].TKCanvas, fig2)
        """
        return fig1, fig2


def module_test():
    """Module testing"""
    import configparser

    print("Module Testing")
    settings_dict = {"GUI": {"font_size": "14",
                             "font_family": "Arial",
                             "theme": "Reddit"},
                     "CSV": {"separator": ",",
                             "decimal": ".",
                             "column_retention": "0",
                             "column_number_of_masses": "7",
                             "column_data_starts": "8",
                             "column_meaning": """retention, time[min], unused, ionisation, device, unused, 
                                         unknown, mass interval, number of masses, mass_space_count"""}}
    settings = configparser.ConfigParser()
    settings.read_dict(settings_dict)

    v = View("View Module Testing", settings)
    while True:
        event, values = v.main_window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break
        if event == "Einstellungen":
            v.make_settings_window('Config.ini')
    return


if __name__ == '__main__':
    module_test()
