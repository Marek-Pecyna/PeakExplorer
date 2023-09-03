import xlsxwriter
import logging
__all__ = ['CreateExcel']


class CreateExcel:
    """ Create specialized Excel file from data in Model with 'chart sheet' followed by 'data sheet'"""
    logger = logging.getLogger().getChild(__name__)  # Start logger
    logger.info('Module imported.')

    source_filename = ""
    excel_filename = ''
    excel_workbook = None

    @classmethod
    def create_excel_file(cls, modes, excel_filename=excel_filename, source_filename=source_filename):
        """Save data to a new created Excel file.
        Parameter 'modes' is a dict of dicts {mode: {trace: ..., deviation: ...}}"""
        cls.logger.debug(f"{cls.create_excel_file.__doc__}")

        # Create new workbook
        cls.create_new_excel_workbook(excel_filename)

        chart_sheet_list = []
        data_sheet_list = []

        # Create chart_sheet
        for mode in modes:
            cls.logger.debug(f"Arbeitsblatt 'Chart {mode.title()}' wird erzeugt.")
            chart_sheet = cls.excel_workbook.add_chartsheet(f'Chart {mode.title()}')
            chart_sheet_list.append(chart_sheet)

        # Create data_sheets and fill corresponding chart_sheets with chart
        for index, mode in enumerate(modes):
            data = modes[mode]["data"]
            trace = modes[mode]["trace"] if "trace" in modes[mode] else 0
            deviation = modes[mode]["deviation"] if "deviation" in modes[mode] else 0

            # Create data_sheet
            cls.logger.debug(f"Arbeitsblatt 'Data {mode.title()}' wird erzeugt.")
            data_sheet = cls.excel_workbook.add_worksheet(f'Data_{mode.title()}')

            # Fill data_sheet with data
            cls.fill_data_sheet(data_sheet, mode, data, trace, deviation, source_filename)
            data_sheet_list.append(data_sheet)

            # Now fill chart_sheet with chart
            show_trace = True if trace != 0 or deviation != 0 else False
            chart = cls.create_chart(mode, data, show_trace=show_trace)
            # Insert the chart into the chart_sheet.
            chart_sheet_list[index].set_chart(chart)

        # Closing of workbook necessary for writing
        cls.excel_workbook.close()
        cls.logger.info('Erzeugung der Ergebnis-Exceldatei beendet.')
        return

    @classmethod
    def create_new_excel_workbook(cls, filename=excel_filename):
        cls.logger.debug('A new Excel file will be created.')
        cls.excel_workbook = xlsxwriter.Workbook(filename)
        return

    @classmethod
    def fill_data_sheet(cls, worksheet, mode, data, trace, deviation, source_filename=source_filename):
        """ Creation of a data sheet in workbook object """
        cls.logger.debug(f"{cls.fill_data_sheet.__doc__}")
        worksheet.freeze_panes(1, 0)
        worksheet.set_landscape()  # set landscape orientation for printing
        worksheet.set_paper(9)  # A4-Format
        worksheet.set_zoom(100)

        # Define formats
        underline_format = cls.excel_workbook.add_format({'bottom': True})
        float_format = cls.excel_workbook.add_format({'num_format': '#,##0.000;;[Red] 0'})
        # float_format.set_num_format('0.000; [Red] (-0.000); 0')

        # Generate header lines
        if mode == "counts_per_time":
            worksheet.write(0, 0, "Elution time [min]", underline_format)
            worksheet.write(0, 1, "Total counts", underline_format)
            if trace != 0:
                worksheet.write(0, 2, f"Counts for mass trace {trace}±{deviation} Da", underline_format)
        else:
            worksheet.write(0, 0, "Ion masses [Da]", underline_format)
            worksheet.write(0, 1, "Summed up total counts", underline_format)
            if trace != 0:
                worksheet.write(0, 2, f"Counts for minute trace {trace}±{deviation} Min", underline_format)

        worksheet.set_column(0, 2, 22)
        cls.logger.debug(f"Länge: {len(data)}")
        cls.logger.debug(data[0])
        for index, entry in enumerate(data):
            worksheet.write(1 + index, 0, entry[0], float_format)
            worksheet.write(1 + index, 1, entry[1], float_format)
            if trace != 0:
                worksheet.write(1 + index, 2, entry[2], float_format)
        worksheet.write(0, 5, f"HPLC-MS-Data derived from '{source_filename}'")
        return

    @classmethod
    def create_chart(cls, mode, data, show_trace):
        """ Creation of a chart in workbook object """
        cls.logger.debug(f"{cls.fill_data_sheet.__doc__}")
        # Create a new chart object.
        chart = cls.excel_workbook.add_chart({'type': 'scatter',
                                              'subtype': 'straight'})

        # Add a series to the chart.
        chart.add_series({
            'name': f'=Data_{mode.title()}!$B$1',
            'categories': f'=Data_{mode.title()}!$A$2:$A${len(data)+1}',
            'values': f'=Data_{mode.title()}!$B$2:$B${len(data)+1}',
            'line': {'width': 1.25,
                     'color': '#4472C4'}})

        if show_trace:  # show mass trace or elution_time trace
            chart.add_series({
                'name': f'=Data_{mode.title()}!$C$1',
                'categories': f'=Data_{mode.title()}!$A$2:$A${len(data)+1}',
                'values': f'=Data_{mode.title()}!$C$2:$C${len(data)+1}',
                'line':   {'width': 1.25,
                           'color': '#ED7D31'}})

        # Set an Excel chart style.
        # chart.set_style(13)

        if mode == "counts_per_time":
            title = f"""HPLC-MS Chromatogram"""
            chart.set_title({'name': title})
            chart.set_x_axis({'name': 'Elution time [min]',
                              'num_format': '0.0'})
            chart.set_y_axis({'name': 'Counts',
                              'num_format': '#,##0'})
        elif mode == "counts_per_mass":
            title = f"""Mass spectrum (HPLC-MS)"""
            chart.set_title({'name': title})
            chart.set_x_axis({'name': 'Ion masses [Da]',
                              'num_format': '0.0'})
            chart.set_y_axis({'name': 'Counts',
                              'num_format': '#,##0'})
        return chart
