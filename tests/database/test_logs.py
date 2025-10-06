import pytest
from unittest.mock import MagicMock
from smartcity.database.functions import rotate_logs_supabase


@pytest.fixture
def mock_supabase():
    """Create a mocked Supabase client with storage methods."""
    supabase = MagicMock()
    supabase.storage.from_.return_value.list.return_value = [
        {"name": "workflow_openaq_2025-09-29_14-00-00.log", "metadata": {"lastModified": 300}},
        {"name": "workflow_openaq_2025-09-29_13-00-00.log", "metadata": {"lastModified": 200}},
        {"name": "workflow_openaq_2025-09-29_12-00-00.log", "metadata": {"lastModified": 100}},
    ]
    return supabase

def test_deletes_old_logs(mock_supabase):
    """
    Ensure rotate_logs_supabase keeps only the latest N logs
    and deletes older ones.
    """

    rotate_logs_supabase(
        supabase=mock_supabase,
        bucket_name="data",
        remote_dir="smartcity-logs",
        remote_name="workflow_openaq.log",
        keep_last=2,
    )

    # Check that delete was called once (only one log older than 2 kept)
    mock_supabase.storage.from_.return_value.remove.assert_called_once_with(
        ["smartcity-logs/workflow_openaq_2025-09-29_12-00-00.log"]
    )
