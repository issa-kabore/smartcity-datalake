from postgrest import APIError
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from smartcity.database import read_db, SUPABASE_URL, SUPABASE_KEY

def test_missing_table(monkeypatch):
    with pytest.raises(APIError, match="Could not find the table"):
        read_db("test_table")

@patch("smartcity.database.create_client")
def test_read_db_returns_data(mock_create_client):
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.execute.return_value.data = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
    mock_create_client.return_value = mock_client

    df = read_db("test_table")
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["id", "name"]
    assert df.iloc[0]["name"] == "Alice"


@patch("smartcity.database.create_client")
def test_read_db_returns_empty_dataframe(mock_create_client):
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.execute.return_value.data = []
    mock_create_client.return_value = mock_client

    df = read_db("empty_table")
    
    assert isinstance(df, pd.DataFrame)
    assert df.empty
