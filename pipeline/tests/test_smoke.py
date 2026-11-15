from atlas import mmg


def test_filename_pattern():
    m = mmg.FILE_RE.search("MMG2025_2019-2023_Data_To_Share_v2.xlsx")
    assert (m["ed"], m["y0"], m["y1"], m["v"]) == ("2025", "2019", "2023", "_v2")
    m = mmg.FILE_RE.search("MMG2011_2009Data_ToShare.xlsx")
    assert (m["ed"], m["y0"], m["y1"]) == ("2011", "2009", None)
