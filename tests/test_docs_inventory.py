from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_adoption_playbook_is_discoverable_from_readme():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "docs/adoption-playbook.md" in readme


def test_adoption_playbook_keeps_staged_rollout_guidance():
    text = (ROOT / "docs" / "adoption-playbook.md").read_text(encoding="utf-8")

    assert "Stage 1: Static Scan" in text
    assert "Stage 2: Gallery Manifest" in text
    assert "Stage 3: Release Gate" in text
    assert "Stage 4: Optional MATLAB Render" in text
    assert "MATLAB is not required" in text
    assert "guaranteed program eligibility" in text
