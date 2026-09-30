# 🚀 GUIA PRÁTICO - OPÇÃO 1 (PYTHON MULTI-CANAL)
## Implementação Passo a Passo

**Versão:** 1.0  
**Data:** 2026-09-30  
**Duração:** 5-6 semanas  
**Custo:** R$ 0 (desenvolvimento interno)  
**Tecnologia:** Python 3.10+ | Linux | SQLite | Selenium | Email/SMS

---

## 📋 PRÉ-REQUISITOS

### Infraestrutura HSF
- [ ] Servidor Linux (Ubuntu 20.04+) com Python 3.10+
- [ ] SMTP do hospital funcionando
- [ ] Acesso à rede interna
- [ ] Acesso ao banco Oracle TASY
- [ ] (Opcional) Gateway SMS disponível

### Equipe
- [ ] 2-3 Desenvolvedores Python
- [ ] 1 DBA (para queries Oracle)
- [ ] 1 DevOps (para deploy/monitoring)

### Validar com TI
```bash
# Checklist antes de começar
[ ] Oracle client instalado? (versão?)
[ ] SMTP testado? (pode enviar email?)
[ ] SMS disponível? (qual gateway?)
[ ] Python 3.10+ instalado?
[ ] Git configurado?
[ ] Servidor Linux preparado?
```

---

## 📁 ESTRUTURA FINAL

```
HSF_WHATSAPP_CLARA_V2/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point
│   ├── config.py                  # Carrega .env
│   ├── database.py                # SQLite local
│   │
│   ├── channels/                  # 3 canais de notificação
│   │   ├── __init__.py
│   │   ├── base.py               # Classe base abstrata
│   │   ├── whatsapp.py           # Canal WhatsApp Web
│   │   ├── sms.py                # Canal SMS
│   │   └── email.py              # Canal Email
│   │
│   ├── orchestrator.py            # Orquestra os canais
│   ├── response_monitor.py        # Monitora respostas
│   ├── validators.py             # Validações
│   ├── tasy_connector.py          # Integração Oracle
│   ├── logger.py                  # Logs estruturados
│   └── dashboard.py              # Web interface
│
├── tests/
│   ├── test_validators.py
│   ├── test_channels.py
│   ├── test_orchestrator.py
│   └── test_integration.py
│
├── config/
│   ├── .env.example
│   ├── .env (local - git ignored)
│   ├── requirements.txt
│   └── settings.json
│
├── sql/
│   ├── QUERY_AGENDAMENTOS_24H.sql
│   ├── QUERY_AGENDAMENTOS_48H.sql
│   └── QUERY_AGENDAMENTOS_72H.sql
│
├── logs/
│   └── (criado em runtime)
│
├── docker-compose.yml (opcional - para facilitar deploy)
├── Dockerfile (opcional)
└── README.md
```

---

## ⚙️ ARQUITETURA MULTI-CANAL

```
┌─────────────────────────────────────────────────────────┐
│                     MAIN.PY (Orquestrador)              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Conectar Oracle TASY                               │
│  2. Executar query (agendamentos próximas 48h)         │
│  3. Para cada agendamento:                             │
│     ├─ Validar telefone/email                          │
│     ├─ Chamar Orchestrator.enviar()                    │
│     └─ Registrar resultado no SQLite                   │
│  4. Iniciar ResponseMonitor                            │
│  5. Atualizar TASY com confirmações                    │
│  6. Gerar relatório do dia                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
            ├─ Orchestrator (escolhe canal)
            │
            ├─ WhatsappChannel
            │  ├─ Selenium + PyAutoGUI
            │  ├─ Enviar mensagem
            │  └─ Monitora resposta via WhatsApp Web
            │
            ├─ SMSChannel (if available)
            │  ├─ Integra com gateway HSF
            │  ├─ Envia SMS
            │  └─ Monitora resposta via SMS
            │
            └─ EmailChannel
               ├─ SMTP do hospital
               ├─ Envia email com link
               └─ Monitora click no link
```

---

## 🔧 SEMANA 1: SETUP + WHATSAPP MELHORADO

### Passo 1: Setup Inicial

```bash
# 1. Clonar/preparar repo
cd /home/hsf/clara_v2
git clone ... (ou init)

# 2. Criar ambiente virtual
python3.10 -m venv venv
source venv/bin/activate

# 3. Instalar dependências
pip install -r config/requirements.txt

# 4. Copiar .env
cp config/.env.example .env
# Editar .env com valores reais
nano .env
```

### Passo 2: Criar `config.py`

```python
# src/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Banco de dados
    TASY_USER = os.getenv("TASY_USER")
    TASY_PASSWORD = os.getenv("TASY_PASSWORD")
    TASY_DSN = os.getenv("TASY_DSN")
    
    # Notificações
    SMTP_SERVER = os.getenv("SMTP_SERVER", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_FROM = os.getenv("SMTP_FROM", "clara@hsf.com.br")
    
    # SMS (optional)
    SMS_GATEWAY_URL = os.getenv("SMS_GATEWAY_URL")
    SMS_API_KEY = os.getenv("SMS_API_KEY")
    
    # WhatsApp
    WHATSAPP_PROFILE = os.getenv("WHATSAPP_PROFILE", "profile/wpp")
    
    # Timeouts
    WHATSAPP_TIMEOUT = int(os.getenv("WHATSAPP_TIMEOUT", "30"))
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    LOGS_DIR = BASE_DIR / "logs"
    DB_PATH = BASE_DIR / "data" / "clara.db"
    
    def __post_init__(self):
        self.LOGS_DIR.mkdir(exist_ok=True)
        self.DB_PATH.parent.mkdir(exist_ok=True)

config = Config()
```

### Passo 3: Criar Base de Dados SQLite

```python
# src/database.py
import sqlite3
from datetime import datetime
from pathlib import Path

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Cria tabelas se não existirem"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Tabela de agendamentos processados
        c.execute('''
            CREATE TABLE IF NOT EXISTS agendamentos (
                id INTEGER PRIMARY KEY,
                nr_seq_agenda INTEGER UNIQUE,
                nr_cpf TEXT,
                nm_paciente TEXT,
                dt_agenda TEXT,
                telefone TEXT,
                email TEXT,
                especialidade TEXT,
                medico TEXT,
                
                -- Rastreamento de envio
                canal_envio TEXT,
                dt_envio TEXT,
                status_envio TEXT,  -- 'OK', 'FALHA', 'PENDENTE'
                erro_msg TEXT,
                
                -- Rastreamento de resposta
                respondeu BOOLEAN DEFAULT 0,
                tipo_resposta TEXT,  -- 'WHATSAPP', 'SMS', 'EMAIL'
                dt_resposta TEXT,
                resposta_texto TEXT,
                
                -- Status TASY
                atualizado_tasy BOOLEAN DEFAULT 0,
                dt_atualizacao_tasy TEXT,
                
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de logs
        c.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                nivel TEXT,
                modulo TEXT,
                mensagem TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def inserir_agendamento(self, dados):
        """Insere agendamento novo"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute('''
                INSERT INTO agendamentos 
                (nr_seq_agenda, nr_cpf, nm_paciente, dt_agenda, telefone, 
                 email, especialidade, medico, status_envio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dados['nr_seq_agenda'],
                dados['nr_cpf'],
                dados['nm_paciente'],
                dados['dt_agenda'],
                dados['telefone'],
                dados.get('email', ''),
                dados['especialidade'],
                dados['medico'],
                'PENDENTE'
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Já existe
        finally:
            conn.close()
    
    def atualizar_envio(self, nr_seq_agenda, canal, status, erro=None):
        """Atualiza status do envio"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            UPDATE agendamentos 
            SET canal_envio=?, status_envio=?, dt_envio=?, erro_msg=?
            WHERE nr_seq_agenda=?
        ''', (canal, status, datetime.now().isoformat(), erro, nr_seq_agenda))
        
        conn.commit()
        conn.close()
```

### Passo 4: Criar Classe Base para Canais

```python
# src/channels/base.py
from abc import ABC, abstractmethod
from enum import Enum

class StatusEnvio(Enum):
    SUCESSO = "OK"
    FALHA = "FALHA"
    PENDENTE = "PENDENTE"

class CanalBase(ABC):
    """Classe base abstrata para canais de notificação"""
    
    def __init__(self, config):
        self.config = config
        self.nome = self.__class__.__name__
    
    @abstractmethod
    def validar(self, contato: str) -> bool:
        """Valida se contato é válido para este canal"""
        pass
    
    @abstractmethod
    def enviar(self, paciente: dict) -> dict:
        """
        Envia notificação
        
        Returns:
            {
                'status': StatusEnvio,
                'mensagem': 'OK ou motivo do erro',
                'id_externo': 'ID da mensagem no canal'
            }
        """
        pass
    
    @abstractmethod
    def monitorar_resposta(self, paciente: dict) -> dict:
        """
        Monitora resposta do paciente
        
        Returns:
            {
                'respondeu': bool,
                'resposta': 'texto da resposta',
                'timestamp': 'quando respondeu'
            }
        """
        pass
```

### Passo 5: Melhorar Canal WhatsApp

```python
# src/channels/whatsapp.py
from channels.base import CanalBase, StatusEnvio
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re

class WhatsappChannel(CanalBase):
    
    def __init__(self, config):
        super().__init__(config)
        self.driver = None
        self.inicializar_driver()
    
    def inicializar_driver(self):
        """Inicializa Selenium WebDriver com profile do WhatsApp"""
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-data-dir={self.config.WHATSAPP_PROFILE}")
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://web.whatsapp.com")
        time.sleep(5)  # Esperar carregar
    
    def validar(self, telefone: str) -> bool:
        """Valida se é celular brasileiro válido"""
        # Remove caracteres especiais
        numero = re.sub(r'\D', '', telefone)
        
        # Deve ter 11 dígitos (DDD + 9 + 8 dígitos)
        if len(numero) != 11:
            return False
        
        # 9º dígito deve ser 9 (celular)
        if numero[2] != '9':
            return False
        
        return True
    
    def enviar(self, paciente: dict) -> dict:
        """Envia mensagem via WhatsApp Web"""
        try:
            telefone = paciente['telefone']
            
            # Validar
            if not self.validar(telefone):
                return {
                    'status': StatusEnvio.FALHA,
                    'mensagem': f'Telefone inválido: {telefone}',
                    'id_externo': None
                }
            
            # Preparar mensagem
            mensagem = self._preparar_mensagem(paciente)
            
            # Abrir chat
            url = f"https://web.whatsapp.com/send?phone={telefone}&text="
            self.driver.get(url)
            time.sleep(3)
            
            # Digitar mensagem (com pequenos delays)
            input_box = self.driver.find_element(By.XPATH, 
                "//div[@contenteditable='true']")
            input_box.click()
            
            # Digitar letra por letra (evita problemas de input)
            for char in mensagem:
                input_box.send_keys(char)
                time.sleep(0.01)
            
            # Enviar (Ctrl+Enter)
            self.driver.find_element(By.XPATH, 
                "//button[@aria-label='Send message']").click()
            
            time.sleep(2)
            
            return {
                'status': StatusEnvio.SUCESSO,
                'mensagem': 'Enviado com sucesso',
                'id_externo': f"whatsapp_{telefone}_{int(time.time())}"
            }
        
        except Exception as e:
            return {
                'status': StatusEnvio.FALHA,
                'mensagem': f'Erro ao enviar: {str(e)}',
                'id_externo': None
            }
    
    def monitorar_resposta(self, paciente: dict) -> dict:
        """Monitora se paciente respondeu"""
        try:
            # Abrir chat
            telefone = paciente['telefone']
            self.driver.get(f"https://web.whatsapp.com/send?phone={telefone}")
            time.sleep(2)
            
            # Procura por mensagens não lidas
            mensagens = self.driver.find_elements(By.CSS_SELECTOR, 
                "div[class*='message-in']")
            
            if mensagens:
                ultima = mensagens[-1].text
                
                # Verificar se contém "1" ou "sim" ou "confirmado"
                if any(word in ultima.lower() 
                       for word in ['1', 'sim', 'confirmado', 'confirmo']):
                    return {
                        'respondeu': True,
                        'resposta': ultima,
                        'timestamp': time.time()
                    }
            
            return {
                'respondeu': False,
                'resposta': None,
                'timestamp': None
            }
        
        except Exception as e:
            return {
                'respondeu': False,
                'resposta': None,
                'timestamp': None
            }
    
    def _preparar_mensagem(self, paciente: dict) -> str:
        """Prepara mensagem formatada"""
        return f"""*Paz e bem!*

Prezado(a) *{paciente['nm_paciente']}*,

gostaríamos de lembrar que no dia: *{paciente['dt_agenda']}*

está agendado: *{paciente['especialidade']}*

com dr(a): *{paciente['medico']}*

Para confirmar, por favor responda com o número *1*

Caso precise cancelar ou reagendar, ligue para: *(21)3294-4500*

Hospital São Francisco na Providência de Deus"""
    
    def fechar(self):
        """Fecha o driver"""
        if self.driver:
            self.driver.quit()
```

---

## 📊 SEMANA 2-4: SMS + EMAIL + ORQUESTRAÇÃO

### Canal SMS

```python
# src/channels/sms.py
class SMSChannel(CanalBase):
    """Integração com gateway SMS HSF"""
    
    def __init__(self, config):
        super().__init__(config)
        self.gateway_url = config.SMS_GATEWAY_URL
        self.api_key = config.SMS_API_KEY
    
    def validar(self, telefone: str) -> bool:
        # Mesmo validador do WhatsApp
        numero = re.sub(r'\D', '', telefone)
        return len(numero) == 11 and numero[2] == '9'
    
    def enviar(self, paciente: dict) -> dict:
        # Integração com API SMS do HSF
        # Detalhes dependem do provider
        pass
```

### Canal Email

```python
# src/channels/email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailChannel(CanalBase):
    
    def validar(self, email: str) -> bool:
        """Valida formato básico de email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def enviar(self, paciente: dict) -> dict:
        try:
            email_dest = paciente.get('email')
            
            if not self.validar(email_dest):
                return {
                    'status': StatusEnvio.FALHA,
                    'mensagem': f'Email inválido: {email_dest}',
                    'id_externo': None
                }
            
            # Gerar token de confirmação único
            import secrets
            token = secrets.token_urlsafe(32)
            
            # Preparar email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Confirmação de Agendamento - {paciente['nm_paciente']}"
            msg['From'] = self.config.SMTP_FROM
            msg['To'] = email_dest
            
            # Link de confirmação
            link = f"http://hsf-internal/clara/confirmar?token={token}"
            
            html = f"""
            <html>
                <body>
                    <h2>Confirmação de Agendamento</h2>
                    <p>Prezado(a) {paciente['nm_paciente']},</p>
                    <p>Seu agendamento está confirmado para:</p>
                    <ul>
                        <li><strong>Data:</strong> {paciente['dt_agenda']}</li>
                        <li><strong>Especialidade:</strong> {paciente['especialidade']}</li>
                        <li><strong>Médico:</strong> {paciente['medico']}</li>
                    </ul>
                    <p><a href="{link}">Clique aqui para confirmar</a></p>
                    <p>Hospital São Francisco</p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            # Enviar
            with smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT) as server:
                server.starttls()
                server.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)
                server.send_message(msg)
            
            return {
                'status': StatusEnvio.SUCESSO,
                'mensagem': 'Email enviado',
                'id_externo': token
            }
        
        except Exception as e:
            return {
                'status': StatusEnvio.FALHA,
                'mensagem': f'Erro ao enviar email: {str(e)}',
                'id_externo': None
            }
```

### Orquestrador Multi-canal

```python
# src/orchestrator.py
class Orchestrator:
    """Escolhe o melhor canal para cada paciente"""
    
    def __init__(self, config, db):
        self.config = config
        self.db = db
        self.canais = {
            'whatsapp': None,  # Inicializar depois
            'sms': None,
            'email': None
        }
    
    def enviar(self, paciente: dict) -> dict:
        """
        Tenta enviar por canais em ordem de prioridade
        Fallback automático se um falhar
        """
        
        # Prioridade 1: SMS (mais direto)
        if self._tem_telefone_valido(paciente):
            resultado = self.canais['sms'].enviar(paciente)
            if resultado['status'] == StatusEnvio.SUCESSO:
                return resultado
        
        # Prioridade 2: WhatsApp (mais popular)
        if self._tem_telefone_valido(paciente):
            resultado = self.canais['whatsapp'].enviar(paciente)
            if resultado['status'] == StatusEnvio.SUCESSO:
                return resultado
        
        # Prioridade 3: Email (sempre funciona)
        if self._tem_email_valido(paciente):
            resultado = self.canais['email'].enviar(paciente)
            if resultado['status'] == StatusEnvio.SUCESSO:
                return resultado
        
        # Nenhum canal disponível
        return {
            'status': StatusEnvio.FALHA,
            'mensagem': 'Nenhum canal disponível para este paciente',
            'id_externo': None
        }
    
    def _tem_telefone_valido(self, paciente) -> bool:
        telefone = paciente.get('telefone', '')
        return self.canais['whatsapp'].validar(telefone)
    
    def _tem_email_valido(self, paciente) -> bool:
        email = paciente.get('email', '')
        return self.canais['email'].validar(email)
```

---

## 🚀 SEMANA 5-6: DEPLOYMENT

### Deploy em Linux

```bash
# 1. Preparar servidor
sudo apt-get update
sudo apt-get install -y python3.10 python3.10-venv git

# 2. Clonar repo
cd /opt/clara
sudo git clone <repo> .

# 3. Setup venv
python3.10 -m venv venv
source venv/bin/activate
pip install -r config/requirements.txt

# 4. Setup .env
sudo cp config/.env.example .env
sudo nano .env  # Preencher valores reais

# 5. Setup systemd service (para rodar como daemon)
sudo cp deployment/clara.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable clara
sudo systemctl start clara

# 6. Verificar logs
sudo journalctl -u clara -f
```

### Monitoramento

```python
# src/monitoring.py
import logging
import smtplib

class Alertas:
    """Sistema de alertas para falhas"""
    
    def __init__(self, config):
        self.config = config
    
    def alerta_falhas(self, nr_falhas):
        """Envia email se muitas falhas"""
        if nr_falhas > 10:
            # Enviar email para TI
            # webhook Slack, etc
            pass
    
    def alerta_baixa_taxa(self, taxa_sucesso):
        """Alerta se taxa < 80%"""
        if taxa_sucesso < 0.80:
            # Alertar para investigação
            pass
```

---

## ✅ CHECKLIST IMPLEMENTAÇÃO

### Semana 1
- [ ] Setup infraestrutura
- [ ] Criar config.py
- [ ] Criar database.py + tabelas SQLite
- [ ] Criar channels/base.py
- [ ] Aprimorar channels/whatsapp.py
- [ ] Testes unitários passando

### Semana 2-3
- [ ] Implementar channels/sms.py
- [ ] Implementar channels/email.py
- [ ] Criar orchestrator.py
- [ ] Testes de integração

### Semana 4-5
- [ ] ResponseMonitor funcionando
- [ ] Dashboard web básico
- [ ] Alertas configurados
- [ ] Testes de carga

### Semana 5-6
- [ ] Deploy staging
- [ ] Testes finais
- [ ] Deploy produção
- [ ] Suporte 24/7 primeira semana

---

## 📞 SUPORTE E TROUBLESHOOTING

**Se WhatsApp Web quebrar:**
1. Verificar se interface mudou (seletores XPATH)
2. Rodar com driver headful (screenshot) para debug
3. Fallback automático para SMS/Email

**Se SMS falhar:**
1. Verificar disponibilidade gateway
2. Verificar quota
3. Fallback para Email

**Altos custos?**
1. Não há custos adicionais (zero budget)
2. Roda em servidor existente
3. ROI cobrindo custo de TI em dias

---

**Próximo passo:** Iniciar Semana 1 com reunião kick-off! 🚀

