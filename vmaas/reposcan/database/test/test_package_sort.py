"""
Unit test for correct package sorting.
Tests data copied from project "rpm-software-management/rpm":
https://github.com/rpm-software-management/rpm/blob/c7e711bba58374f03347c795a567441cbef3de58/tests/rpmvercmp.at
"""
import re

from vmaas.common import rpm_utils


def test_rpmver_1_numbers(db_conn):
    """
    Test ver/rel strings including only numbers.
    """

    assert rpmvercmp(db_conn, "1.0.0", "1.1.2") == -1
    assert rpmvercmp(db_conn, "1.0.0", "1.0.0") == 0
    assert rpmvercmp(db_conn, "1.0", "1.0") == 0
    assert rpmvercmp(db_conn, "1.0", "2.0") == -1
    assert rpmvercmp(db_conn, "2.0", "1.0") == 1
    assert rpmvercmp(db_conn, "2.0.1", "2.0.1") == 0
    assert rpmvercmp(db_conn, "2.0", "2.0.1") == -1
    assert rpmvercmp(db_conn, "2.0.1", "2.0") == 1


def test_rpmver_2_letters(db_conn):
    """
    Test ver/rel strings including letters too.
    """

    assert rpmvercmp(db_conn, "2.0.1a", "2.0.1a") == 0
    assert rpmvercmp(db_conn, "2.0.1a", "2.0.1") == 1
    assert rpmvercmp(db_conn, "2.0.1", "2.0.1a") == -1
    assert rpmvercmp(db_conn, "5.5p1", "5.5p1") == 0
    assert rpmvercmp(db_conn, "5.5p1", "5.5p2") == -1
    assert rpmvercmp(db_conn, "5.5p2", "5.5p1") == 1
    assert rpmvercmp(db_conn, "5.5p10", "5.5p10") == 0
    assert rpmvercmp(db_conn, "5.5p1", "5.5p10") == -1
    assert rpmvercmp(db_conn, "5.5p10", "5.5p1") == 1
    assert rpmvercmp(db_conn, "10xyz", "10.1xyz") == -1
    assert rpmvercmp(db_conn, "10.1xyz", "10xyz") == 1
    assert rpmvercmp(db_conn, "xyz10", "xyz10") == 0
    assert rpmvercmp(db_conn, "xyz10", "xyz10.1") == -1
    assert rpmvercmp(db_conn, "xyz10.1", "xyz10") == 1
    assert rpmvercmp(db_conn, "xyz.4", "xyz.4") == 0
    assert rpmvercmp(db_conn, "xyz.4", "8") == -1
    assert rpmvercmp(db_conn, "8", "xyz.4") == 1
    assert rpmvercmp(db_conn, "xyz.4", "2") == -1
    assert rpmvercmp(db_conn, "2", "xyz.4") == 1
    assert rpmvercmp(db_conn, "5.5p2", "5.6p1") == -1
    assert rpmvercmp(db_conn, "5.6p1", "5.5p2") == 1
    assert rpmvercmp(db_conn, "5.6p1", "6.5p1") == -1
    assert rpmvercmp(db_conn, "6.5p1", "5.6p1") == 1
    assert rpmvercmp(db_conn, "6.0.rc1", "6.0") == 1
    assert rpmvercmp(db_conn, "6.0", "6.0.rc1") == -1
    assert rpmvercmp(db_conn, "10b2", "10a1") == 1
    assert rpmvercmp(db_conn, "10a2", "10b2") == -1
    assert rpmvercmp(db_conn, "1.0aa", "1.0aa") == 0
    assert rpmvercmp(db_conn, "1.0a", "1.0aa") == -1
    assert rpmvercmp(db_conn, "1.0aa", "1.0a") == 1
    assert rpmvercmp(db_conn, "10.0001", "10.0001") == 0
    assert rpmvercmp(db_conn, "10.0001", "10.1") == 0
    assert rpmvercmp(db_conn, "10.1", "10.0001") == 0
    assert rpmvercmp(db_conn, "10.0001", "10.0039") == -1
    assert rpmvercmp(db_conn, "10.0039", "10.0001") == 1
    assert rpmvercmp(db_conn, "4.999.9", "5.0") == -1
    assert rpmvercmp(db_conn, "5.0", "4.999.9") == 1
    assert rpmvercmp(db_conn, "20101121", "20101121") == 0
    assert rpmvercmp(db_conn, "20101121", "20101122") == -1
    assert rpmvercmp(db_conn, "20101122", "20101121") == 1


def test_rpmver_3_chars(db_conn):
    """
    Test ver/rel strings including other characters too.
    """

    assert rpmvercmp(db_conn, "2_0", "2_0") == 0
    assert rpmvercmp(db_conn, "2.0", "2_0") == 0
    assert rpmvercmp(db_conn, "2_0", "2.0") == 0
    assert rpmvercmp(db_conn, "a", "a") == 0
    assert rpmvercmp(db_conn, "a+", "a+") == 0
    assert rpmvercmp(db_conn, "a+", "a_") == 0
    assert rpmvercmp(db_conn, "a_", "a+") == 0
    assert rpmvercmp(db_conn, "+a", "+a") == 0
    assert rpmvercmp(db_conn, "+a", "_a") == 0
    assert rpmvercmp(db_conn, "_a", "+a") == 0
    assert rpmvercmp(db_conn, "+_", "+_") == 0
    assert rpmvercmp(db_conn, "_+", "+_") == 0
    assert rpmvercmp(db_conn, "_+", "_+") == 0
    assert rpmvercmp(db_conn, "+", "_") == 0
    assert rpmvercmp(db_conn, "_", "+") == 0


def test_rpmver_4_tilda(db_conn):
    """
    Test ver/rel strings including ~ notation too.
    """

    assert rpmvercmp(db_conn, "1.0~rc1", "1.0~rc1") == 0
    assert rpmvercmp(db_conn, "1.0~rc1", "1.0") == -1
    assert rpmvercmp(db_conn, "1.0", "1.0~rc1") == 1
    assert rpmvercmp(db_conn, "1.0~rc1", "1.0~rc2") == -1
    assert rpmvercmp(db_conn, "1.0~rc2", "1.0~rc1") == 1
    assert rpmvercmp(db_conn, "1.0~rc1~git123", "1.0~rc1~git123") == 0
    assert rpmvercmp(db_conn, "1.0~rc1~git123", "1.0~rc1") == -1
    assert rpmvercmp(db_conn, "1.0~rc1", "1.0~rc1~git123") == 1


def test_rpmver_5_circum_flex(db_conn):
    """
    Test ver/rel strings including ^ notation too.
    """

    assert rpmvercmp(db_conn, "1.0^", "1.0^") == 0
    assert rpmvercmp(db_conn, "1.0^", "1.0") == 1
    assert rpmvercmp(db_conn, "1.0", "1.0^") == -1
    assert rpmvercmp(db_conn, "1.0^git1", "1.0^git1") == 0
    assert rpmvercmp(db_conn, "1.0^git1", "1.0") == 1
    assert rpmvercmp(db_conn, "1.0", "1.0^git1") == -1
    assert rpmvercmp(db_conn, "1.0^git1", "1.0^git2") == -1
    assert rpmvercmp(db_conn, "1.0^git2", "1.0^git1") == 1
    assert rpmvercmp(db_conn, "1.0^git1", "1.01") == -1
    assert rpmvercmp(db_conn, "1.01", "1.0^git1") == 1
    assert rpmvercmp(db_conn, "1.0^20160101", "1.0^20160101") == 0
    assert rpmvercmp(db_conn, "1.0^20160101", "1.0.1") == -1
    assert rpmvercmp(db_conn, "1.0.1", "1.0^20160101") == 1
    assert rpmvercmp(db_conn, "1.0^20160101^git1", "1.0^20160101^git1") == 0
    assert rpmvercmp(db_conn, "1.0^20160102", "1.0^20160101^git1") == 1
    assert rpmvercmp(db_conn, "1.0^20160101^git1", "1.0^20160102") == -1
    assert rpmvercmp(db_conn, "1.0~rc1^git1", "1.0~rc1^git1") == 0
    assert rpmvercmp(db_conn, "1.0~rc1^git1", "1.0~rc1") == 1
    assert rpmvercmp(db_conn, "1.0~rc1", "1.0~rc1^git1") == -1
    assert rpmvercmp(db_conn, "1.0^git1~pre", "1.0^git1~pre") == 0
    assert rpmvercmp(db_conn, "1.0^git1", "1.0^git1~pre") == 1
    assert rpmvercmp(db_conn, "1.0^git1~pre", "1.0^git1") == -1


def _typed_sql_array(ver: str) -> str:
    """
    Create sql array string in long notation.
    Example '1a' -> 'ARRAY[(1,null)::evr_array_item,(0,'a')::evr_array_item'
    """

    res = rpm_utils.rpmver2sqlarray(ver)
    res = re.sub(r"([A-Za-z]+)", r"'\1'", res)
    res = res.replace("{", "ARRAY[")
    res = res.replace("}", "]")
    res = res.replace(",)", ",null)")
    res = res.replace('"', '')
    res = res.replace(")", ")::evr_array_item")
    return res


def test_sql_array():
    """
    Test sql array building.
    """

    act = _typed_sql_array("1a")
    exp = "ARRAY[(1,null)::evr_array_item,(0,'a')::evr_array_item,(-2,null)::evr_array_item]"
    assert act == exp


def rpmvercmp(db_conn, ver1: str, ver2: str) -> int:
    """
    Compare two rpm version/release strings using sql comparison.
    return: 0: equal, 1: first is greater, -1: second is greater.
    """

    cur = db_conn.cursor()
    cur.execute("""select a, b, a = b, a > b from (values (%s, %s)) as t (a, b)"""
                % (_typed_sql_array(ver1), _typed_sql_array(ver2)))
    row = cur.fetchone()  # return comparison result and arrays for debugging
    if row[2]:
        return 0
    if row[3]:
        return 1
    return -1
