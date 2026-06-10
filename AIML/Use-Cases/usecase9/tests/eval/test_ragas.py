from __future__ import annotations

from tests.test_ragas_offline import test_ragas_dataset_contract_is_offline_ready


def test_offline_ragas_contract(tmp_path):
    test_ragas_dataset_contract_is_offline_ready(tmp_path)
