from __future__ import annotations

import pytest

from tests.helpers import load_module


@pytest.fixture(scope="session")
def edge_workspace_links():
    return load_module()
