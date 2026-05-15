from src.models.mt.nllb_engine import NLLBTranslator


def test_nllb_translate() -> None:
    tr = NLLBTranslator()
    result = tr.translate("hello", "en", "ja")
    assert "en->ja" in result.text
