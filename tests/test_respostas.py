import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from respostas import eh_confirmacao


class TestEhConfirmacao(unittest.TestCase):
    def test_confirma(self):
        for texto in ["1", " 1 ", "Sim", "sim, obrigado", "Confirmo!", "CONFIRMADO", "confirma sim"]:
            with self.subTest(texto=texto):
                self.assertTrue(eh_confirmacao(texto))

    def test_nao_confirma(self):
        for texto in ["", None, "oi", "não confirmo", "Nao posso ir", "10", "quero remarcar", "2"]:
            with self.subTest(texto=texto):
                self.assertFalse(eh_confirmacao(texto))


if __name__ == "__main__":
    unittest.main()
