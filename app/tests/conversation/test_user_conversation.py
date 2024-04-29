import pytest
#from conversation.user_conversation import UserConversation


@pytest.mark.skip(reason="code refactor")
def test_get_citations_from_text():
    cites = []
    titles = ["Title 1", "Title 2"]
    sources = ["https://title1.com", "https://title2.com"]

    result = UserConversation.get_citations_from_text(cites, titles, sources)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["citation_text"] == "Title 1"
    assert result[0]["citation_path"] == "https://title1.com"
    assert result[1]["citation_text"] == "Title 2"
    assert result[1]["citation_path"] == "https://title2.com"


@pytest.mark.skip(reason="code refactor")
def test_get_citations_from_text_multiple_sections_returned():
    cites = []
    titles = ["Title 1", "Title 2", "Title 2"]
    sources = [
        "https://title1.com",
        "https://title2.com#section1",
        "https://title2.com#section2",
    ]

    result = UserConversation.get_citations_from_text(cites, titles, sources)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["citation_text"] == "Title 1"
    assert result[0]["citation_path"] == "https://title1.com"
    assert result[1]["citation_text"] == "Title 2"
    assert result[1]["citation_path"] == "https://title2.com"
