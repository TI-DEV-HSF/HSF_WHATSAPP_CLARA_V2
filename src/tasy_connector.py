"""
Conector Oracle TASY
Busca agendamentos e atualiza status
"""

import json
from pathlib import Path

import oracledb

BASE_DIR = Path(__file__).resolve().parent.parent
SQL_DIR = BASE_DIR / "sql"
QUERIES_POR_HORIZONTE = {
    24: "QUERY_AGENDAMENTOS_24H.sql",
    48: "QUERY_AGENDAMENTOS_48H.sql",
    72: "QUERY_AGENDAMENTOS_72H.sql",
}


def inicializar_oracle_client():
    """Carrega o Oracle Client em Thick Mode (TASY exige: verifier 0x939 não roda em Thin)."""
    possibilidades = [
        BASE_DIR / "instantclient_23_6",
        Path("C:/instantclient_23_6"),
        Path("C:/instantclient_21_13"),
        Path("C:/instantclient_19_23"),
        Path("C:/instantclient"),
        Path("C:/oracle/instantclient"),
    ]

    for caminho in possibilidades:
        if (caminho / "oci.dll").exists():
            try:
                oracledb.init_oracle_client(lib_dir=str(caminho))
                print(f"✅ Oracle Client carregado em Thick Mode: {caminho}")
                return True
            except oracledb.ProgrammingError:
                return True
            except Exception as e:
                print(f"⚠️ Tentativa com {caminho} falhou: {e}")

    print("❌ Oracle Client não encontrado. Ver INSTALAR_ORACLE_CLIENT.md")
    return False


inicializar_oracle_client()


class TasyConnector:
    """Conecta ao Oracle TASY e busca agendamentos"""

    def __init__(self, config):
        self.config = config
        self.connection = None
        self.conectado = False

    def conectar(self):
        try:
            print(f"🔗 Conectando ao TASY: {self.config.TASY_DSN}...")
            self.connection = oracledb.connect(
                user=self.config.TASY_USER,
                password=self.config.TASY_PASSWORD,
                dsn=self.config.TASY_DSN,
            )
            self.conectado = True
            print("✅ Conectado ao TASY com sucesso!")
            return True
        except oracledb.DatabaseError as e:
            print(f"❌ Erro ao conectar TASY: {e}")
            self.conectado = False
            return False

    def buscar_agendamentos_proximos(self, horas=48):
        """
        Executa a query de sql/QUERY_AGENDAMENTOS_{24,48,72}H.sql.
        Retorna lista de dicts com as colunas da query em minúsculo
        (nr_seq_agenda, nm_paciente, dt_agenda, telefone, ds_especialidade, nm_medico_resp, ...).
        """
        if not self.conectado:
            print("❌ Não conectado ao TASY")
            return []

        arquivo = QUERIES_POR_HORIZONTE.get(horas)
        if arquivo is None:
            raise ValueError(f"Horizonte {horas}h sem query. Use: {sorted(QUERIES_POR_HORIZONTE)}")

        sql = (SQL_DIR / arquivo).read_text(encoding="utf-8").strip().rstrip(";")

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                colunas = [d[0].lower() for d in cursor.description]
                agendamentos = [dict(zip(colunas, row)) for row in cursor.fetchall()]

            print(f"✅ {len(agendamentos)} agendamentos encontrados ({arquivo})")
            return agendamentos
        except oracledb.DatabaseError as e:
            print(f"❌ Erro ao buscar agendamentos: {e}")
            return []

    def atualizar_status_confirmado(self, nr_seq_agenda):
        """Confirma a agenda no TASY (mesmo UPDATE do CLARA v1 em produção)."""
        if not self.conectado:
            return False

        sql = """
            UPDATE agenda_consulta
            SET    cd_motivo_cancelamento = '',
                   nm_usuario_cancelamento = 'CLARA',
                   nm_usuario_status = 'CLARA',
                   nm_usuario = 'CLARA',
                   ie_status_agenda = 'N',
                   ds_confirmacao = 'WHATSAPP',
                   dt_confirmacao = SYSDATE,
                   dt_status = SYSDATE
            WHERE  nr_sequencia = :nr_seq_agenda
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, {"nr_seq_agenda": int(nr_seq_agenda)})
            self.connection.commit()
            print(f"✅ Status confirmado no TASY: {nr_seq_agenda}")
            return True
        except oracledb.DatabaseError as e:
            print(f"❌ Erro ao atualizar status: {e}")
            self.connection.rollback()
            return False

    def desconectar(self):
        if self.connection:
            self.connection.close()
            self.conectado = False
            print("✅ Desconectado do TASY")


if __name__ == "__main__":
    import sys
    from config import config

    horas = int(sys.argv[1]) if len(sys.argv) > 1 else 48
    tasy = TasyConnector(config)

    if tasy.conectar():
        agendamentos = tasy.buscar_agendamentos_proximos(horas)
        if agendamentos:
            com_telefone = sum(1 for a in agendamentos if a.get("telefone"))
            print(f"📞 Com telefone preenchido: {com_telefone}/{len(agendamentos)}")
            print("\n📋 Colunas retornadas:")
            print(json.dumps(sorted(agendamentos[0].keys()), indent=2))
        tasy.desconectar()
