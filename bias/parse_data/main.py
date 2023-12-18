import argparse
import json
import os

from data_parser import parse_data
from mail_sender import send_mails
import pandas as pd


# ============= CONSTANTS =============
DEFAULT_CONFIG_PATH = "secrets.json"
DEFAULT_OUTPUT_PATH = os.path.join(".", "output")

JH_CREDS = "jh_credentials.csv"
JH_CONFIG = "jh_config.csv"
JH_CONFIG_STRING = "jh_config_strjoin.csv"
# =====================================


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="BiasSender",
        description="Combines the Users from the course roster and the Bias PDF and finally sends emails",
    )
    parser.add_argument(
        "roster_file", type=str, help="The path to the file of the course roster in csv"
    )
    parser.add_argument(
        "bias_path", type=str, help="The path to the folder containing the Bias PDFs"
    )
    parser.add_argument(
        "merge_file", type=str, help="The path to the file containing the merge data"
    )
    parser.add_argument("-c", "--config", type=str, help="The path to the config file")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="The path to the output folder",
    )

    args = parser.parse_args()
    return args


def write_output_path(output_path: str, data: pd.DataFrame):
    path = output_path
    if not os.path.exists(path):
        os.makedirs(path)

    tmp_file_name = "jh_config_strjoin_tmp.csv"

    # All data is written to all.csv
    data.to_csv(os.path.join(path, JH_CREDS), index=False)

    # TODO wirte individual csv files with different columns
    contraint_data = data[["Nutzernamen", "Vorname", "Nachname", "E-Mail"]]
    contraint_data.to_csv(os.path.join(path, JH_CONFIG), index=False, header=False)

    str_data = contraint_data.apply(lambda row: ",".join(map(str, row)), axis=1)
    str_data.to_csv(os.path.join(path, tmp_file_name), index=False, header=False)
    with open(os.path.join(path, tmp_file_name), "r") as tmp_file, open(
        os.path.join(path, JH_CONFIG_STRING), "w"
    ) as out_file:
        for line in tmp_file:
            line_with_comma = line.strip() + ",\n"
            out_file.write(line_with_comma)
    os.remove(os.path.join(path, tmp_file_name))


def mail_sender_loop(output_path: str, config_path: str):
    if not os.path.exists(config_path):
        with open(config_path, "w") as config_file:
            data = {
                "Mail": "",
                "Password": "",
                "smtp-server": "smtp.uni-hannover.de",
                "port": 587,
            }
            json.dump(data, config_file, indent=4)
        print(
            f"\n\nPlease fill in the config file at {config_path} in your current working directory. It is already filled out with sensible defaults.\n\n"
        )
        return

    with open(config_path, "r") as config_file:
        config = json.load(config_file)

    while True:
        print("Do you want to send the emails? [y/n]")
        answer = input()
        try:
            answer = answer.lower()
        except:
            pass

        match answer:
            case "y":
                print("Sending emails...")
                send_mails(os.path.join(output_path, JH_CREDS), config)
                break
            case "n":
                print("Not sending emails...")
                break
            case _:
                print("Please enter 'y' or 'n'.")


def main():
    args = parse_arguments()
    bias_path = args.bias_path
    roster_file = args.roster_file
    merge_file = args.merge_file
    output_path = DEFAULT_OUTPUT_PATH if args.output is None else args.output
    config_path = DEFAULT_CONFIG_PATH if args.config is None else args.config

    print("Parsing data...")
    data = parse_data(roster_file, bias_path, merge_file)

    print("Writing output to folder...")
    write_output_path(output_path, data)

    mail_sender_loop(output_path, config_path)


if __name__ == "__main__":
    main()
