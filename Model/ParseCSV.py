from collections import namedtuple
import csv
import logging

__all__ = ['ParseCSV']
Line = namedtuple('Line', ['elution_time', 'mass_count_list'])
MassCount = namedtuple('MassCount', ['mass', 'count'])


class ParseCSV:
    """
    Parse HPLC-MS raw data from special-formatted CSV files to a defined format for later analysis
    """
    logger = logging.getLogger().getChild(__name__)  # Start logger

    # CSV constants
    delimiter = ','
    decimal = '.'
    quotechar = '"'
    quoting = csv.QUOTE_NONNUMERIC  # means quotes everything except integers and floats
    encoding = 'utf8'

    # Special constants for parsing this special HPLC-MS format
    col_retention = 0
    col_number_masses = 7
    col_data_starts = 8

    @classmethod
    def read_csv_file(cls, csv_filename):
        cls.logger.info(f"Parsing of {csv_filename}")
        data = []
        errors = []
        with open(csv_filename, newline='', encoding=cls.encoding) as csvfile:
            reader = csv.reader(csvfile, delimiter=cls.delimiter)
            try:
                for line in reader:
                    # ONLY THIS FUNCTION decide how format will be parsed!
                    new_line = cls.make_correct_format_hplc_ms(reader.line_num, line)
                    if new_line:
                        data.append(new_line)
                    else:
                        errors.append(reader.line_num)
            except (csv.Error, UnicodeDecodeError) as e:
                cls.logger.critical('file {}, line {}: {}'.format(csv_filename, reader.line_num, e))
                return None
        if errors:
            cls.logger.critical(f"File '{csv_filename}' contains errors in {len(errors)} lines.")
            return None
        return data

    @classmethod
    def make_correct_format_hplc_ms(cls, line_num, line):
        """
        *** Parse 1 line in special HPLC-MS format in *.ascii files ***
        Returns defined format: [elution_time, (mass, counts), (mass, counts),...]
        Returns None if errors during parsing of this line occur
        """
        if len(line) < cls.col_data_starts:  # eine konforme Datenzeile hat mindestens 8 Einträge
            cls.logger.info(f"Wrong format while parsing {line_num}. line.")
            return None

        # Change all decimals to '.' just to be sure
        line = [item.replace(cls.decimal, '.') for item in line]

        # Extract elution time and number of masses
        try:
            elution_time = float(line[cls.col_retention])
            number_of_masses = float(line[cls.col_number_masses])
        except (ValueError, IndexError) as e:
            cls.logger.info(f"{type(e)} while parsing {line_num}. line.")
            return None
        if number_of_masses == 0:  # no masses for this elution time
            cls.logger.warning(f"No masses for {elution_time = } in {line_num = }.")
            return None

        # Create new data 'line' as named tuple
        new_line = Line(elution_time, [])

        # Extract masses with corresponding counts
        line_data = [value.split(" ") for value in line[cls.col_data_starts:]]  # Hardcoded separator!
        for value in line_data:
            try:
                mass = float(value[0])
                count = float(value[1])
            except (ValueError, IndexError) as e:
                cls.logger.info(f"{type(e)} while parsing {line_num}. line.")
                return None
            new_line.mass_count_list.append(MassCount(mass, count))
        return new_line
