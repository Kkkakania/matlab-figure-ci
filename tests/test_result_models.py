from matlab_figure_ci.result import Finding


def test_finding_from_dict_normalizes_line_numbers():
    numeric = Finding.from_dict(
        {
            "severity": "error",
            "rule_id": "privacy.email",
            "path": "src/example.m",
            "line": "7",
            "message": "<redacted>",
        }
    )
    invalid = Finding.from_dict(
        {
            "severity": "error",
            "rule_id": "privacy.email",
            "path": "src/example.m",
            "line": "not-a-line",
            "message": "<redacted>",
        }
    )

    assert numeric.line == 7
    assert invalid.line is None
