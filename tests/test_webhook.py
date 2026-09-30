import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from webhook_server import numero_remetente, texto_da_mensagem


class TestWebhook(unittest.TestCase):
    def test_numero_remetente(self):
        casos = [
            ({"remoteJid": "5521988887777@s.whatsapp.net"}, "5521988887777"),
            ({"remoteJid": "552188887777@s.whatsapp.net"}, "5521988887777"),
            ({"remoteJid": "123456789@lid", "remoteJidAlt": "5521988887777@s.whatsapp.net"}, "5521988887777"),
            ({"remoteJid": "123456789@lid"}, None),
            ({"remoteJid": "120363000000@g.us"}, None),
            ({}, None),
        ]
        for key, esperado in casos:
            with self.subTest(key=key):
                self.assertEqual(numero_remetente(key), esperado)

    def test_texto_da_mensagem(self):
        self.assertEqual(texto_da_mensagem({"conversation": " 1 "}), "1")
        self.assertEqual(texto_da_mensagem({"extendedTextMessage": {"text": "sim"}}), "sim")
        self.assertEqual(texto_da_mensagem({"imageMessage": {}}), "")
        self.assertEqual(texto_da_mensagem(None), "")


if __name__ == "__main__":
    unittest.main()
