from collections import namedtuple
import logging
import numpy as np

__all__ = ['Data']
Line = namedtuple('Line', ['elution_time', 'mass_count_list'])
MassCount = namedtuple('MassCount', ['mass', 'count'])
Summary = namedtuple('Summary', ['elution_times',
                                 'total_counts_per_time',
                                 'total_masses_per_time',
                                 'number_of_masses_per_time',
                                 'max_mass_per_time',
                                 'min_mass_per_time',
                                 'ion_masses',
                                 'total_counts_per_mass'])


class Data:
    """
    Calculate 'counts per time' (Chromatogram) with optional mass trace
    Calculate 'counts per mass' (Mass spectrum) with optional elution time trace
    """
    logger = logging.getLogger().getChild(__name__)  # Start logger
    logger.info('Module imported.')

    @staticmethod
    def get_total_counts(data: [Line]):
        elution_times = []
        total_counts_per_time = []
        total_masses_per_time = []
        number_of_masses_per_time = []
        max_mass_per_time = []
        min_mass_per_time = []

        for line in data:
            # for each line get 'elution_time' and calculate 'total counts' and 'total mass'
            elution_times.append(line.elution_time)
            total_counts_per_time.append(sum([item.count for item in line.mass_count_list]))
            total_masses_per_time.append(sum([item.mass for item in line.mass_count_list]))
            number_of_masses_per_time.append(len(line.mass_count_list))
            max_mass_per_time.append(max([item.mass for item in line.mass_count_list]))
            min_mass_per_time.append(min([item.mass for item in line.mass_count_list]))

        ion_masses_dict = {}
        for line in data:
            # Sum up for every line counts for every mass
            for mass, count in line.mass_count_list:
                # if mass already in dict, sum up counts
                if mass in ion_masses_dict:
                    ion_masses_dict[mass] += count
                else:
                    ion_masses_dict[mass] = count

        ion_masses = sorted(list(ion_masses_dict.keys()))  # Sort keys
        total_counts_per_mass = [ion_masses_dict[key] for key in ion_masses]  # ...and values

        return Summary(elution_times=elution_times,
                       total_counts_per_time=total_counts_per_time,
                       total_masses_per_time=total_masses_per_time,
                       number_of_masses_per_time=number_of_masses_per_time,
                       max_mass_per_time=max_mass_per_time,
                       min_mass_per_time=min_mass_per_time,
                       ion_masses=ion_masses,
                       total_counts_per_mass=total_counts_per_mass)

    @classmethod
    def mass_trace(cls, data: [Line], mass=0, mass_interval=0):
        """
        Calculates mass_trace in 'counts per elution time'
        Returns: 1-D list or None
        """

        low = round(mass - mass_interval, 1)
        lower_limit = low if low > 0 else 0
        upper_limit = round(mass + mass_interval, 1)

        # Check for correct mass
        trace = True if upper_limit > 0 else False  # Masses weigh more than 0 Da :-)
        Data.logger.debug(f"{trace = }, Mass: {lower_limit}-{upper_limit} Da")

        if trace:
            trace_counts = []
            for line in data:
                trace_counts.append(sum([item.count
                                        for item in line.mass_count_list
                                        if lower_limit <= item.mass <= upper_limit]))
            return trace_counts
        return None

    @classmethod
    def elution_time_trace(cls, data: [Line], time=0, time_interval=0):
        """
        Calculates elution_time_trace in 'counts per mass'
        Returns: 1-D list or None
        """

        low = round(time - time_interval, 1)
        lower_limit = low if low > 0 else 0
        upper_limit = round(time + time_interval, 1)

        # Check if there is a specific mass given to trace
        trace = True if upper_limit > 0 else False
        Data.logger.debug(f"{trace = }, Time: {lower_limit}-{upper_limit} Min")

        if trace:
            ion_masses_dict = {}
            for line in data:
                correct_elution_time = True if lower_limit <= line.elution_time <= upper_limit else False
                for mass, count in line.mass_count_list:
                    if correct_elution_time:
                        # if mass already in dict, sum up counts
                        if mass in ion_masses_dict:
                            ion_masses_dict[mass] += count
                        else:
                            ion_masses_dict[mass] = count
                    else:
                        if mass not in ion_masses_dict:  # Don't count masses outside correct elution time
                            ion_masses_dict[mass] = 0

            ion_masses = sorted(list(ion_masses_dict.keys()))  # Sort keys
            return [ion_masses_dict[key] for key in ion_masses]  # ...and values

        return None

    @classmethod
    def peakdetect(cls, y_axis, x_axis=None, lookahead=200, delta=0):
        """
        Converted from/based on a MATLAB script at:
        http://billauer.co.il/peakdet.html

        function for detecting local maxima and minima in a signal.
        It discovers peaks by searching for values which are surrounded by lower
        or larger values for maxima and minima respectively

        keyword arguments:
        y_axis -- A list containing the signal over which to find peaks

        x_axis -- A x-axis whose values correspond to the y_axis list and is used
            in the return to specify the position of the peaks. If omitted an
            index of the y_axis is used.
            (default: None)

        lookahead -- distance to look ahead from a peak candidate to determine if
            it is the actual peak
            (default: 200)
            '(samples / period) / f' where '4 >= f >= 1.25' might be a good value

        delta -- this specifies a minimum difference between a peak and
            the following points, before a peak may be considered a peak. Useful
            to hinder the function from picking up false peaks towards to end of
            the signal. To work well delta should be set to delta >= RMSnoise * 5.
            (default: 0)
                When omitted delta function causes a 20% decrease in speed.
                When used Correctly it can double the speed of the function

        return: two lists [max_peaks, min_peaks] containing the positive and
            negative peaks respectively. Each cell of the lists contains a tuple
            of: (position, peak_value)
            to get the average peak value do: np.mean(max_peaks, 0)[1] on the
            results to unpack one of the lists into x, y coordinates do:
            x, y = zip(*max_peaks)
        """
        max_peaks = []
        min_peaks = []
        dump = []  # Used to pop the first hit which almost always is false

        # check input data
        x_axis, y_axis = cls._datacheck_peakdetect(x_axis, y_axis)
        # store data length for later use
        length = len(y_axis)

        # perform some checks
        if lookahead < 1:
            raise ValueError("Lookahead must be '1' or above in value")
        if not (np.isscalar(delta) and delta >= 0):
            raise ValueError("delta must be a positive number")

        # maxima and minima candidates are temporarily stored in
        # _max and _min respectively
        _min, _max = np.inf, -np.inf
        min_pos, max_pos = np.NaN, np.NaN

        # Only detect peak if there is 'lookahead' amount of points after it
        for index, (x, y) in enumerate(zip(x_axis[:-lookahead],
                                           y_axis[:-lookahead])):
            this = y
            if this > _max:
                _max = this
                max_pos = x
            if this < _min:
                _min = this
                min_pos = x

        # Only detect peak if there is 'lookahead' amount of points after it
        for index, (x, y) in enumerate(zip(x_axis[:-lookahead],
                                           y_axis[:-lookahead])):
            if y > _max:
                _max = y
                max_pos = x
            if y < _min:
                _min = y
                min_pos = x

            # # # # look for max # # # #
            if y < _max - delta and _max != np.Inf:
                # Maxima peak candidate found
                # look ahead in signal to ensure that this is a peak and not jitter
                if y_axis[index:index + lookahead].max() < _max:
                    max_peaks.append([max_pos, _max])
                    dump.append(True)
                    # set algorithm to only find minima now
                    _max = np.Inf
                    _min = np.Inf
                    if index + lookahead >= length:
                        # end is within lookahead no more peaks can be found
                        break
                    continue
                # else:  #slows shit down this does
                #    _max = ahead
                #    max_pos = x_axis[np.where(y_axis[index:index+lookahead]==_max)]

            # # # # look for min # # # #
            if y > _min + delta and _min != -np.Inf:
                # Minima peak candidate found
                # look ahead in signal to ensure that this is a peak and not jitter
                if y_axis[index:index + lookahead].min() > _min:
                    min_peaks.append([min_pos, _min])
                    dump.append(False)
                    # set algorithm to only find maxima now
                    _min = -np.Inf
                    _max = -np.Inf
                    if index + lookahead >= length:
                        # end is within lookahead no more peaks can be found
                        break
                # else:  #slows shit down this does
                #    _min = ahead
                #    min_pos = x_axis[np.where(y_axis[index:index+lookahead]==_min)]

        # Remove the false hit on the first value of the y_axis
        try:
            if dump[0]:
                max_peaks.pop(0)
            else:
                min_peaks.pop(0)
            del dump
        except IndexError:
            # no peaks were found, should the function return empty lists?
            pass

        return [max_peaks, min_peaks]

    @classmethod
    def _datacheck_peakdetect(cls, x_axis, y_axis):
        if x_axis is None:
            x_axis = range(len(y_axis))

        if len(y_axis) != len(x_axis):
            raise ValueError(
                "Input vectors y_axis and x_axis must have same length")

        # needs to be a numpy array
        y_axis = np.array(y_axis)
        x_axis = np.array(x_axis)
        return x_axis, y_axis
