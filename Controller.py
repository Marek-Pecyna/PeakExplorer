from os import startfile
from pathlib import Path

import configparser
import logging
import matplotlib.pyplot as plt

from Model.Data import Data
from Model.ParseCSV import ParseCSV
from Model.CreateExcel import CreateExcel

__all__ = ["Controller"]
WINDOW_CLOSED = None


class Controller:
    logger = logging.getLogger().getChild(__name__)

    def __init__(self, settings_filename):
        """ Create Controller instance """
        Controller.logger.info('Started.')
        self.view = None
        self.model = None

        # sg variables
        self.window = None
        self.event = None
        self.values = None

        # GUI hardcoded defaults
        self.follow_mass_trace = True
        self.follow_time_trace = True
        self.show_with_matplot = True
        self.open_excel = False
        self.mass = 465  # mass in Dalton
        self.mass_interval = 0.5  # +- deviation in Dalton
        self.time = 4  # elution time in minutes
        self.time_interval = 0.4  # +- time deviation in minutes

        # Loading other settings from config file
        self.settings = None
        if Path(settings_filename).is_file():  # if complete path to file is given
            self.settings_filename = Path(settings_filename)
        else:  # if not, looking in cwd for filename
            settings_path = str(Path.cwd())
            self.settings_filename = Path(settings_path, settings_filename)
        Controller.logger.info(f"{self.settings_filename = }")
        self.load_settings_from_file()

        # Settings for files
        self.ascii_filename = ""
        self.result_filename = ""
        self.output_folder = ""

        # Data storage
        self.summary = None
        self.mass_trace = None
        self.elution_time_trace = None
        self.number_of_entries = None
        self.max_peaks = []
        self.min_peaks = []

        Controller.logger.info('Finished.')
        return

    def load_settings_from_file(self):
        """Load settings from config file. If file not exists or is empty, default values will be used."""
        Controller.logger.info(f"{self.load_settings_from_file.__doc__.split('.')[0]}")
        if Path(self.settings_filename).is_file():
            # create the settings object
            self.settings = configparser.ConfigParser(allow_no_value=True)
            self.settings.read(self.settings_filename)
        if self.settings and self.settings.sections != []:  # config file is present AND contains correct data
            Controller.logger.info("Loaded from config file!")
            if not Path(self.settings['GUI']['last_file']).is_file():
                self.settings['GUI']['last_file'] = ""
        else:
            Controller.logger.warning(f"Error on config file '{self.settings_filename}'."
                                      f" Program defaults will be used.")
            settings_dict = {"GUI": {"font_size": "14",
                                     "font_family": "Arial",
                                     "theme": "Reddit",
                                     "last_file": ""},
                             "CSV": {"delimiter": ",",
                                     "decimal": ".",
                                     "encoding": 'utf-8'},
                             "DATA": {"col_retention": "0",
                                      "col_number_masses": "7",
                                      "col_data_starts": "8",
                                      "col_meaning":
                                          'retention time[min], unused, ionisation, device, unused,'
                                          ' unknown, mass interval, number of masses, mass_space_count'}}
            self.settings = configparser.ConfigParser()
            self.settings.read_dict(settings_dict)
        return

    def set_view(self, view):
        """This function prepares the GUI in a useful state for first usage"""
        Controller.logger.info(f"{self.set_view.__doc__}")
        self.view = view

        plt.close('all')  # if some windows are still open, close them

        if self.settings:
            self.view.update_gui_settings()
            self.view.settings_filename = self.settings_filename

        if Path(self.settings['GUI']['last_file']).is_file():
            self.view.main_window["-IN-"].update(self.settings["GUI"]["last_file"])

        self.view.main_window["-MATPLOT-"].update(self.show_with_matplot)
        self.view.main_window["-EXCEL-"].update(self.open_excel)
        self.view.main_window["-MASS_FRAME-"].update(visible=self.follow_mass_trace)
        self.view.main_window["-MASS_TRACE-"].update(self.follow_mass_trace)

        self.view.main_window["-TIME_FRAME-"].update(visible=self.follow_time_trace)
        self.view.main_window["-ELUTION_TIME_TRACE-"].update(self.follow_time_trace)

        self.view.main_window["-MASS_INTERVAL-"].update(self.mass_interval)
        self.view.main_window["-TIME_INTERVAL-"].update(self.time_interval)
        self.view.main_window["-MASS-"].update(self.mass)
        self.view.main_window["-TIME-"].update(self.time)
        self.view.move_up_left(self.view.main_window)
        return

    def mainloop(self):
        Controller.logger.info('Entering controller mainloop')
        while True:
            self.window, self.event, self.values = self.view.read_all_windows()

            if self.event in (WINDOW_CLOSED, "Beenden"):
                self.window.close()
                if self.window == self.view.result_window:  # if closing result win, mark as closed
                    self.view.result_window = None
                elif self.window == self.view.main_window:  # if closing main win, exit program
                    break
            if self.event in ("-EXIT1-", "-EXIT2-"):
                self.window.close()
                if self.window == self.view.result_window:  # if closing result win, mark as closed
                    self.view.result_window = None
            if self.event == "Öffnen in Excel":
                self.create_excel_file()  # generate Excel file
            if self.event == "Über":
                self.view.about_window()
            if self.event == "Einstellungen":
                settings_to_save = self.view.settings_window()
                if settings_to_save:
                    self.view.update_gui_settings()
                    try:
                        with open(self.settings_filename, 'w') as configfile:
                            self.settings.write(configfile)
                    except Exception as e:
                        text = f"User settings could not be saved to file:\n" \
                               f"'{self.settings_filename}'\n{e}"
                        self.view.popup(title='User Settings save error',
                                        text=text)
                        Controller.logger.error(text)
                    else:
                        # Display success message
                        self.view.popup(title="", text="Einstellungen gespeichert!")
                    self.view.main_window.close()
                    self.view.make_main_window()
                    self.view.move_up_left(self.view.main_window)
                    if self.view.result_window:
                        self.view.result_window.close()
                        self.view.make_result_window(self.ascii_filename,
                                                     self.number_of_entries)
                        # self.view.move_up(self.view.result_window)
                    self.view.main_window["-MASS_INTERVAL-"].update(self.mass_interval)
                    self.view.main_window["-TIME_INTERVAL-"].update(self.time_interval)
                    self.view.main_window["-MASS-"].update(self.mass)
                    self.view.main_window["-TIME-"].update(self.time)
            if self.event == "-IN-":
                if Path(self.values['-IN-']).is_file():
                    self.settings['GUI']['last_file'] = self.values['-IN-']
                else:
                    self.view.main_window['-IN-'].update('')

            if self.event == "-MASS_TRACE-":
                visible = True if self.values["-MASS_TRACE-"] else False
                self.view.main_window["-MASS_FRAME-"].update(visible=visible)
            if self.event == "-ELUTION_TIME_TRACE-":
                visible = True if self.values["-ELUTION_TIME_TRACE-"] else False
                self.view.main_window["-TIME_FRAME-"].update(visible=visible)
            if self.event == '-MASS-':
                if not self.is_int(self.values['-MASS-']):
                    self.view.main_window['-MASS-'].update("")
            if self.event == '-TIME-':
                if not self.is_int(self.values['-TIME-']):
                    self.view.main_window['-TIME-'].update("")
            if self.event == "-MASS_INTERVAL_UP-":
                if self.mass_interval <= 15.9:
                    self.mass_interval += 0.1
                    self.mass_interval = round(self.mass_interval, 1)
                    self.view.main_window["-MASS_INTERVAL-"].update(f"{self.mass_interval:0.1f}")
                else:
                    self.mass_interval = 0.1
                    self.view.main_window["-MASS_INTERVAL-"].update(f"{self.mass_interval:0.1f}")
            if self.event == "-MASS_INTERVAL_DOWN-":
                if self.mass_interval >= 0.2:
                    self.mass_interval -= 0.1
                    self.mass_interval = round(self.mass_interval, 1)
                    self.view.main_window["-MASS_INTERVAL-"].update(f"{self.mass_interval:0.1f}")
                else:
                    self.mass_interval = 16.0
                    self.view.main_window["-MASS_INTERVAL-"].update(f"{self.mass_interval:0.1f}")
            if self.event == "-TIME_INTERVAL_UP-":
                if self.time_interval <= 0.9:
                    self.time_interval += 0.1
                    self.time_interval = round(self.time_interval, 1)
                else:
                    self.time_interval = 0.1
                self.view.main_window["-TIME_INTERVAL-"].update(f"{self.time_interval:0.1f}")
            if self.event == "-TIME_INTERVAL_DOWN-":
                if self.time_interval >= 0.2:
                    self.time_interval -= 0.1
                    self.time_interval = round(self.time_interval, 1)
                else:
                    self.time_interval = 1.0
                self.view.main_window["-TIME_INTERVAL-"].update(f"{self.time_interval:0.1f}")
            if self.event == "-START_BUTTON-":
                self.start_button_pressed()

        self.view.main_window.close()  # Close GUI, return to main()
        return

    def start_button_pressed(self):
        """ Here the analysis and Excel file generation is controlled. """
        Controller.logger.info('Start button was pressed...')

        # Check, if given filepath is valid
        if not Path(self.values['-IN-']).is_file():
            self.view.main_window['-IN-'].update('')
            return

        # Set flags for mass_trace and/or elution_time_trace
        self.follow_mass_trace = True if self.values['-MASS_TRACE-'] else False
        self.follow_time_trace = True if self.values['-ELUTION_TIME_TRACE-'] else False
        self.show_with_matplot = True if self.values['-MATPLOT-'] else False
        self.open_excel = True if self.values['-EXCEL-'] else False
        # Convert GUI entries for mass and time to float -> no ValueError here, because of prefiltering
        self.mass = float(self.values['-MASS-'])
        self.time = float(self.values['-TIME-'])
        self.ascii_filename = self.values['-IN-']
        self.settings['GUI']['last_file'] = self.ascii_filename
        self.output_folder = Path(self.ascii_filename).parent
        Controller.logger.info('Start was button pressed (and all required infos are given by user).')
        Controller.logger.debug(f"{self.ascii_filename = }")
        Controller.logger.debug(f"{self.output_folder = }")
        Controller.logger.debug(f"{self.follow_mass_trace = }, {self.mass = }, {self.mass_interval = }")
        Controller.logger.debug(f"{self.follow_time_trace = }, {self.time = }, {self.time_interval = }")

        # Start analysis -> Results are stored in instance variables
        if not self.analysis():
            Controller.logger.error(f"Error in analyzing file content!")
            title = 'Dateiformat kann nicht gelesen werden!'
            text = [f"Die Datei\n"
                    f"\n'{Path(self.ascii_filename).name}'",
                    '\nkann nicht korrekt als CSV-Datei eingelesen werden.',
                    'Bitte passen Sie die Einstellungen an.']
            self.view.popup(title, "\n".join(text))
            return

        # Generate Excel file
        if self.open_excel:
            self.create_excel_file()

        # Generate Plots
        fig1, fig2 = self.view.plot_canvas(matplot=self.show_with_matplot,
                                           summary=self.summary,
                                           mass=self.mass,
                                           mass_interval=self.mass_interval,
                                           mass_trace=self.mass_trace,
                                           time=self.time,
                                           time_interval=self.time_interval,
                                           elution_time_trace=self.elution_time_trace,
                                           max_peaks=self.max_peaks)

        # Show with Matplot
        if self.show_with_matplot:
            plt.show()
        else:
            # Show in result window
            if self.view.result_window:
                self.view.result_window.close()
            plt.close('all')
            self.view.make_result_window(self.ascii_filename,
                                         self.number_of_entries)
            self.view.draw_figure(self.view.result_window['-CANVAS1-'].TKCanvas, fig1)
            self.view.draw_figure(self.view.result_window['-CANVAS2-'].TKCanvas, fig2)
        return

    def set_csv_settings(self):
        """Set setting for data analysis in Data class"""
        ParseCSV.delimiter = self.settings['CSV']['delimiter']
        ParseCSV.decimal = self.settings['CSV']['decimal']
        ParseCSV.encoding = self.settings['CSV']['encoding']

        ParseCSV.col_retention = int(self.settings['DATA']['col_retention'])
        ParseCSV.col_number_masses = int(self.settings['DATA']['col_number_masses'])
        ParseCSV.col_data_starts = int(self.settings['DATA']['col_data_starts'])
        return

    def analysis(self):
        Controller.logger.info('Data analysis starts.')
        # Set settings for ParseCSV module
        self.set_csv_settings()

        # Read CSV file
        data = ParseCSV.read_csv_file(self.ascii_filename)
        if not data:
            return

        # Get 'Counts per time' and 'Counts per mass'
        Controller.logger.info(f"{len(data)} lines found in file.")
        self.number_of_entries = len(data)
        self.summary = Data.get_total_counts(data)

        # Extract mass trace
        if self.follow_mass_trace:
            self.mass_trace = Data.mass_trace(data=data,
                                              mass=self.mass,
                                              mass_interval=self.mass_interval)
            if self.mass_trace:
                Controller.logger.debug(f"Mass trace entries: {len(self.mass_trace)}")

        # Extract elution time trace
        if self.follow_time_trace:
            self.elution_time_trace = Data.elution_time_trace(data=data,
                                                              time=self.time,
                                                              time_interval=self.time_interval)
            if self.elution_time_trace:
                Controller.logger.debug(f"Time trace entries: {len(self.elution_time_trace)}")

        # Get Peaks in 'Counts per time' graph
        self.max_peaks, self.min_peaks = Data.peakdetect(y_axis=self.summary.total_counts_per_time,
                                                               x_axis=self.summary.elution_times,
                                                               lookahead=50, delta=0)
        Controller.logger.info(f"Data analysis finished.")
        return True

    @staticmethod
    def is_file_in_use(filename):
        if Path(filename).is_file():
            try:
                Path(filename).rename(filename)
            except OSError as error_message:
                Controller.logger.error(f"Zugriffs-Fehler auf Datei '{filename}'! {error_message}")
                return True
        Controller.logger.debug(f"File '{filename}' can be accessed in write-mode.")
        return False

    @staticmethod
    def is_int(text):
        try:
            int(text)
        except ValueError:
            return False
        return True

    @staticmethod
    def create_result_filename(filename):
        """Creating result filename: (Path/)HPLC_MS_filename.xlsx"""
        path = Path(filename).parent
        name = f'HPLC_MS_{Path(filename).name}.xlsx'
        return Path(path, name)

    def set_model(self, model):
        """Setting model for controller"""
        Controller.logger.info(f"{self.set_model.__doc__}")
        self.model = model

    def create_excel_file(self):
        """Create excel-file. Existing file with same name will be overwritten."""
        Controller.logger.info(f"{self.create_excel_file.__doc__}")
        result_filename = self.create_result_filename(self.ascii_filename)
        Controller.logger.info(f"{result_filename = }")

        # Check if file is in use
        if self.is_file_in_use(result_filename):
            title = 'Datei bereits geöffnet!'
            text = f"Die Datei\n\n{Path(result_filename).name}\n\nist bereits in einer anderen Anwendung geöffnet.\n" + \
                   "Bitte schließen diese Anwendung.\n"
            self.view.popup(title, text)
            return

        # Generation of Result-Excel-File
        Controller.logger.info(f"Generation of Excel file:")
        data1 = list(zip(self.summary.elution_times, self.summary.total_counts_per_time, self.mass_trace))\
            if self.mass_trace \
            else list(zip(self.summary.elution_times, self.summary.total_counts_per_time))

        data2 = list(zip(self.summary.ion_masses, self.summary.total_counts_per_mass, self.elution_time_trace)) \
            if self.elution_time_trace\
            else list(zip(self.summary.ion_masses, self.summary.total_counts_per_mass))

        modes = {"counts_per_time": {"data": data1, "trace": 0, "deviation": 0.0},
                 "counts_per_mass": {"data": data2, "trace": 0, "deviation": 0.0}
                 }
        if self.follow_mass_trace:
            modes["counts_per_time"]["trace"] = self.mass
            modes["counts_per_time"]["deviation"] = self.mass_interval

        if self.follow_time_trace:
            modes["counts_per_mass"]["trace"] = self.time
            modes["counts_per_mass"]["deviation"] = self.time_interval

        Controller.logger.info(f"Aufruf '{CreateExcel.create_excel_file.__name__}':")
        CreateExcel.create_excel_file(modes=modes,
                                      excel_filename=Path(self.output_folder, result_filename),
                                      source_filename=self.ascii_filename)

        Controller.logger.info(f"Öffnen der Ergebnis-Exceldatei.")
        startfile(result_filename)
        return


def module_testing():
    """Module testing"""
    print(f"Testing module '{__file__}'")
    controller = Controller('config.ini')

    for var in vars(controller):
        print(f"{var:_<40}{repr(vars(controller)[var])}")


if __name__ == '__main__':
    module_testing()
