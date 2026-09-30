import sqlite3
from pathlib import Path
from datetime import datetime

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Cria tabelas se não existirem"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS agendamentos (
                id INTEGER PRIMARY KEY,
                nr_seq_agenda INTEGER UNIQUE,
                nm_paciente TEXT,
                dt_agenda TEXT,
                telefone TEXT,
                especialidade TEXT,
                medico TEXT,
                status_envio TEXT,
                dt_envio TEXT,
                respondeu BOOLEAN DEFAULT 0,
                dt_resposta TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        print(f"✅ Database criado: {self.db_path}")

    def inserir(self, dados):
        """Insere agendamento no banco"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO agendamentos
                (nr_seq_agenda, nm_paciente, dt_agenda, telefone, especialidade, medico, status_envio, dt_envio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dados.get('nr_seq_agenda'),
                dados.get('nm_paciente'),
                dados.get('dt_agenda'),
                dados.get('celular'),
                dados.get('ds_especialidade'),
                dados.get('nm_medico_resp'),
                'ENVIADO',
                datetime.now().isoformat()
            ))
            conn.commit()
            print(f"✅ Inserido: {dados.get('nm_paciente')}")
        except sqlite3.IntegrityError:
            print(f"⚠️ Agendamento já existe: {dados.get('nr_seq_agenda')}")
        finally:
            conn.close()

    def ja_enviado(self, nr_seq_agenda):
        conn = sqlite3.connect(self.db_path)
        try:
            return conn.execute(
                "SELECT 1 FROM agendamentos WHERE nr_seq_agenda = ?", (nr_seq_agenda,)
            ).fetchone() is not None
        finally:
            conn.close()

if __name__ == "__main__":
    from config import config
    db = Database(config.DB_PATH)
    print("✅ Database pronto!")
