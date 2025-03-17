import argparse
import os
import json
from wildfire_processing_functions_BY import (
    load_json_file,
    create_data_file_path,
    convert_coordinate_to_float,
    convert_month_to_int,
    filter_nfdb_data,
    filter_whitesands_f4_data,
    visualize_nfdb_results,
    visualize_whitesands_F4_results,
)


if __name__ == "__main__":
    # This script is used to clean, analyse, and visualize wildfire datasets.
    # The script reads a configuration file that contains the parameters
    # needed to process. The configuration file can be provided as a path or
    # as a JSON string. The script will look for a file called
    # `wildfire_config_BY.json` in the same directory if no configuration file
    # is provided.
    # This script can be run on a local machine or virtual machine (like a
    # Google Cloud Engine). For processing very huge datasets and
    # parallel processing, it is recommended to run it on a Kubernetes cluster
    # in Apache Airflow, like the Google Kubernetes Engine (GKE).

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-c",
        "--config",
        required=False,
        help="Location of the json configuration file used to set parameters."
        " If None is provided, the script will look for a file called"
        " wildfire_config_BY.json in the same directory.",
    )
    parser.add_argument(
        "-j",
        "--json_string",
        required=False,
        help="Full config contents formatted as a JSON string."
        " This will override any config path or defaults.",
    )

    args = parser.parse_args()
    config_arg = args.config
    json_string = args.json_string

    if json_string is not None:
        config = json.loads(json_string)
    else:
        if config_arg is None:
            path_to_config = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "wildfire_config_BY.json",
            )
        else:
            path_to_config = config_arg

        # read the config file
        config = load_json_file(path_to_config)

    # ---------------------------------------------------------------------------
    # Data cleaning
    # ---------------------------------------------------------------------------

    print("\n *** Data cleaning has started... *** \n")

    # ----- Clean the NFDB data ----- #
    # create NFDB data file path
    nfdb_data_path = create_data_file_path(
        data_package_dir=config["data_package_dir"],
        file_name=config["NFDB_data"]["file_name"],
    )

    # convert lat and lon to float
    lat = convert_coordinate_to_float(
       coordinate=config["NFDB_data"]["region_of_interest"]["region_centre_latitude"]
    )
    lon = convert_coordinate_to_float(
       coordinate=config["NFDB_data"]["region_of_interest"]["region_centre_longitude"]
    )

    # convert month to integer if it is a string
    if isinstance(config["NFDB_data"]["time_of_interest"]["start_month"], str):
        start_month = convert_month_to_int(
            month=config["NFDB_data"]["time_of_interest"]["start_month"]
        )
    else:
        start_month = config["NFDB_data"]["time_of_interest"]["start_month"]
    if isinstance(config["NFDB_data"]["time_of_interest"]["end_month"], str):
        end_month = convert_month_to_int(
            month=config["NFDB_data"]["time_of_interest"]["end_month"]
        )
    else:
        end_month = config["NFDB_data"]["time_of_interest"]["end_month"]

    # Filter NFDB data according to the data cleaning parameters
    filtered_nfdb_data = filter_nfdb_data(
        file_path=nfdb_data_path,
        province_or_territory_column_name=config["NFDB_data"]["region_of_interest"]["province_or_territory_column_name"],
        province_or_territory=config["NFDB_data"]["region_of_interest"]["province_or_territory_name"],
        region_centre_latitude_column_name=config["NFDB_data"]["region_of_interest"]["region_centre_latitude_column_name"],
        region_centre_lat=lat,
        region_centre_longitude_column_name=config["NFDB_data"]["region_of_interest"]["region_centre_longitude_column_name"],
        region_centre_lon=lon,
        region_radius=float(config["NFDB_data"]["region_of_interest"]["region_radius"]),
        year_column=config["NFDB_data"]["time_of_interest"]["year_column_name"],
        start_year=config["NFDB_data"]["time_of_interest"]["start_year"],
        end_year=config["NFDB_data"]["time_of_interest"]["end_year"],
        month_column=config["NFDB_data"]["time_of_interest"]["month_column_name"],
        start_month=start_month,
        end_month=end_month,
    )

    print(
        f"NFDB data has been filtered according to the data cleaning parameters."
        f" The filtered data contains {filtered_nfdb_data.shape[0]} rows. \n"
    )

    # ----- Clean the Whitesands F4 data ----- #
    # create  Whitesands F4 data file path
    whitesands_f4_data_path = create_data_file_path(
        data_package_dir=config["data_package_dir"],
        file_name=config["Whitesands_F4_data"]["file_name"],
    )

    # convert month to integer if it is a string
    if isinstance(config["Whitesands_F4_data"]["time_of_interest"]["start_month"], str):
        start_month = convert_month_to_int(
            month=config["Whitesands_F4_data"]["time_of_interest"]["start_month"]
        )
    else:
        start_month = config["Whitesands_F4_data"]["time_of_interest"]["start_month"]
    if isinstance(config["Whitesands_F4_data"]["time_of_interest"]["end_month"], str):
        end_month = convert_month_to_int(
            month=config["Whitesands_F4_data"]["time_of_interest"]["end_month"]
        )
    else:
        end_month = config["Whitesands_F4_data"]["time_of_interest"]["end_month"]

    # Filter Whitesands F4 data according to the data cleaning parameters
    filtered_whitesands_F4_data = filter_whitesands_f4_data(
        file_path=whitesands_f4_data_path,
        date_column_name=config["Whitesands_F4_data"]["time_of_interest"]["date_column_name"],
        start_year=config["Whitesands_F4_data"]["time_of_interest"]["start_year"],
        end_year=config["Whitesands_F4_data"]["time_of_interest"]["end_year"],
        start_month=start_month,
        end_month=end_month,
    )

    print(
        f"Whitesands F4 data has been filtered according to the data cleaning parameters."
        f" The filtered data contains {filtered_whitesands_F4_data.shape[0]} rows. \n"
    )

    # Optionally save the cleaned data to a file
    if config["save_results"]["save_results"]:
        # write the filtered NFDB data to a shapefile
        filtered_nfdb_data.to_file(
            create_data_file_path(
                data_package_dir=config["save_results"]["results_dir"],
                file_name=config["save_results"]["cleaned_NFDB_data_file_name"],
            )
        )
        # write the filtered Whitesands F4 data to a shapefile
        filtered_whitesands_F4_data.to_csv(
            create_data_file_path(
                data_package_dir=config["save_results"]["results_dir"],
                file_name=config["save_results"]["cleaned_Whitesands_F4_data_file_name"],
            ),
            index=False,
        )
    print("\n *** Data cleaning has been completed! *** \n")

    # ---------------------------------------------------------------------------
    # Data visualization
    # ---------------------------------------------------------------------------

    print("\n *** Data visualization has started... *** \n")

    # ----- Visualize cleaned NFDB data results ----- #
    # Filter wildfires in the filtered NFDB dataset > 200 hectars
    filtered_nfdb_data_large_fires = filtered_nfdb_data[
        filtered_nfdb_data[config["NFDB_data"]["fire_conditions"]["fire_size_column_name"]] > 200
    ]

    print(
        f"Number of wildfires in the filtered NFDB dataset > 200 hectars: {filtered_nfdb_data_large_fires.shape[0]} \n"
    )

    # Optionally save the filtered NFDB data to a file
    if config["save_results"]["save_results"]:
        # write the filtered NFDB data to a shapefile
        filtered_nfdb_data_large_fires.to_file(
            create_data_file_path(
                data_package_dir=config["save_results"]["results_dir"],
                file_name=config["save_results"]["filtered_nfdb_data_large_fires_file_name"],
            )
        )

    if config["visualize_results"]:
        # Visualize the filtered NFDB data results
        visualize_nfdb_results(config, filtered_nfdb_data_large_fires)

    # # ----- Visualize cleaned Whitesands F4 data results from 2014 to 2021 ----- #
    # # Filter Whitesands F4 data for years between 2014 and 2021
    # monthly_filtered_whitesands_F4_data = []
    # for month_num in range(start_month, end_month + 1):
    #     one_month_filtered_whitesands_F4_data = filtered_whitesands_F4_data[
    #         (filtered_whitesands_F4_data["year"] >= 2014)
    #         & (filtered_whitesands_F4_data["year"] <= 2021)
    #         & (filtered_whitesands_F4_data["month"] == month_num)
    #     ]
    #     monthly_filtered_whitesands_F4_data.append(one_month_filtered_whitesands_F4_data)

    # if config["visualize_results"]:
    #     # Visualize the filtered Whitesands F4 data results
    #     visualize_whitesands_F4_results(config, monthly_filtered_whitesands_F4_data)

    # ----- Visualize cleaned Whitesands F4 data results from 2010 to 2021 ----- #
    # Filter Whitesands F4 data for years between 2010 and 2021
    monthly_filtered_whitesands_F4_data = []
    for month_num in range(start_month, end_month + 1):
        one_month_filtered_whitesands_F4_data = filtered_whitesands_F4_data[
            (filtered_whitesands_F4_data["month"] == month_num)
        ]
        monthly_filtered_whitesands_F4_data.append(one_month_filtered_whitesands_F4_data)

    if config["visualize_results"]:
        # Visualize the filtered Whitesands F4 data results
        visualize_whitesands_F4_results(config, monthly_filtered_whitesands_F4_data)

    print("\n *** Data visualization has been completed! *** \n")
