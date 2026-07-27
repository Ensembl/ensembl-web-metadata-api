import pytest

from api.schemas.region_validation import RegionValidation


@pytest.mark.parametrize(
    ("location_input", "expected"),
    [
        ("13", ("13", None, None)),
        ("X:100-200", ("X", "100", "200")),
        ("GL000194.1:1-191469", ("GL000194.1", "1", "191469")),
        ("KI270442_1", ("KI270442_1", None, None)),
    ],
)
def test_parse_location_input_success(location_input, expected):
    assert RegionValidation.parse_location_input(location_input) == expected


@pytest.mark.parametrize(
    "location_input",
    [
        "X:100",
        "X:100-",
        "X:-200",
        "X:100-200:300",
        "X 100-200",
    ],
)
def test_parse_location_input_returns_defaults_locations(location_input):
    assert RegionValidation.parse_location_input(location_input) == (None, None, None)


def test_validate_region_invalid_location_input():
    region_validation = RegionValidation(
        genome_uuid="test-genome-id", location_input="X:100"
    )

    assert region_validation.validate_region(db_conn=object()) is None
