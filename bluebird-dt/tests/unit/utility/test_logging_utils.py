import io
import json
import tarfile

import pandas as pd
import pytest

from bluebird_dt.utility.logging_utils import (
    read_tar_csv_to_df,
    read_tar_json_to_dict,
    read_tar_parquet_to_df,
    save_df_to_csv_tar,
    save_df_to_parquet_tar,
    save_json_to_tar,
)


def test_save_and_read_tar_dataframe_round_trip():
    """
    Check writing and then reading parquet and csv within tar files work correctly
    """
    df = pd.DataFrame([{"a": 1, "b": 2.5}, {"a": 2, "b": 3.5}])
    buffer = io.BytesIO()

    with tarfile.open(fileobj=buffer, mode="w") as tar:
        save_df_to_parquet_tar(df, tar, "data")
        save_df_to_csv_tar(df, tar, "data_csv")

    buffer.seek(0)
    with tarfile.open(fileobj=buffer, mode="r") as tar:
        df_parquet = read_tar_parquet_to_df(tar, "data")
        df_csv = read_tar_csv_to_df(tar, "data_csv")

    pd.testing.assert_frame_equal(df_parquet, df)
    pd.testing.assert_frame_equal(df_csv, df)


def test_save_and_read_tar_json_round_trip():
    """
    Check writing and then reading json within tar files work correctly
    """
    input = {"a": 1, "b": "two"}
    buffer = io.BytesIO()

    with tarfile.open(fileobj=buffer, mode="w") as tar:
        save_json_to_tar(json.dumps(input), tar, "config")

    buffer.seek(0)
    with tarfile.open(fileobj=buffer, mode="r") as tar:
        output = read_tar_json_to_dict(tar, "config")

    assert output == input


def test_read_tar_missing_file_raises():
    """
    Test trying to read a missing tar file raises and exception
    """
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w"):
        pass

    buffer.seek(0)
    with tarfile.open(fileobj=buffer, mode="r") as tar:
        with pytest.raises(FileNotFoundError):
            _ = read_tar_csv_to_df(tar, "missing")
        with pytest.raises(FileNotFoundError):
            _ = read_tar_parquet_to_df(tar, "missing")
        with pytest.raises(FileNotFoundError):
            _ = read_tar_json_to_dict(tar, "missing")
