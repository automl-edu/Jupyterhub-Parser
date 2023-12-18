import argparse
import pandas as pd
import sys
import os

# ==================== Config =============
SIZE = 50
# =========================================


def parse_arguments() -> argparse.Namespace:
    """Parses the arguments from the command line

    Returns:
        argparse.Namespace: The parsed arguments
    """

    parser = argparse.ArgumentParser(
        prog="MailExporter",
        description="Exports the emails of the course roster in batches of 50 in the terminal",
    )
    parser.add_argument(
        "roster_file", type=str, help="The path to the file of the course roster as csv"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="The path to the output file",
    )
    parser.add_argument(
        "-n", type=int, help="The batch size of the mails", default=SIZE, dest="size"
    )

    args = parser.parse_args()
    return args


def get_mails(roster_file: str) -> pd.Series:
    """Gets the emails from the course roster. Only emails with the domain uni-hannover.de are returned

    Args:
        roster_file (str): The path to the file of the course roster as csv

    Returns:
        pd.Series: The emails of the course roster
    """

    df = pd.read_csv(roster_file, sep=";")
    mails = df["E-Mail"].dropna().str.strip()
    mails = mails[mails.str.contains("uni-hannover.de")]
    return mails


def main():
    args = parse_arguments()
    roster_file = args.roster_file
    output_file = args.output
    batch_size = args.size

    emails = get_mails(roster_file)

    f = sys.stdout
    if output_file:
        if os.path.exists(output_file) and os.path.isfile(output_file):
            os.remove(output_file)
        f = open(output_file, "a")

    f.write("\n\n===================================\n\n")
    for i in range(0, len(emails), batch_size):
        batch = emails[i : i + batch_size]
        for email in batch:
            f.write(email + "\n")
        f.write("\n===================================\n\n")

    if output_file:
        f.close()


if __name__ == "__main__":
    main()
