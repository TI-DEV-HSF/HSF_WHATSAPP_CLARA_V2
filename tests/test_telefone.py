import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from telefone import normalizar_celular


class TestNormalizarCelular(unittest.TestCase):
    def test_formatos_validos(self):
        casos = {
            "M: (21)988887777 ": "5521988887777",
            "M: (21)988887777 R: (21) 22223333 ": "5521988887777",
            "M: (21) 98888-7777 R: (21) 97777-6666": "5521988887777",
            "21988887777": "5521988887777",
            "21 98888-7777": "5521988887777",
            "21 988887777": "5521988887777",
            "5521988887777": "5521988887777",
            "021988887777": "5521988887777",
            "21 98888 7777 ou 21 97777 6666": "5521988887777",
            "21988887777 21977776666": "5521988887777",
            "(21)22223333 / 21988887777": "5521988887777",
            "M: (21)88887777 ": "5521988887777",
            "552188887777": "5521988887777",
        }
        for bruto, esperado in casos.items():
            with self.subTest(bruto=bruto):
                self.assertEqual(normalizar_celular(bruto), esperado)

    def test_celular_na_residencial_quando_movel_e_fixo(self):
        self.assertEqual(
            normalizar_celular("M: (21)22223333 R: (21) 988887777 "), "5521988887777"
        )

    def test_invalidos(self):
        for bruto in [None, "", "21", "M: (21)  ", "22223333", "988887777", "(21)22223333"]:
            with self.subTest(bruto=bruto):
                self.assertIsNone(normalizar_celular(bruto))


if __name__ == "__main__":
    unittest.main()
