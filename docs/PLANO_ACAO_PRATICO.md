# 🛠️ PLANO DE AÇÃO PRÁTICO - CLARA
## Transformação Passo a Passo

**Objetivo:** Colocar o sistema em produção com qualidade hospitalar

---

## FASE 1: CORREÇÃO RÁPIDA (2 SEMANAS)

### Passo 1: Setup Seguro de Credenciais

#### 1.1 Criar arquivo `.env` (NUNCA COMMITAR NO GIT)

```bash
# .env (adicionar em .gitignore)
TASY_USER=TASY
TASY_PASSWORD=sua_senha_aqui
TASY_DSN=192.168.5.9:1521/TASYPRD
ORACLE_CLIENT_PATH=instantclient-basiclite-windows.x64-23.6.0.24.10/instantclient_23_6

# WhatsApp (se usar API futura)
WHATSAPP_API_KEY=seu_token_aqui
WHATSAPP_PHONE_ID=seu_phone_id_aqui
```

#### 1.2 Atualizar `main.py` para usar variáveis de ambiente

```python
# NO TOPO DO ARQUIVO - ANTES DE QUALQUER OUTRO CÓDIGO
from dotenv import load_dotenv
import os

load_dotenv()  # Carrega variáveis do .env

def conectar_tasy():
    """Conecta ao banco de dados Oracle usando credenciais seguras"""
    db_user = os.getenv("TASY_USER")
    db_password = os.getenv("TASY_PASSWORD")
    db_dsn = os.getenv("TASY_DSN")
    
    if not all([db_user, db_password, db_dsn]):
        raise ValueError("Variáveis de ambiente TASY não configuradas!")
    
    connection = oracledb.connect(
        user=db_user, 
        password=db_password, 
        dsn=db_dsn
    )
    return connection

# REMOVER LINHAS ANTIGAS:
# db_password = "<REMOVIDA>"  # ❌ DELETAR ESTA LINHA!
```

#### 1.3 Atualizar `.gitignore`

```gitignore
# Variáveis de ambiente
.env
.env.local
.env.*.local

# Logs
log.txt
*.log
logs/

# Cache Python
__pycache__/
*.py[cod]
*$py.class

# Ambientes virtuais
venv/
.venv/
env/

# IDE
.vscode/
.idea/

# Dados sensíveis
profile/
*.xlsx
```

---

### Passo 2: Melhorar Validação de Telefone

#### 2.1 Criar arquivo `validators.py` (novo)

```python
"""
validators.py
Funções de validação para dados do sistema CLARA
"""
import re
from typing import Union

class TelefoneValidator:
    """Valida e normaliza números de telefone brasileiros"""
    
    # DDDs válidos no Brasil
    DDDS_VALIDOS = {
        # Sul
        41, 42, 43, 44, 45, 46,  # PR
        47, 48, 49,               # SC
        51, 52, 53, 54, 55,       # RS
        
        # Sudeste
        11, 12, 13, 14, 15, 16, 17, 18, 19,  # SP
        21, 22, 24,               # RJ
        27, 28,                   # ES
        31, 32, 33, 34, 35, 37, 38,  # MG
        
        # Nordeste
        61, 62, 64,               # DF/GO
        63, 64, 68,               # TO/MT/MS
        71, 73, 74, 75, 77,       # BA
        81, 82, 83, 84, 85, 87, 88,  # CE/AL/PE/PB/PI/RN/MA
        86, 89,                   # PI/MA
        
        # Norte
        91, 92, 93, 94, 95, 96, 97, 98, 99,  # PA/AM/AP/RO/AC/RR/TO/MA/AP
    }
    
    @staticmethod
    def normalizar(numero: str) -> str:
        """
        Remove caracteres especiais mantendo apenas dígitos
        
        Exemplos:
            "(21) 99817-5736" → "21998175736"
            "+55 21 99817-5736" → "21998175736"
        """
        # Remove espaços, parênteses, hífens, etc
        numero_limpo = re.sub(r'\D', '', numero)
        
        # Se começar com 55 (código Brasil), remover
        if numero_limpo.startswith('55') and len(numero_limpo) == 13:
            numero_limpo = numero_limpo[2:]
        
        return numero_limpo
    
    @staticmethod
    def validar(numero: str) -> dict:
        """
        Valida número de telefone com feedback detalhado
        
        Returns:
            {
                'valido': bool,
                'tipo': 'celular'|'fixo'|'inválido',
                'ddd': int|None,
                'numero_normalizado': str,
                'mensagem': str
            }
        """
        numero_norm = TelefoneValidator.normalizar(numero)
        
        # Verificar tamanho mínimo
        if len(numero_norm) < 10:
            return {
                'valido': False,
                'tipo': 'inválido',
                'ddd': None,
                'numero_normalizado': numero_norm,
                'mensagem': f'Número incompleto: {numero_norm} ({len(numero_norm)} dígitos)'
            }
        
        # Extrair DDD (2 primeiros dígitos)
        ddd = int(numero_norm[:2])
        
        # Validar DDD
        if ddd not in TelefoneValidator.DDDS_VALIDOS:
            return {
                'valido': False,
                'tipo': 'inválido',
                'ddd': ddd,
                'numero_normalizado': numero_norm,
                'mensagem': f'DDD inválido: ({ddd}). Não existe DDD de duas letras {ddd} no Brasil'
            }
        
        # Verificar se é celular (9º dígito = 9) ou fixo (9º dígito ≠ 9)
        eh_celular = numero_norm[2] == '9'
        tipo_telefone = 'celular' if eh_celular else 'fixo'
        
        # Para RPA CLARA, apenas celulares são aceitos
        if len(numero_norm) == 10:
            # Formato antigo fixo (sem DDD)
            return {
                'valido': False,
                'tipo': 'fixo',
                'ddd': ddd,
                'numero_normalizado': numero_norm,
                'mensagem': f'Telefone fixo não é aceito. Necessário celular com 9º dígito = 9'
            }
        
        if len(numero_norm) == 11 and not eh_celular:
            return {
                'valido': False,
                'tipo': 'fixo',
                'ddd': ddd,
                'numero_normalizado': numero_norm,
                'mensagem': f'Telefone fixo ({numero_norm}). Necessário celular (9º dígito deve ser 9)'
            }
        
        if len(numero_norm) == 11 and eh_celular:
            return {
                'valido': True,
                'tipo': 'celular',
                'ddd': ddd,
                'numero_normalizado': numero_norm,
                'mensagem': f'✅ Celular válido: ({ddd}) {numero_norm[2:7]}-{numero_norm[7:]}'
            }
        
        return {
            'valido': False,
            'tipo': 'inválido',
            'ddd': ddd,
            'numero_normalizado': numero_norm,
            'mensagem': f'Formato não reconhecido: {numero_norm} ({len(numero_norm)} dígitos)'
        }

# ===== TESTES =====
if __name__ == "__main__":
    testes = [
        "21998175736",           # ✅ Válido
        "(21) 99817-5736",       # ✅ Válido
        "+55 21 99817-5736",     # ✅ Válido
        "2122223333",            # ❌ Fixo
        "99999999",              # ❌ Sem DDD
        "21912345678",           # ✅ Válido (Vivo/Claro SP)
        "(11) 2222-3333",        # ❌ Fixo SP
        "",                      # ❌ Vazio
    ]
    
    for numero in testes:
        resultado = TelefoneValidator.validar(numero)
        print(f"{numero:20} → {resultado['mensagem']}")
```

#### 2.2 Atualizar `main.py` para usar novo validator

```python
# No topo de main.py
from validators import TelefoneValidator

def filtrar_agendamentos_para_envio(df):
    """
    Filtra apenas agendamentos com números de celular válidos
    
    Versão melhorada com feedback
    """
    if df is None or df.empty:
        registrar_log("DataFrame vazio recebido em filtrar_agendamentos_para_envio")
        return pd.DataFrame()
    
    agendamentos_validos = []
    agendamentos_invalidos = []
    
    for idx, row in df.iterrows():
        telefone = str(row.get('TELEFONE', ''))
        nr_seq = row.get('NR_SEQ_AGENDA', 'N/A')
        nome_pac = row.get('NM_PACIENTE', 'N/A')
        
        # Validar telefone
        resultado = TelefoneValidator.validar(telefone)
        
        if resultado['valido']:
            # Normalizar o telefone na linha
            row['TELEFONE'] = resultado['numero_normalizado']
            agendamentos_validos.append(row)
            registrar_log(f"✅ {nr_seq} - {nome_pac}: {resultado['mensagem']}")
        else:
            agendamentos_invalidos.append({
                'NR_SEQ_AGENDA': nr_seq,
                'NM_PACIENTE': nome_pac,
                'TELEFONE_ORIGINAL': telefone,
                'MOTIVO': resultado['mensagem']
            })
            registrar_log(f"❌ {nr_seq} - {nome_pac}: {resultado['mensagem']}")
    
    # Log resumido
    registrar_log(f"\n📊 RESUMO DA VALIDAÇÃO:")
    registrar_log(f"  Total: {len(df)}")
    registrar_log(f"  ✅ Válidos: {len(agendamentos_validos)}")
    registrar_log(f"  ❌ Inválidos: {len(agendamentos_invalidos)}")
    
    if agendamentos_invalidos:
        registrar_log("\n⚠️ Agendamentos sem telefone válido:")
        df_invalidos = pd.DataFrame(agendamentos_invalidos)
        for _, row in df_invalidos.iterrows():
            registrar_log(f"  - {row['NR_SEQ_AGENDA']}: {row['MOTIVO']}")
    
    # Retornar apenas válidos como DataFrame
    if agendamentos_validos:
        return pd.DataFrame(agendamentos_validos)
    else:
        return pd.DataFrame()
```

---

### Passo 3: Melhorar Query SQL no TASY

#### 3.1 Criar `QUERY_AGENDAMENTOS_72H_MELHORADA.sql`

```sql
-- QUERY_AGENDAMENTOS_72H_MELHORADA.sql
-- Versão 2: Com filtro de telefone válido
-- Data: 2026-09-30
-- Melhorias: Valida telefone, trata formatos, remover brancos

SELECT
    EXTRACT(YEAR FROM a.dt_agenda)                  ANO,
    EXTRACT(MONTH FROM a.dt_agenda)                 MES,
    EXTRACT(DAY FROM a.dt_agenda)                   DIA,
    A.NR_SEQUENCIA                                  NR_SEQ_AGENDA,
    obter_cpf_pessoa_fisica(A.CD_PESSOA_FISICA)     NR_CPF,
    a.ie_classif_agenda                             CD_TIPO_AGENDA,
    'CLARA'                                         NM_USUARIO,                            
    to_char(a.dt_agenda, 'dd/mm/yyyy hh24:mi')      DT_AGENDA,
    A.CD_PESSOA_FISICA                              CD_PESSOA_FISICA,
    obter_cpf_pessoa_fisica(A.CD_PESSOA_FISICA)     CPF,
    TRIM(REPLACE(REPLACE(INITCAP(A.NM_PACIENTE), '1vez',''),'1 Vez','')) NM_PACIENTE,
    a.ie_status_agenda                              IE_STATUS_AGENDA,
    INITCAP(a.ds_status_agenda)                     DS_STATUS_AGENDA,
    
    -- TELEFONE MELHORADO: Remove espaços extras e valida formato
    TRIM(SUBSTR(
        REPLACE(REPLACE(REPLACE(REPLACE(A.NR_TELEFONE,'M:',''),'(',''),')',''),'-','')
        ,
        1, 
        12
    ))                                              TELEFONE,
    
    INITCAP(
        OBTER_CLASSIF_AGENDA_CONSULTA(
            a.ie_classif_agenda))                   DS_CLASSIF_AGENDA,
    b.cd_especialidade                              CD_ESPECIALIDADE,
    INITCAP(
        decode(
            B.cd_especialidade, 
            null, obter_especialidades_medico(B.cd_pessoa_fisica), 
            (
                SELECT 
                max(ds_especialidade) 
                FROM especialidade_medica 
                WHERE cd_especialidade = B.cd_especialidade)
                )
            )                                       DS_ESPECIALIDADE,
    b.cd_agenda                                     CD_AGENDA,
    INITCAP(REPLACE(b.ds_agenda,'(Nova)',''))       DS_AGENDA,
    INITCAP(
        COALESCE(
            obter_nome_medico(a.CD_MEDICO_REQ,'PS'), 
            obter_nome_medico(b.CD_PESSOA_FISICA,'PS')
        )
    )                                               NM_MEDICO_RESP
FROM 
    Agenda_Consulta_v a
    LEFT JOIN Agenda b ON (a.cd_agenda = b.cd_agenda)
    LEFT JOIN Convenio e ON (e.cd_convenio = a.cd_convenio)
WHERE 
    -- Filtro por data: próximas 72h
    trunc(a.dt_agenda) <= trunc(SYSDATE+3)
    AND trunc(a.dt_agenda) >= trunc(SYSDATE)
    
    -- Filtro por status: apenas agendamentos ativos
    AND a.IE_STATUS_AGENDA NOT IN ('L', 'C', 'B', 'II')  -- Lançado, Cancelado, Bloqueado, Informativo
    
    -- Filtro por data de criação: apenas agendamentos válidos
    AND A.CD_PESSOA_FISICA IS NOT NULL
    
    -- ⭐ NOVO: Validação rigorosa de telefone
    AND A.NR_TELEFONE IS NOT NULL
    AND LENGTH(TRIM(
        REPLACE(REPLACE(REPLACE(REPLACE(A.NR_TELEFONE,'M:',''),'(',''),')',''),'-','')
    )) = 11  -- Apenas números com 11 dígitos (DDD + 9 + 8 dígitos)
    AND SUBSTR(
        REPLACE(REPLACE(REPLACE(REPLACE(A.NR_TELEFONE,'M:',''),'(',''),')',''),'-',''),
        3,  -- 3º caractere
        1
    ) = '9'  -- Verifica se 9º dígito é 9 (celular)
    
    -- Filtro por especialidade/médico
    AND(
        b.cd_agenda IN (46,33,69,15,75,71,6,9,4,24,28,56,63,2,21,72,8)
        OR
        INITCAP(
            decode(
                B.cd_especialidade, 
                null, obter_especialidades_medico(B.cd_pessoa_fisica), 
                (
                    SELECT max(ds_especialidade) 
                    FROM especialidade_medica 
                    WHERE cd_especialidade = B.cd_especialidade
                )
            )
        ) IN (
            'Psicologia', 'Psiquiatria', 'Cardiologia', 'Ortopedia',
            'Pneumologia', 'Proctologia', 'Reumatologia', 'Clínica Médica'
        )
        OR UPPER(COALESCE(
            obter_nome_medico(a.CD_MEDICO_REQ,'PS'), 
            obter_nome_medico(b.CD_PESSOA_FISICA,'PS')
        )) LIKE UPPER('%Sylvio%')
        -- ... outros filtros de médico
    )
    
    -- Valida que médico existe
    AND COALESCE(
        obter_nome_medico(a.CD_MEDICO_REQ,'PS'), 
        obter_nome_medico(b.CD_PESSOA_FISICA,'PS')
    ) IS NOT NULL
    
ORDER BY 
    a.dt_agenda,
    b.ds_agenda,
    a.nm_paciente;
```

---

### Passo 4: Melhorar Tratamento de Erros

#### 4.1 Criar `exceptions.py` (novo)

```python
"""
exceptions.py
Exceções customizadas para o sistema CLARA
"""

class CLARAException(Exception):
    """Exceção base para o sistema CLARA"""
    pass

class TelefoneInvalidoException(CLARAException):
    """Telefone não passou na validação"""
    def __init__(self, numero, motivo):
        self.numero = numero
        self.motivo = motivo
        super().__init__(f"Telefone inválido ({numero}): {motivo}")

class ConexaoBancoDadosException(CLARAException):
    """Erro na conexão com banco de dados"""
    def __init__(self, mensagem):
        super().__init__(f"Erro de conexão com BD: {mensagem}")

class EnvioWhatsappException(CLARAException):
    """Erro ao enviar mensagem WhatsApp"""
    def __init__(self, numero, motivo):
        self.numero = numero
        self.motivo = motivo
        super().__init__(f"Falha ao enviar para {numero}: {motivo}")

class AtualizacaoTasyException(CLARAException):
    """Erro ao atualizar status no TASY"""
    def __init__(self, nr_seq, motivo):
        self.nr_seq = nr_seq
        self.motivo = motivo
        super().__init__(f"Falha ao atualizar agendamento {nr_seq}: {motivo}")
```

#### 4.2 Atualizar funções com melhor tratamento de erro

```python
# Em main.py
from exceptions import ConexaoBancoDadosException, AtualizacaoTasyException
import traceback

def update_confirmar_agenda(nr_seq_agenda, max_tentativas=3):
    """
    Atualiza status do agendamento no TASY com retry automático
    """
    registrar_log(f'update_confirmar_agenda({nr_seq_agenda}) - Início')
    
    for tentativa in range(1, max_tentativas + 1):
        try:
            caminho_instantclient = encontrar_diretorio_instantclient()
            if not caminho_instantclient:
                raise ConexaoBancoDadosException("Instant Client não encontrado")
            
            oracledb.init_oracle_client(lib_dir=caminho_instantclient)
            connection = conectar_tasy()  # Usa função com credenciais do .env
            
            nr_seq_agenda = int(nr_seq_agenda)
            
            with connection:
                with connection.cursor() as cursor:
                    sql = """ 
                        UPDATE agenda_consulta
                        SET    
                            cd_motivo_cancelamento = '',
                            nm_usuario_cancelamento = 'CLARA',
                            nm_usuario_status = 'CLARA',
                            nm_usuario = 'CLARA',
                            ie_status_agenda = 'N',
                            ds_confirmacao = 'WHATSAPP',
                            dt_confirmacao = SYSDATE,
                            dt_status = SYSDATE
                        WHERE nr_sequencia = :nr_seq_agenda                        
                    """
                    
                    cursor.execute(sql, {'nr_seq_agenda': nr_seq_agenda})
                    connection.commit()
            
            registrar_log(f"✅ Agendamento {nr_seq_agenda} confirmado com sucesso no TASY")
            return True
            
        except oracledb.DatabaseError as db_error:
            registrar_log(f"⚠️ Tentativa {tentativa}/{max_tentativas}: Erro Oracle - {db_error}")
            if tentativa < max_tentativas:
                time.sleep(2 ** tentativa)  # Backoff exponencial: 2s, 4s, 8s
            else:
                registrar_log(f"❌ Falha permanente ao atualizar {nr_seq_agenda}")
                raise AtualizacaoTasyException(nr_seq_agenda, str(db_error))
        
        except Exception as erro:
            registrar_log(f"❌ Erro inesperado na tentativa {tentativa}/{max_tentativas}: {erro}")
            registrar_log(traceback.format_exc())
            if tentativa == max_tentativas:
                raise AtualizacaoTasyException(nr_seq_agenda, str(erro))
    
    return False
```

---

### Passo 5: Testes Melhorados

#### 5.1 Criar `test_validators.py` (novo)

```python
"""
test_validators.py
Testes para o módulo de validação de telefones
"""
import pytest
from validators import TelefoneValidator

class TestTelefoneValidator:
    
    def test_celular_valido_simples(self):
        """Testa celular válido sem formatação"""
        resultado = TelefoneValidator.validar("21998175736")
        assert resultado['valido'] == True
        assert resultado['tipo'] == 'celular'
        assert resultado['ddd'] == 21
    
    def test_celular_valido_formatado(self):
        """Testa celular válido com formatação"""
        resultado = TelefoneValidator.validar("(21) 99817-5736")
        assert resultado['valido'] == True
        assert resultado['numero_normalizado'] == "21998175736"
    
    def test_celular_com_codigo_pais(self):
        """Testa celular com código de país"""
        resultado = TelefoneValidator.validar("+55 21 99817-5736")
        assert resultado['valido'] == True
        assert resultado['numero_normalizado'] == "21998175736"
    
    def test_telefone_fixo(self):
        """Testa rejeição de telefone fixo"""
        resultado = TelefoneValidator.validar("2122223333")
        assert resultado['valido'] == False
        assert resultado['tipo'] == 'fixo'
    
    def test_ddd_invalido(self):
        """Testa rejeição de DDD inválido"""
        resultado = TelefoneValidator.validar("99998888888")
        assert resultado['valido'] == False
        assert resultado['ddd'] == 99
    
    def test_numero_incompleto(self):
        """Testa rejeição de número incompleto"""
        resultado = TelefoneValidator.validar("9988888")
        assert resultado['valido'] == False
    
    def test_vazio(self):
        """Testa rejeição de entrada vazia"""
        resultado = TelefoneValidator.validar("")
        assert resultado['valido'] == False
    
    def test_normalizar_simples(self):
        """Testa normalização simples"""
        assert TelefoneValidator.normalizar("(21) 99817-5736") == "21998175736"
    
    def test_normalizar_com_espaco(self):
        """Testa normalização com espaços"""
        assert TelefoneValidator.normalizar("21 99817 5736") == "21998175736"
    
    def test_normalizar_com_codigo_pais(self):
        """Testa normalização com código de país"""
        assert TelefoneValidator.normalizar("+55 21 99817-5736") == "21998175736"
```

**Rodar testes:**
```bash
pytest test_validators.py -v
```

---

## CHECKLIST DA FASE 1

- [ ] Criar `.env` com variáveis de ambiente
- [ ] Adicionar `python-dotenv` em `requirements.txt`
- [ ] Criar `validators.py` com classe `TelefoneValidator`
- [ ] Criar `exceptions.py` com exceções customizadas
- [ ] Atualizar `main.py` para usar variáveis de ambiente
- [ ] Atualizar `main.py` para usar novo validador
- [ ] Criar `test_validators.py` com testes unitários
- [ ] Testar query SQL melhorada no TASY
- [ ] Atualizar `.gitignore`
- [ ] Rodar todos os testes: `pytest`
- [ ] Teste manual em staging
- [ ] Revisão de código (code review)
- [ ] Deploy em produção

---

## PRÓXIMAS FASES

### FASE 2: N8n Integration
- [ ] Provisionar instância N8n
- [ ] Criar workflow de conexão Oracle
- [ ] Integrar WhatsApp Business API
- [ ] Migrar lógica de Python para N8n

### FASE 3: Excelência
- [ ] Dashboard de confirmações
- [ ] Alertas em tempo real
- [ ] Relatórios automáticos
- [ ] Conformidade LGPD

---

**Preparado por:** Análise Sistema CLARA  
**Versão:** 1.0  
**Status:** Pronto para implementação
