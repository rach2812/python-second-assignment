"""
    This data analysis application takes in stock market data and applies
    analytical techniques employed by real-world commercial applications.

    The program should load data files (supplied as either CSV or as a Triplet)
    and then add this new data to the existing library of stock, indexed by
    the stock IDs. Additionally, it will execute a few analyses on the data and
    return the results of this analysis.
    
    __author__ = "Rachel Quilligan"
    student number = 42371241
    __email__ = "rachel.quilligan@uqconnect.edu.au"
"""
import stocks

class LoadCSV(stocks.Loader):
    """Load files in CSV format into the application ready for analysing."""
    
    def __init__(self, filename, stocks):
        """Inherits from Loader object for filename and stocks parameters.

        Parameters:
            filename (str): name and location of the file to be read.
            stocks (StockCollection):   Collection of existing stock market data
                                        to which the new data will be added.
        """
        super().__init__(filename, stocks)

    def _process(self, file):
        """Parse the CSV format stock market data and format into TradingData
        class object.

        Next, attaches this TradingData to a Stock object, which is found by
        retrieving information from StockCollection.

        Parameters:
            file (str): The file as identified in __init__ method parameters
            (after being opened using __init__ method)
        """
        for line in file:
            all_data = tuple(line.split(','))
            #Errors identify individual problems with different parts of file
            if len(all_data) != 7:
                raise RuntimeError("Error: not enough parameters in the file.")
            stock_code = all_data[0]
            date, day_open, day_high, day_low, day_close, volume = all_data[1:]
            try:
                day_open = float(day_open)
            except ValueError:
                raise RuntimeError("Error:'day_open' not a float.")
            try:
                day_high = float(day_high)
            except ValueError:
                raise RuntimeError("Error: 'day_high' not a float.")
            try:
                day_low = float(day_low)
            except ValueError:
                raise RuntimeError("Error: 'day_low' not a float.")
            try:
                day_close = float(day_close)
            except ValueError:
                raise RuntimeError("Error: 'day_close' not a float.")
            try:
                volume = int(volume.strip("\n"))
            except ValueError:
                raise RuntimeError("Error: 'volume' not an integer.")
            new_trading_object = stocks.TradingData(date, day_open, day_high, day_low, day_close, volume)
            collection_entry = self._stocks.get_stock(stock_code)
            collection_entry.add_day_data(new_trading_object)

class HighLow(stocks.Analyser):
    """Determines the highest and lowest prices paid for a single stock object
    across all of the data stored for the stock.
    """
    
    def __init__(self):
        self._high = []
        self._low = []

    def process(self, day):
        """Retrieves the high and low prices for a single stock.

        Parameters:
            day (TradingData): Trading data for one stock on one day.
        """
        try:
            self._high.append(day.get_high())
            self._low.append(day.get_low())
        except ValueError:
            raise RuntimeError("The data was invalid. Unable to process.")
        
    def reset(self) :
        """Resets the initialised values to restart the process for a new
        analysis.
        """
        self._high = []
        self._low = []

    def result(self):
        """Returns the result of the analysis.

        Return:
             tuple: The highest and lowest priced stock as a tuple pair. 
        """
        low_value = min(self._low)
        high_value = max(self._high)
        return (high_value, low_value)

class MovingAverage(stocks.Analyser):
    """Calculates the average closing price of a stock of a specified period of
    time.
    """
    
    def __init__(self, num_days):
        """
        Parameters:
                num_days (int): The user-specified number of days over which to
                calculate the average.
        """
        self._num_days = num_days
        self._days_counted = 0
        self._moving_average = []

    def process(self, day):
        """Processes the closing price for required days to prepare analysis.

        Parameters:
            day (TradingData): The day to be analysed.
        """
        try:
            self._days_counted += 1
            self._moving_average.append(day.get_close())
        except ValueError:
            print("There was an error in the data. Function not complete.")
        
    def reset(self):
        """Resets the initialised values to restart the process for a new
        analysis.
        """
        self._days_counted = 0
        self._moving_average = 0

    def result(self):
        """Produces the average for the specified amount of days.

        Return:
            float: Average closing price of stock across specified amount of
            days.
        """
        self._moving_average = self._moving_average[::-1]
        #This flips the list so it is the most recent dates first
        final_figures = self._moving_average[:self._num_days]
        return (sum(final_figures) / self._num_days)

class GapUp(stocks.Analyser):
    """Finds the most recent day where an individual stock's opening price was
    significantly higher than the previous day's closing price.
    """
    
    def __init__(self, delta):
        """
        Parameters:
                delta (float): The user-specified number that indicates
                significance. 
        """
        self._delta = delta
        self._closing_value = None
        self._gap_ups = []

    def process(self, day):
        """Finds all the candidates where the stock's opening price was
        signifcantly higher than the previous day's closing price.

        Parameters:
            day (TradingData): The trading data object to be analysed.
        """
        try:
            #Checks if this day is the first on the list
            if self._closing_value == None:
                self._closing_value = day.get_close()
            else:
                #Adds the day to the list of potentials if it is valid
                if (day.get_open() - self._closing_value) >= self._delta:
                    self._gap_ups.append(day)
                #Changes the variable to the new closing price
                self._closing_value = day.get_close()
        except ValueError:
            raise RuntimeError("There was an error in the data. The file was not processed.")
       
    def reset(self):
        """Resets the initialised values to restart the process for a new
        analysis.
        """
        self._closing_value = None
        self._gap_ups = []

    def result(self):
        """Returns the latest day to have the opening price signifcantly higher
        than the previous day's closing price. If no significant GapUps
        occurred, returns None.

        Return:
            day (TradingData): The most recent day to have a GapUp occur.
        """ 
        if self._gap_ups:
            return self._gap_ups[-1]
        else:
                return None

class LoadTriplet(stocks.Loader):
    """Loads files in triplet form into the application ready for analysing."""
    
    def __init__(self, filename, stocks):
        """Inherits from Loader object for filename and stocks parameters.

        Parameters:
            filename (str): name and location of the file to be read.
            stocks (StockCollection):   Collection of existing stock market data
                                        to which the new data will be added.
        """
        super().__init__(filename, stocks)

    def _process(self, file):
        """Parses through the triplet file, pulling the data from each line to
        form a new TradingData object.

        Next, attaches this TradingData to a Stock object, which is found by
        retrieving information from StockCollection.

        Parameters:
            file (str): The file as identified in __init__ method parameters
            (after being opened using __init__ method)

        """
        count = 0
        stock_code = 0
        date = ""
        day_open = 0
        day_high = 0
        day_low = 0
        day_close = 0
        volume = 0
        for line in file:
            #Aligns data with the correct parameter for a TradingData object
            #and checks for ValueErrors at the same time
            try:
                stock_code, key, data  = line.split(":")
                if  key == "DA":
                    date = data
                elif key == "OP":
                    day_open = float(data)
                elif key == "HI":
                    day_high = float(data)
                elif key == "LO":
                    day_low = float(data)
                elif key == "CL":
                    day_close = float(data)
                elif key == "VO":
                    volume = int(data)
                count += 1
            except ValueError:
                    raise RuntimeError("Error: Invalid data in file. Could not process.")
            #Every six lines form a complete TradingData object, even if the
            #data is out of order, so the program clears that data as a new
            #object and restarts the counter
            if count == 6:
                new_trading_object = stocks.TradingData(date, day_open, day_high, day_low, day_close, volume)
                collection_entry = self._stocks.get_stock(stock_code)
                collection_entry.add_day_data(new_trading_object)
                count = 0

def example_usage () :
    all_stocks = stocks.StockCollection()
    LoadCSV("march1.csv", all_stocks)
    LoadCSV("march2.csv", all_stocks)
    LoadCSV("march3.csv", all_stocks)
    LoadCSV("march4.csv", all_stocks)
    LoadCSV("march5.csv", all_stocks)
    LoadTriplet("feb1.trp", all_stocks)
    LoadTriplet("feb2.trp", all_stocks)
    LoadTriplet("feb3.trp", all_stocks)
    LoadTriplet("feb4.trp", all_stocks)
    volume = stocks.AverageVolume()
    stock = all_stocks.get_stock("ADV")
    stock.analyse(volume)
    print("Average Volume of ADV is", volume.result())
    high_low = HighLow()
    stock.analyse(high_low)
    print("Highest & Lowest trading price of ADV is", high_low.result())
    moving_average = MovingAverage(10)
    stock.analyse(moving_average)
    print("Moving average of ADV over last 10 days is {0:.2f}"
          .format(moving_average.result()))
    gap_up = GapUp(0.011)
    stock = all_stocks.get_stock("YOW")
    stock.analyse(gap_up)
    print("Last gap up date of YOW is", gap_up.result().get_date())

if __name__ == "__main__" :
    example_usage()
