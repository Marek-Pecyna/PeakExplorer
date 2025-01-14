import logging
import FreeSimpleGUI as sg
import numpy as np

from Constants import DEFAULT_ASCII_FILE
import webbrowser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # The matplot tk canvas

alw = b'iVBORw0KGgoAAAANSUhEUgAAAIwAAACqCAYAAAB/NacVAAABhWlDQ1BJQ0MgcHJvZmlsZQAAKJF9kT1Iw0AcxV8/pCoVETuIiGSoThZBRRxLFYtgobQVWnUwufQLmjQkKS6OgmvBwY/FqoOLs64OroIg+AHi6uKk6CIl/i8ptIjx4Lgf7+497t4B3kaFKYY/CiiqqafiMSGbWxUCr+iBHwOYxKjIDC2RXszAdXzdw8PXuwjPcj/35+iT8wYDPAJxlGm6SbxBPLtpapz3iUOsJMrE58QTOl2Q+JHrksNvnIs2e3lmSM+k5olDxEKxg6UOZiVdIZ4hDsuKSvnerMMy5y3OSqXGWvfkLwzm1ZU012mOII4lJJCEAAk1lFGBiQitKikGUrQfc/EP2/4kuSRylcHIsYAqFIi2H/wPfndrFKannKRgDOh6sayPMSCwCzTrlvV9bFnNE8D3DFypbX+1Acx9kl5va+EjoH8buLhua9IecLkDDD1poi7ako+mt1AA3s/om3LA4C3Qu+b01trH6QOQoa6Wb4CDQ2C8SNnrLu/u7uzt3zOt/n4AxnZyyLHBmt4AAAAGYktHRAAAAAAAAPlDu38AAAAJcEhZcwAALiMAAC4jAXilP3YAAAbMSURBVHja7dxdbFPnGcDx57VjJ/42lDHKiGN3mbHTjjRokyZV3dZstJvQGlDLrra7bUWkg0DHNO2m2s0uJg2GQqeRljWCINpVWtUGWkYrbWonTZVWFpGQDEoD8UfaoXzYTiDHJ/Y5u0hSQhLmdJphx/n/7owCQUd/v+9zjo+PCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMpp8NJbztffuOh9pu1jG0fjVlUcglt9dPZ4YNq17pGatZ+pqvEYZ0RkkqNyE++gedJvdgaD4YYdvjXhZ233+L9sd1RxfAhmaYlTR1etqt/0ZE0ottde7YmKsinD5LiwJS0h1f18cHW0aYcrFNstjpqYiNJFTBGCIZhFM8upjkAwunlHTV1stzhq4qKUjVAIZulY3ng+EKjf/N3ZWGKi1K1btCIQgrk5swQD9Q8+4QrFfiwOV1yUsi/8GUUwBCMikuh+Ibgm2vSEq27jHnG4GpaKRUTENAhkxQeTOn3Uv7q+cftsLPcv2oZAMJ/MLGeP+wJ1se2uuti+2W2IWAhmacNnu3yB2uh2V2jjT8Tpjt9uG5o/7zLDrNBgEm8e9wdqoy2uSHy/OD0lY5lTNChmxQWTONPlv6cu2uKONOwXp7thOduQEhGHTRwPfaXgHh5OFAqFZf0qZZrm7NmVMmf/GbPE71HZaWUOZA19x+a6ghWOZ0W/hT46e9zrr924bTaWB5Y7s0yLFK/fkD6XzfxrlcOYWnCczAXHbv7ruUjMEn9HRMRUStTolOjvJbKnL49ef2/vw6ECK8xd8vGfOr2+2ug2dzj+qWIREXGI2AMu2aSUiovYy3rd12kXzS6edPGG9ncRIZi7curc3eHzhRpa3OHYfqn2/FenzkqJEhHnHfjvGqahbFa55lNxwQy9fiSwqr6pxR2J7xOn+/7lDrhYgcEkuzt8q7/Q1OIOx9tmtyHLxGKaBHNnZ5bu33m99Y0t7nB8jzjdm1hZCOb2Z0OvHfb66pu2u8MNbeJ0WTIWq1wktHwwyVef8/miX2pxRxraZlYWGzeFEcxtBtzXjvhXRZse90TmVhbLxqKEGabMp86njnqD931xqyfcsEec7kZRytLxW+UmP0se5H+d6XR7QrGtnkjsGam2fixsSeWcWc4cc3s21H/HE47/VKq9myolFobeMkic/r03WPv5rZ77HqioWFhhymDw2LNO/7o1D3kjG/dKtbex0q6zWOXCnWXuOFM2UTa7WSNiuEVMblQhmP8s8r1f5HPXUn/WEhfaJZ+7JKZRUbdoK4L539vwaGsuk+5/KT/Uc0C0zCUxipUSjWmVYix3E/S932idyA0PvKQle38t+dzFCoqGYMplbfOuiUzywitaqu+g6LmLlbA9MfSWe6X5Zmt25ErPK1PJvkOVONMQTBnUPrY7MzJ47g9asvc3ks9+IIZ1o1HMMHdG6Ftt4+NDPS9ryd6Dks9etnI0BHOHrN+yO5NN9Z3MJ3sPiJ69bMHtyTKfVlfMV0XXNbfmssMDJ2dWmtyHVovGKp9WV9R3iz/7yM7c2NW+k1ri/EHJ5wYZhAmmpM892prNpQdO5BM9B0TLDVklGj6tvpsrTfPO3Mg7HV1KlDhrG/dLjb9OlO1TvTkMUwybkuly7xZKRFPKKMx8u5Zg7po1X/3RxOg7HV0eEVUdenCfVPsiy42mIGJMajLgtpt/q6oytTLGonRT8oZN66vyGEVrTOcV7tpfjvj962Pfr65t3LvcaCZN0d5Pmr8dO3f9l9taHDlNu/kYBzW7d8z74v0tr+f+bOHrpX7GJqZkCjY5N1YsfLvOw7z1/yL91nNB7dK7T5tT4x+YRrFolpAzzKm3rxq/+tnPsz6OXoUPvUsOwltaM9l0f5ee7D0k+dwVMZb3yGaHk/tuVmQwM6fcT2Uy6YEuPXXhkOjLu05j8rzelRvMXDTjyfMn9HR/u+gTg2KWWGkIZmUHIyKyrnnX2MiVf5zIp/sPiz75YclosLKDmZlpnh4dGew5oacvHBY9N3i7mYaHIhLMJzZs2TUyNnS+azrV3y76xNUlVxqCIZj57m3eOZpJ9R2bTve2iz65KBqeBE4wi6z9+lPj4+l/duqp3sOiTw4x0xBM6bOnr/1wfDTR16mn+tpFn0wQDcGUtL5551gm3f/idKr3kKFPDCuzaPJg+cX4bvKClebauy+8WHTZR23ZiEjRwRTDClNipnn4B5mikXrZGB/+Y3bMuMERAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFvFvb+6M1dD/JHkAAAAASUVORK5CYII='
arw = b'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'

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
        font_size = 11
        font_size_title = 15
        default_text = DEFAULT_ASCII_FILE

        if self.settings:
            font = self.settings["GUI"]["font_family"]
            font_size = int(self.settings["GUI"]["font_size"])
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
            sg.B(image_source=alw, image_subsample=5, pad=0, k="-MASS_INTERVAL_DOWN-"),
            sg.B(image_source=arw, image_subsample=5, pad=0, k="-MASS_INTERVAL_UP-")
            ]

        time_frame = [
            sg.Input(s=5, justification="r", key="-TIME-", enable_events=True, tooltip="Ganzzahlige Werte"),
            sg.T("Min", s=3, pad=0),
            sg.T("±", s=1),
            sg.Input("", s=4, pad=0, k="-TIME_INTERVAL-", readonly=True, tooltip="0.1 bis 1.0 Min einstellbar"),
            sg.T("Min", s=3, pad=0, key="-TIME_TEXT2-"),
            sg.B(image_source=alw, image_subsample=5, pad=0, k="-TIME_INTERVAL_DOWN-"),
            sg.B(image_source=arw, image_subsample=5, pad=0, k="-TIME_INTERVAL_UP-")
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
