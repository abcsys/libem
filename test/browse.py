import libem


def test_negative_no_browse():
    e1 = "mighty strike freedom gundam"
    e2 = "ZGMF/A-262PD-P"

    # No browse:
    libem.calibrate({
        "libem.match.parameter.tools": [],
    })

    is_match = libem.match(e1, e2)
    assert is_match['answer'] == 'no', f"Expected 'no', but got {is_match['answer']}"


def test_positive_with_browse():
    e1 = "mighty strike freedom gundam"
    e2 = "ZGMF/A-262PD-P"

    # With browse:
    libem.calibrate({
        "libem.match.parameter.tools": ["libem.browse"],
    })

    is_match = libem.match(e1, e2)
    assert is_match['answer'] == 'yes', f"Expected 'yes', but got {is_match['answer']}"
