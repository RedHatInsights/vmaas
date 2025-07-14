"""Module with tools used with unit tests."""
import iso8601


def match(expected, given):
    """Checks if expected record matches given record."""
    msg = True
    not_match = {}
    for key, value in expected.items():
        # exact match for all the values
        if key == "cvss3_score" and value:
            if float(value) == float(given[key]):
                continue

            not_match.update({key: given[key]})
        elif value and key in ("public_date", "modified_date"):
            value = iso8601.parse_date(value)
            if value != given[key]:
                not_match.update({key: given[key]})
        elif value == given[key]:
            continue
        not_match.update({key: given[key]})

    if not_match:
        msg = """
            Expected details does not match:
            expected: {!r}
            not matching: {!r}
        """.format(expected, not_match)
    return msg
