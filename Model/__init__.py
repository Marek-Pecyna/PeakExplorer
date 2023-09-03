"""
Parse and analyze HPLC-MS raw data from CSV files (Module Data)
Generate Excel file with results (Module CreateExcel)
"""

# import submodules
from Model.Data import Data  # Data analysis
from Model.CreateExcel import CreateExcel  # Create Excel
from Model.ParseCSV import ParseCSV
__all__ = ['Model', 'Data', 'CreateExcel', 'ParseCSV']


class Model:
    @staticmethod
    def peakdetect(y_axis, x_axis=None, lookahead=200, delta=0):
        return Data.peakdetect(y_axis, x_axis, lookahead, delta)
