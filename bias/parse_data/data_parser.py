import os
from pathlib import Path
from py_pdf_parser.loaders import load_file
import pandas as pd


def _to_path(path: str) -> Path:
    if os.path.exists(path):
        return Path(path)
    raise FileNotFoundError(f"Path {path} does not exist")


def _extract_account_details_from_PDF(pdf_file_path: str) -> pd.Series:
    document = load_file(pdf_file_path)
    accounts_table_as_single_string = document.elements.filter_by_text_contains("nhwp")[
        0
    ].text()
    accounts_as_list = accounts_table_as_single_string.split("\n")[
        1:
    ]  # First entry contains table header only
    accounts = {}
    for account_iter in range(0, len(accounts_as_list), 2):
        # Check, which entry is the username (containing substring "nhml")
        if "nhwp" in accounts_as_list[account_iter + 1]:
            user, pwd = (
                accounts_as_list[account_iter + 1],
                accounts_as_list[account_iter],
            )
        else:
            user, pwd = (
                accounts_as_list[account_iter],
                accounts_as_list[account_iter + 1],
            )
        accounts.update({user: pwd})

    accounts = pd.Series(accounts).reset_index(name="Passwort")
    accounts.columns = ["Nutzernamen", "Passwort"]
    accounts.sort_values(by="Nutzernamen", inplace=True)
    accounts.reset_index(drop=True, inplace=True)

    return accounts


def _extract_bias_data(bias_path: Path) -> dict:
    pdf_files = list(bias_path.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files")

    accounts = dict()
    for pdf_file in pdf_files:
        print(f"Extracting data from {pdf_file}")
        accounts = _extract_account_details_from_PDF(pdf_file)
        print(f"Found {len(accounts)} accounts")
        accounts.update(accounts)

    return accounts


def _get_jupyterhub_users(df, bias_return: str) -> pd.DataFrame:
    bias = pd.read_csv(
        bias_return,
        sep=" - ",
        header=None,
        names=["Nutzernamen", "E-Mail"],
        engine="python",
    )

    df = pd.merge(bias, df, on="E-Mail")
    df.rename(columns={"Nutzernamen_x": "Nutzernamen"}, inplace=True)
    return df


def parse_data(roster_file: str, bias_path: str, merge_file: str) -> pd.DataFrame:
    roster_file = _to_path(roster_file)
    bias_path = _to_path(bias_path)
    merge_file = _to_path(merge_file)
    if not bias_path.is_dir():
        raise ValueError(f"Path {bias_path} is not a directory")

    accounts = _extract_bias_data(bias_path)

    df = pd.read_csv(roster_file, sep=";")
    df.columns = [
        "Anrede",
        "Titel",
        "Vorname",
        "Nachname",
        "Titel2",
        "Nutzernamen",
        "Privatadr",
        "Privatnr",
        "E-Mail",
        "Anmeldedatum",
        "Studiengänge",
        "Bemerkung",
    ]
    df = df[df["E-Mail"].str.contains("uni-hannover.de")]

    df_jupyter = _get_jupyterhub_users(df, bias_return=merge_file)
    df_jupyter = pd.merge(accounts, df_jupyter, on="Nutzernamen")

    return df_jupyter
