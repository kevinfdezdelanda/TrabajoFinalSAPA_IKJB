import pytest
from unittest.mock import patch

@pytest.fixture
def mock_load_dataset(monkeypatch):
    # Esta función simulará `load_dataset` y devolverá un objeto simulado o estructura de datos
    def mock(*args, **kwargs):
        # Aquí debes definir una estructura de datos falsa que imite lo que esperarías de tu dataset real
        return {"dummy": "data"}  # Modifica esto según las necesidades de tus pruebas

    # Usar `monkeypatch` para reemplazar `load_dataset` con la función `mock`
    monkeypatch.setattr("datasets.load_dataset", mock)
