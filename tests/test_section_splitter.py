from segmentation.section_splitter import SectionSplitter


def test_section_splitter_basic():
    text = """
    ITEM 1A. RISK FACTORS
    We face volatility in the market.

    ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS
    Our operations may be impacted by supply chain issues.

    ITEM 3. LEGAL PROCEEDINGS
    We are subject to litigation.
    """
    splitter = SectionSplitter()
    sections = splitter.split(text)

    assert "volatility" in sections["risk_factors"].lower()
    assert "operations" in sections["mda"].lower()
    assert "litigation" in sections["legal"].lower()
