"""Histórico local (SQLite) de envios e respostas."""

import sqlite3
from contextlib import closing
from datetime import datetime


class Database:
    def __init__(self, db_path):
        self.db_path = str(db_path)
        with closing(self._conn()) as conn, conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS envios (
                    id               INTEGER PRIMARY KEY,
                    nr_seq_agenda    INTEGER NOT NULL,
                    nm_paciente      TEXT,
                    dt_agenda        TEXT,
                    celular_paciente TEXT,
                    destino          TEXT NOT NULL,
                    modo             TEXT NOT NULL,      -- TESTE | PRODUCAO
                    message_id       TEXT,
                    dt_envio         TEXT NOT NULL,
                    resposta         TEXT,
                    dt_resposta      TEXT,
                    confirmou        INTEGER DEFAULT 0,
                    confirmado_tasy  INTEGER DEFAULT 0
                )""")
            conn.execute("CREATE INDEX IF NOT EXISTS ix_envios_destino ON envios(destino, dt_envio)")

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def registrar_envio(self, agenda, destino, modo, message_id):
        with closing(self._conn()) as conn, conn:
            conn.execute(
                """INSERT INTO envios (nr_seq_agenda, nm_paciente, dt_agenda, celular_paciente,
                                       destino, modo, message_id, dt_envio)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (int(agenda["nr_seq_agenda"]), agenda.get("nm_paciente"), agenda.get("dt_agenda"),
                 agenda.get("celular"), destino, modo, message_id, datetime.now().isoformat(sep=' ', timespec='seconds')),
            )

    def ja_enviado(self, nr_seq_agenda):
        with closing(self._conn()) as conn:
            return conn.execute(
                "SELECT 1 FROM envios WHERE nr_seq_agenda = ? AND modo = 'PRODUCAO'",
                (int(nr_seq_agenda),),
            ).fetchone() is not None

    def envio_pendente(self, destino):
        """Último envio ainda não confirmado para este número, dos últimos 4 dias."""
        with closing(self._conn()) as conn:
            return conn.execute(
                """SELECT * FROM envios
                   WHERE destino = ? AND confirmou = 0 AND dt_envio >= datetime('now', 'localtime', '-4 days')
                   ORDER BY dt_envio DESC LIMIT 1""",
                (destino,),
            ).fetchone()

    def registrar_resposta(self, envio_id, texto, confirmou, confirmado_tasy=False):
        with closing(self._conn()) as conn, conn:
            conn.execute(
                """UPDATE envios SET resposta = ?, dt_resposta = ?, confirmou = ?, confirmado_tasy = ?
                   WHERE id = ?""",
                (texto, datetime.now().isoformat(sep=' ', timespec='seconds'), int(confirmou), int(confirmado_tasy), envio_id),
            )
