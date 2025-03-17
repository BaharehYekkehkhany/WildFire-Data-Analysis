import os
import json
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def set_plot_font_size(
    font_size: int = 12
) -> None:
    """
    Set the font size of the plot

    Parameters
    ----------
    font_size : int, optional
        The font size of the plot. Default is 12
    """
    plt.rcParams.update({'font.size': font_size})


def visualize_whitesands_F4_results(
    config: dict,
    monthly_filtered_whitesands_F4_data: list,
) -> None:
    """
    A wrapper function to visualize the Whitesands F4 results

    Parameters
    ----------
    config : dict
        The configuration parameters
    monthly_filtered_whitesands_F4_data : list
        The filtered Whitesands F4 data by month
    """
    set_plot_font_size(font_size=11)
    validate_type(config, dict, "config")
    validate_type(monthly_filtered_whitesands_F4_data, list, "filtered_whitesands_f4_data")

    # Create 4 graphs aggregating wind speed and direction data from 2014-2021 categorized by month
    fig, axs = plt.subplots(2, 2)
    fig.suptitle("Wind direction distribution between 2010 and 2021 categorized by month")

    i = 0
    for r in range(2):
        for c in range(2):
            wind_dir_aggregated = monthly_filtered_whitesands_F4_data[i].groupby(
                config["Whitesands_F4_data"]["weather_data"]["wind_direction_column_name"]
            ).size()
            bars = axs[r, c].bar(wind_dir_aggregated.index, wind_dir_aggregated)
            axs[r, c].set_xlabel("Wind direction")
            axs[r, c].set_ylabel("Number of measurements")
            for j, bar in enumerate(bars):
                if bar.get_height() == wind_dir_aggregated.max():
                    bar.set_color("red")
                    # bar.set_label(f"Most frequent wind direction: {wind_dir_aggregated.max()}")
                    y_value = bar.get_height()
                    x_value = bar.get_x() + bar.get_width() / 2
                    axs[r, c].annotate(
                        wind_dir_aggregated.max(),
                        (x_value, y_value),
                        xytext=(0, 0),
                        textcoords="offset points",
                        ha='center',
                        va='bottom',
                    )
                    predominant_wind_dir = wind_dir_aggregated[wind_dir_aggregated == wind_dir_aggregated.max()].index[0]
                    predominant_wind_dir_percentage = round(wind_dir_aggregated.max() / wind_dir_aggregated.sum() * 100)
                    axs[r, c].set_title(f"Month {i + 5} (predominant wdir: {predominant_wind_dir} occuring ~{predominant_wind_dir_percentage}% of the time)")
            i += 1
    plt.show()

    # Create 4 graphs averaging minimum and maximum temperatures of the month from 2014-2021
    fig, axs = plt.subplots(2, 2)
    fig.suptitle("Monthly averaged min and max temperatures between 2010 and 2021")

    i = 0
    for r in range(2):
        for c in range(2):
            annual_aggregated = monthly_filtered_whitesands_F4_data[i].groupby("year").size().index
            average_min_temp = monthly_filtered_whitesands_F4_data[i].groupby("year")["minimum_temperature"].mean()
            average_max_temp = monthly_filtered_whitesands_F4_data[i].groupby("year")["maximum_temperature"].mean()
            relative_humidity = monthly_filtered_whitesands_F4_data[i].groupby("year")["relative_humidity"].mean()
            # Add regression line to plot
            min_reg_coef = np.polyfit(annual_aggregated, average_min_temp, 1)
            p_min = np.poly1d(min_reg_coef)
            max_reg_coef = np.polyfit(annual_aggregated, average_max_temp, 1)
            p_max = np.poly1d(max_reg_coef)
            humidity_reg_coef = np.polyfit(annual_aggregated, relative_humidity, 1)
            p_humidity = np.poly1d(humidity_reg_coef)
            axs[r, c].plot(
                annual_aggregated,
                average_min_temp,
                c='green',
            )
            axs[r, c].plot(
                annual_aggregated,
                average_max_temp,
                c='red',
            )
            axs[r, c].plot(
                annual_aggregated,
                relative_humidity,
                c='blue',
            )
            axs[r, c].plot(
                annual_aggregated,
                p_min(annual_aggregated),
                c='green',
                linestyle='dashed',
                label=f'Min temperature regression line ({min_reg_coef[0]:.2f} slope)',
            )
            axs[r, c].plot(
                annual_aggregated,
                p_max(annual_aggregated),
                c='red',
                linestyle='dashed',
                label=f'Max temperature regression line ({max_reg_coef[0]:.2f} slope)',
            )
            axs[r, c].plot(
                annual_aggregated,
                p_humidity(annual_aggregated),
                c='blue',
                linestyle='dashed',
                label=f'Relative humidity regression line ({humidity_reg_coef[0]:.2f} slope)',
            )
            axs[r, c].set_xlabel("Year")
            axs[r, c].set_ylabel("Average min and max temperatures \n and relative humidity")
            axs[r, c].set_title(f"Month {i + 5}")
            axs[r, c].legend()
            i += 1
    plt.show()


def visualize_nfdb_results(
    config: dict,
    filtered_nfdb_data_large_fires: gpd.GeoDataFrame,
) -> None:
    """
    A wrapper function to visualize the NFDB results

    Parameters
    ----------
    config : dict
        The configuration parameters
    filtered_nfdb_data_large_fires : GeoDataFrame
        The filtered NFDB data for large fires
    """
    set_plot_font_size(font_size=13)
    validate_type(config, dict, "config")
    validate_type(filtered_nfdb_data_large_fires, gpd.GeoDataFrame, "filtered_nfdb_data_large_fires")

    # create a map of all wildfires in the filtered NFDB dataset > 200 hectars according to their lat and lon
    filtered_nfdb_data_large_fires.plot(
        x=config["NFDB_data"]["region_of_interest"]["region_centre_longitude_column_name"],
        y=config["NFDB_data"]["region_of_interest"]["region_centre_latitude_column_name"],
        kind='scatter',
        color='red',
        label='Wildfires > 200 hectars'
    )
    plt.title('Map of all wildfires in the filtered NFDB dataset > 200 hectars')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()

    # show the number of wildfires in the filtered NFDB dataset > 200 hectars by year
    filtered_nfdb_data_large_fires_by_year = filtered_nfdb_data_large_fires.groupby(
        config["NFDB_data"]["time_of_interest"]["year_column_name"]
    ).size()
    bars = plt.bar(filtered_nfdb_data_large_fires_by_year.index, filtered_nfdb_data_large_fires_by_year)
    for j, bar in enumerate(bars):
        y_value = bar.get_height()
        x_value = bar.get_x() + bar.get_width() / 2
        plt.annotate(
            bar.get_height(),
            (x_value, y_value),
            xytext=(0, 0),
            textcoords="offset points",
            ha='center',
            va='bottom',
        )
    # filtered_nfdb_data_large_fires_by_year.plot(kind='bar')
    plt.title('Number of wildfires in the filtered NFDB dataset > 200 hectars by year')
    plt.xlabel('Year')
    plt.ylabel('Number of wildfires')
    plt.show()

    # show the number of wildfires in the filtered NFDB dataset > 200 hectars by month and year
    filtered_nfdb_data_large_fires_by_month = filtered_nfdb_data_large_fires.groupby(
        config["NFDB_data"]["time_of_interest"]["month_column_name"]
    ).size()
    filtered_nfdb_data_large_fires_by_month_and_year = filtered_nfdb_data_large_fires.groupby(
        [config["NFDB_data"]["time_of_interest"]["year_column_name"],
         config["NFDB_data"]["time_of_interest"]["month_column_name"]]
    ).size()
    fig, (ax1, ax2) = plt.subplots(1, 2)
    filtered_nfdb_data_large_fires_by_month.plot(kind='bar', ax=ax1)
    ax1.set_title('# of wildfires in the filtered NFDB dataset > 200 hectars by month')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Number of wildfires')
    filtered_nfdb_data_large_fires_by_month_and_year.unstack().plot(kind='bar', stacked=True, ax=ax2)
    ax2.set_title('# of wildfires in the filtered NFDB dataset > 200 hectars by month and year')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Number of wildfires')
    plt.show()

    # show the map of all wildfires in the filtered NFDB dataset > 200 hectars colored by year
    filtered_nfdb_data_large_fires.plot(
        x=config["NFDB_data"]["region_of_interest"]["region_centre_longitude_column_name"],
        y=config["NFDB_data"]["region_of_interest"]["region_centre_latitude_column_name"],
        kind='scatter',
        c=config["NFDB_data"]["time_of_interest"]["year_column_name"],
        colormap='viridis',
        label='Wildfires > 200 hectars',
        marker='o',
        s=100,
    )
    plt.title('Map of all wildfires in the filtered NFDB dataset > 200 hectars colored by year')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()


def separate_date_series_to_Y_m_d(
    date_series: pd.Series,
    date_format: str = "%Y-%m-%d %H:%M",
    errors: str = "raise",
) -> pd.DataFrame:
    """
    Separate a series of dates into year, month, and day

    Parameters:
    ----------
    date_series : pandas.Series
        The series of dates to be converted.
    date_format : str, optional
        The format of the input dates. Default is "%Y-%m-%d %H:%M".
    errors : str, optional
        How to handle errors in the conversion. Default is "raise". The options are:
            'raise': invalid parsing will raise an exception.
            'coerce': invalid parsing will be set as NaT.
            'ignore': invalid parsing will return the input.

    Returns:
    -------
    pandas.Series
        A DataFrame with columns for year, month, and day
    """
    validate_type(date_series, pd.Series, "date_series")
    validate_type(date_format, str, "date_format")
    validate_type(errors, str, "errors")

    date_series = pd.to_datetime(
        date_series,
        format=date_format,
        errors=errors
    )

    separated_date_dataframe = pd.DataFrame(
        {
            "year": date_series.dt.year,
            "month": date_series.dt.month,
            "day": date_series.dt.day,
        }
    )

    return separated_date_dataframe


def filter_whitesands_f4_data(
    file_path: str,
    date_column_name: str,
    start_year: int,
    end_year: int,
    start_month: int,
    end_month: int,
) -> pd.DataFrame:
    """
    Filter Whitesands F4 data according to the data cleaning parameters

    Parameters
    ----------
    file_path : str
        The path to the Whitesands F4 data
    date_column_name : str
        The name of the date column
    start_year : int
        The start year of interest
    end_year : int
        The end year of interest
    start_month : int
        The start month of interest
    end_month : int
        The end month of interest

    Returns
    -------
    filtered_whitesands_f4_data : DataFrame
        The filtered Whitesands F4 data
    """
    # read in the Whitesands F4 data
    validate_type(file_path, str, "Whitesands F4 data path")
    validate_type(date_column_name, str, "date_column_name")
    validate_type(start_year, int, "start_year")
    validate_type(end_year, int, "end_year")
    validate_type(start_month, int, "start_month")
    validate_type(end_month, int, "end_month")

    whitesands_f4_data_df = pd.read_csv(file_path)

    separated_date_dataframe = separate_date_series_to_Y_m_d(
        date_series=whitesands_f4_data_df[date_column_name]
    )

    whitesands_f4_data_df["year"] = separated_date_dataframe["year"]
    whitesands_f4_data_df["month"] = separated_date_dataframe["month"]

    # filter according to the years of interest
    filtered_whitesands_f4_data = whitesands_f4_data_df.loc[
        whitesands_f4_data_df["year"].between(start_year, end_year)
    ]

    # filter according to the months of interest
    filtered_whitesands_f4_data = filtered_whitesands_f4_data.loc[
        filtered_whitesands_f4_data["month"].between(start_month, end_month)
    ]

    return filtered_whitesands_f4_data


def convert_month_to_int(
    month: str,
) -> int:
    """
    Convert month to int

    Parameters
    ----------
    month : str
        The month as a string

    Returns
    -------
    int_month : int
        The month as an integer
    """
    validate_type(month, str, "month")

    if month.casefold() in ["jan", "january", "janv", "janvier", "1"]:
        int_month = 1
    elif month.casefold() in ["feb", "february", "fév", "février", "fev", "fevrier" "2"]:
        int_month = 2
    elif month.casefold() in ["mar", "march", "mars", "3"]:
        int_month = 3
    elif month.casefold() in ["apr", "april", "avr", "avril", "4"]:
        int_month = 4
    elif month.casefold() in ["may", "mai", "5"]:
        int_month = 5
    elif month.casefold() in ["jun", "june", "juin", "6"]:
        int_month = 6
    elif month.casefold() in ["jul", "july", "juil", "juillet", "7"]:
        int_month = 7
    elif month.casefold() in ["aug", "august", "août", "aout", "8"]:
        int_month = 8
    elif month.casefold() in ["sep", "september", "sept", "septembre", "9"]:
        int_month = 9
    elif month.casefold() in ["oct", "october", "octobre", "10"]:
        int_month = 10
    elif month.casefold() in ["nov", "november", "novembre", "11"]:
        int_month = 11
    elif month.casefold() in ["dec", "december", "déc", "décembre", "12"]:
        int_month = 12
    else:
        raise ValueError(
            "The month should be one of the following: "
            "jan, january, janv, janvier, 1, "
            "feb, february, fév, février, fev, fevrier 2, "
            "mar, march, mars, 3, "
            "apr, april, avr, avril, 4, "
            "may, mai, 5, "
            "jun, june, juin, 6, "
            "jul, july, juil, juillet, 7, "
            "aug, august, août, aout, 8, "
            "sep, september, sept, septembre, 9, "
            "oct, october, octobre, 10, "
            "nov, november, novembre, 11, "
            "dec, december, déc, décembre, 12."
        )

    return int_month


def convert_coordinate_to_float(
    coordinate: str,
) -> float:
    """
    Convert coordinate to float

    Parameters
    ----------
    coordinate : str
        The coordinate value as a string. The format should be
        "deg°min'sec''direction". For example, "50°30'30''N"
        To write the degree symbol, press and hold the Alt key, and type 0176
        on the numeric keypad. You can also use the degree symbol in the
        Character Map on Windows.

    Returns
    -------
    float_coordinate : float
        The coordinate value as a float
    """
    validate_type(coordinate, str, "coordinate")

    deg = float(coordinate.split("°")[0])
    min = float(coordinate.split("°")[1].split("'")[0])
    sec = float(coordinate.split("°")[1].split("'")[1].split("''")[0])
    direction = coordinate.split("''")[1]

    float_coordinate = deg + min / 60 + sec / 3600
    if direction == "S" or direction == "W":
        float_coordinate = - float_coordinate

    return float_coordinate


def load_json_file(
    json_name: str,
    json_path: str = None,
) -> dict:
    """
    Function to load a json file using the filepath and filename

    Parameters:
    -----------
    json_name: str
        The name of the json file to load
    json_path: str
        The path to the json file. Default is None

    Returns:
    --------
    loaded_json: dict
        The loaded json file
    """
    if json_path is None:
        json_path = os.getcwd()

    try:
        if json_name is not None:
            path_to_json = os.path.join(json_path, json_name)

            with open(path_to_json, "r") as f:
                loaded_json = json.load(f)
    except ValueError:
        print(
            f"Failed to open {os.path.join(json_path, json_name)}. "
            f"File not found in this location"
        )

    return loaded_json


def create_data_file_path(
    data_package_dir: str,
    file_name: str,
) -> str:
    """
    Create the path to the data file

    Parameters
    ----------
    data_package_dir : str
        The path to the data package directory.
        It should be the directory containing the data_package folder.
    file_name : str
        The name of the file

    Returns
    -------
    data_file_path : str
        The path to the data file
    """
    if data_package_dir.endswith("/"):
        data_package_dir = data_package_dir
    else:
        data_package_dir = data_package_dir + "/"
    if "/data_package/" not in data_package_dir:
        raise ValueError(
            "The data_package_dir should be the directory containing "
            "the data_package folder."
        )

    if "." not in file_name:
        raise ValueError(
            "The file name should include the file extension."
        )

    data_file_path = os.path.join(
        data_package_dir,
        file_name,
    )

    return data_file_path


def filter_nfdb_data(
        file_path: str,
        province_or_territory_column_name: str,
        province_or_territory: str,
        region_centre_latitude_column_name: str,
        region_centre_lat: float,
        region_centre_longitude_column_name: str,
        region_centre_lon: float,
        region_radius: float,
        year_column: str,
        start_year: int,
        end_year: int,
        month_column: str,
        start_month: int,
        end_month: int,
) -> gpd.GeoDataFrame:
    """
    Filter NFDB data according to the data cleaning parameters

    Parameters
    ----------
    file_path : str
        The path to the NFDB data
    province_or_territory_column_name : str
        The name of the province or territory column
    province_or_territory : str
        The province or territory of interest
    region_centre_latitude_column_name : str
        The name of the region centre latitude column
    region_centre_lat : float
        The region centre latitude
    region_centre_longitude_column_name : str
        The name of the region centre longitude column
    region_centre_lon : float
        The region centre longitude
    region_radius : float
        The radius of the region of interest
    year_column : str
        The name of the year column
    start_year : int
        The start year of interest
    end_year : int
        The end year of interest
    month_column : str
        The name of the month column
    start_month : int
        The start month of interest
    end_month : int
        The end month of interest

    Returns
    -------
    filtered_nfdb_data : GeoDataFrame
        The filtered NFDB data
    """
    # read in the NFDB data
    validate_type(file_path, str, "NFDB data path")
    validate_type(province_or_territory_column_name, str, "province_or_territory_column_name")
    validate_type(province_or_territory, str, "province_or_territory")
    validate_type(region_centre_latitude_column_name, str, "region_centre_latitude_column_name")
    validate_type(region_centre_lat, float, "region_centre_lat")
    validate_type(region_centre_longitude_column_name, str, "region_centre_longitude_column_name")
    validate_type(region_centre_lon, float, "region_centre_lon")
    validate_type(region_radius, float, "region_radius")
    validate_type(year_column, str, "year_column")
    validate_type(start_year, int, "start_year")
    validate_type(end_year, int, "end_year")
    validate_type(month_column, str, "month_column")
    validate_type(start_month, int, "start_month")
    validate_type(end_month, int, "end_month")

    nfdb_data_gdf = read_vector_file_into_gdf(file_path)

    # filter according to the province or territory
    filtered_nfdb_data = nfdb_data_gdf.loc[
        nfdb_data_gdf[province_or_territory_column_name] == province_or_territory
    ]

    # filter according to the region centre coordinates
    filtered_nfdb_data = filtered_nfdb_data.loc[
        filtered_nfdb_data[region_centre_latitude_column_name].between(
            region_centre_lat - region_radius,
            region_centre_lat + region_radius
        )
    ]
    filtered_nfdb_data = filtered_nfdb_data.loc[
        filtered_nfdb_data[region_centre_longitude_column_name].between(
            region_centre_lon - region_radius,
            region_centre_lon + region_radius
        )
    ]

    # filter according to the years of interest
    filtered_nfdb_data = filtered_nfdb_data.loc[
        filtered_nfdb_data[year_column].between(start_year, end_year)
    ]

    # filter according to the months of interest
    filtered_nfdb_data = filtered_nfdb_data.loc[
        filtered_nfdb_data[month_column].between(start_month, end_month)
    ]

    return filtered_nfdb_data


def validate_type(
    variable: any,
    expected_type: (type),
    arg_name: str = "input"
) -> None:
    """
    Validate type of the input variable

    Parameters
    ----------
    variable : any
        The variable to be validated
    expected_type : type or tuple of types
        The expected type or a tuple of expected types of the self object
    arg_name : str
        The name of the argument to be used in the error message. Default is "input".

    Raises
    ------
    TypeError
        If the variable is not of the expected type
    """
    if not isinstance(variable, expected_type):
        raise TypeError(
            f"The {arg_name} should be {expected_type} not {type(variable)}!"
        )


def read_vector_file_into_gdf(
    file_path: str
) -> gpd.GeoDataFrame:
    """
    Read a vector file into a GeoDataFrame

    Parameters
    ----------
    file_path : str
        The path to the vector file

    Returns
    -------
    data_gdf : GeoDataFrame
        The data in the vector file as a GeoDataFrame
    """
    validate_type(file_path, str, "file_path")

    # read in the data
    data_gdf = gpd.read_file(file_path)

    return data_gdf
