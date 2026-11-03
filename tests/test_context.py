from oido.context import classify

def kinds(text: str) -> set[str]:
    return {a.kind for a in classify(text)}

def test_detects_idea():
    assert "idea" in kinds("Se me ocurre que podríamos detectar acordes.")

def test_detects_roadmap():
    assert "roadmap" in kinds("Primero capturamos audio y después transcribimos.")

def test_detects_bug():
    assert "bug" in kinds("Hay un error y a veces se traba el micrófono.")

def test_falls_back_to_note():
    assert "note" in kinds("Compré pan en la tarde.")
