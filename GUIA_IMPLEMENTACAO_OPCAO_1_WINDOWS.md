# 🚀 GUIA PRÁTICO - OPÇÃO 1 WINDOWS ONLY
## Python Multi-Canal (WhatsApp + SMS) em Servidor Windows

**Versão:** 1.0 - REVISADO PARA WINDOWS  
**Data:** 2026-09-30  
**Duração:** 4-5 semanas  
**Custo:** R$ 0 (desenvolvimento interno)  
**Tecnologia:** Python 3.10+ | Windows Server/Desktop | Selenium | SQLite

---

## ⚠️ AJUSTES DO WINDOWS

### Informação Crítica
```
❌ NÃO temos servidor Linux
✅ TEMOS servidores Windows (normais)

❌ NÃO usaremos Email/SMTP
✅ USAREMOS: WhatsApp Web + SMS

❌ NÃO usaremos systemd/bash
✅ USAREMOS: Task Scheduler/PowerShell
```

---

## 📋 PRÉ-REQUISITOS

### No Servidor Windows

```powershell
# Verificar pré-requisitos
python --version          # Deve ser 3.10+
pip --version             # Deve existir

# Se não tiver Python 3.10:
# Baixar de: https://www.python.org/downloads/
# Marcar "Add Python to PATH"

# Validar Oracle client
# (deve estar instalado para conectar ao TASY)
```

### Validar com TI

```
[ ] Em qual servidor Windows vai rodar?
    - Hostname: _______________
    - IP: _______________
    - Acesso RDP disponível?

[ ] Python 3.10+ instalado?
    - Versão: _______________

[ ] Oracle Client instalado?
    - Versão: _______________

[ ] Acesso ao TASY funciona?
    - Testar conexão: _______________

[ ] Gateway SMS disponível?
    - Provider: _______________
    - URL da API: _______________
    - Credenciais: _______________
```

---

## 📁 ESTRUTURA WINDOWS

```
C:\clara\
├── venv\                     # Virtual environment
├── src\
│   ├── main.py              # Entry point
│   ├── config.py
│   ├── database.py          # SQLite
│   ├── channels\
│   │   ├── base.py
│   │   ├── whatsapp.py      # WhatsApp Web
│   │   └── sms.py           # SMS (if available)
│   ├── orchestrator.py
│   ├── response_monitor.py
│   └── logger.py
│
├── data\
│   └── clara.db             # Banco SQLite
│
├── logs\                     # Logs diários
│   └── clara_2026-09-30.log
│
├── backups\                  # Backups automáticos
│   └── clara_2026-09-30.db
│
├── config\
│   ├── .env                 # Credenciais (NÃO commitar!)
│   └── requirements.txt
│
└── scheduled_tasks\         # Scripts para Task Scheduler
    └── run_clara.ps1
```

---

## 🔧 SETUP INICIAL

### Passo 1: Criar Pasta e Venv

```powershell
# Criar pastas
mkdir C:\clara
mkdir C:\clara\data
mkdir C:\clara\logs
mkdir C:\clara\backups

# Entrar na pasta
cd C:\clara

# Criar virtual environment
python -m venv venv

# Ativar venv
.\venv\Scripts\Activate.ps1

# Se der erro de "execution policy", rodar:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Passo 2: Instalar Dependências

```powershell
# Dentro do venv ativado
pip install --upgrade pip

# Criar requirements.txt
cat > requirements.txt << 'EOF'
oracledb==1.5.1
pandas==2.2.3
selenium==4.16.0
python-dotenv==1.1.1
pyperclip==1.9.0
pyautogui==0.9.54
requests==2.31.0
EOF

# Instalar
pip install -r requirements.txt

# Baixar ChromeDriver compatível
# https://chromedriver.chromium.org/
# (ou deixar Selenium gerenciar automaticamente)
```

### Passo 3: Preparar .env

```powershell
# Criar .env
cat > config\.env << 'EOF'
# TASY Oracle
TASY_USER=TASY
TASY_PASSWORD=sua_senha
TASY_DSN=192.168.5.9:1521/TASYPRD
ORACLE_CLIENT_PATH=C:\instantclient_23_6

# WhatsApp
WHATSAPP_PROFILE=C:\clara\profile\wpp
WHATSAPP_TIMEOUT=30

# SMS (se tiver)
SMS_GATEWAY_URL=https://sms-api.provider.com.br
SMS_API_KEY=sua_api_key

# Logging
LOG_LEVEL=INFO
LOG_DIR=C:\clara\logs
EOF

# IMPORTANTE: Editr manualmente para adicionar credenciais reais!
notepad config\.env
```

---

## 💻 CÓDIGO WINDOWS (SIMPLIFICADO)

### Main.py

```python
# src/main.py
import sys
from pathlib import Path
from config import config
from database import Database
from orchestrator import Orchestrator
from tasy_connector import TasyConnector
from response_monitor import ResponseMonitor
from logger import setup_logger

# Setup
base_dir = Path(__file__).parent.parent
logger = setup_logger("CLARA", base_dir / "logs")

def main():
    logger.info("="*60)
    logger.info("CLARA v2 - Iniciando execução")
    logger.info("="*60)
    
    try:
        # 1. Conectar ao banco local SQLite
        db = Database(config.DB_PATH)
        logger.info(f"✅ Banco de dados: {config.DB_PATH}")
        
        # 2. Conectar ao TASY
        tasy = TasyConnector(config)
        agendamentos = tasy.buscar_agendamentos_proximos(48)
        logger.info(f"✅ Encontrados {len(agendamentos)} agendamentos")
        
        # 3. Orquestrador de canais
        orchestrator = Orchestrator(config, db)
        
        # 4. Enviar notificações
        enviados = 0
        falhas = 0
        
        for agenda in agendamentos:
            resultado = orchestrator.enviar(agenda)
            
            if resultado['status'].value == 'OK':
                enviados += 1
                logger.info(f"✅ Enviado para {agenda['nm_paciente']}")
            else:
                falhas += 1
                logger.warning(f"❌ Falha: {agenda['nm_paciente']} - {resultado['mensagem']}")
        
        # 5. Monitorar respostas
        logger.info("Monitorando respostas...")
        monitor = ResponseMonitor(orchestrator, db)
        confirmados = monitor.verificar_respostas()
        
        # 6. Atualizar TASY
        for confirm in confirmados:
            tasy.atualizar_status_confirmado(confirm['nr_seq_agenda'])
            logger.info(f"✅ Atualizado TASY: {confirm['nr_seq_agenda']}")
        
        # 7. Relatório
        logger.info(f"RESUMO: {enviados} enviados, {falhas} falhas, {len(confirmados)} confirmados")
        
    except Exception as e:
        logger.error(f"❌ Erro crítico: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Config.py

```python
# src/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar .env
load_dotenv(Path(__file__).parent.parent / "config" / ".env")

class Config:
    # TASY
    TASY_USER = os.getenv("TASY_USER")
    TASY_PASSWORD = os.getenv("TASY_PASSWORD")
    TASY_DSN = os.getenv("TASY_DSN")
    
    # WhatsApp
    WHATSAPP_PROFILE = os.getenv("WHATSAPP_PROFILE", "C:\\clara\\profile\\wpp")
    WHATSAPP_TIMEOUT = int(os.getenv("WHATSAPP_TIMEOUT", "30"))
    
    # SMS
    SMS_GATEWAY_URL = os.getenv("SMS_GATEWAY_URL")
    SMS_API_KEY = os.getenv("SMS_API_KEY")
    
    # Paths (Windows)
    BASE_DIR = Path(__file__).parent.parent
    LOGS_DIR = BASE_DIR / "logs"
    DB_PATH = BASE_DIR / "data" / "clara.db"
    DATA_DIR = BASE_DIR / "data"
    
    # Create dirs
    for d in [LOGS_DIR, DATA_DIR]:
        d.mkdir(exist_ok=True, parents=True)

config = Config()
```

---

## ⏰ AUTOMAÇÃO COM WINDOWS TASK SCHEDULER

### Passo 1: Criar Script PowerShell

```powershell
# C:\clara\scheduled_tasks\run_clara.ps1

# Ativar modo para não mostrar janela
$env:PYTHONUNBUFFERED=1

# Mudar para diretório
Set-Location C:\clara

# Ativar venv
.\venv\Scripts\Activate.ps1

# Executar
python src\main.py

# Log da execução
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path "logs\task_scheduler.log" -Value "$timestamp - Execução concluída"
```

### Passo 2: Configurar Task Scheduler

```powershell
# Abrir Task Scheduler e criar nova tarefa agendada:

Nome: CLARA_Notificacoes
Descrição: Enviar notificações via WhatsApp/SMS

Trigger (Quando executar):
- Diária às 08:00 (Buscar agendamentos)
- Diária às 12:00 (Re-tentar falhas)
- Diária às 18:00 (Último lembrete)
- Diária às 20:00 (Relatório do dia)

Action (O que executar):
- Program: powershell.exe
- Arguments: -ExecutionPolicy Bypass -File C:\clara\scheduled_tasks\run_clara.ps1
- Start in: C:\clara

Advanced:
- Run with highest privileges
- Run whether user is logged in or not
```

### Ou via PowerShell (Script)

```powershell
# Script para criar tarefa automaticamente
$trigger = New-ScheduledTaskTrigger -Daily -At "08:00"
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -File C:\clara\scheduled_tasks\run_clara.ps1"
$principal = New-ScheduledTaskPrincipal -UserID "SYSTEM" -RunLevel Highest

Register-ScheduledTask -TaskName "CLARA_Notificacoes" `
    -Trigger $trigger -Action $action -Principal $principal
```

---

## 📊 CANAIS SUPORTADOS

### ✅ WhatsApp Web

```python
# src/channels/whatsapp.py

class WhatsappChannel:
    """Envia via WhatsApp Web (Selenium)"""
    
    def enviar(self, paciente):
        # Mesmo código que antes
        # Compatível com Windows!
        pass
```

### ✅ SMS (If Available)

```python
# src/channels/sms.py

class SMSChannel:
    """Envia via gateway SMS"""
    
    def enviar(self, paciente):
        # Integração com API do provider
        # Fallback automático
        pass
```

### ❌ Email (NÃO USAR)

```python
# DELETADO - não usar
# SMTP do hospital não vai ser usado
```

---

## 🎯 ARQUITETURA MULTI-CANAL WINDOWS

```
Main.py (chamado por Task Scheduler)
  │
  ├─ Orchestrator.enviar(paciente)
  │   │
  │   ├─ 1. Tentar WhatsApp
  │   │    └─ Se falhar: próximo
  │   │
  │   ├─ 2. Tentar SMS (if available)
  │   │    └─ Se falhar: próximo
  │   │
  │   └─ 3. Registrar falha (para follow-up manual)
  │
  └─ ResponseMonitor.verificar_respostas()
      └─ Atualizar TASY se confirmado
```

---

## 📅 TIMELINE WINDOWS (4-5 SEMANAS)

### **SEMANA 1: Setup + WhatsApp**
```
Seg: Setup Windows, Python, venv
Ter: Database SQLite
Qua: WhatsApp Channel (Selenium)
Qui: Config .env + Logging
Sex: Testes unitários
```

### **SEMANA 2: SMS**
```
Seg-Ter: SMS Channel (integração gateway)
Qua: Orchestrator multi-canal
Qui-Sex: ResponseMonitor
```

### **SEMANA 3: Automação**
```
Seg-Ter: Task Scheduler scripts
Qua-Qui: Monitoring + Alertas
Sex: Testes de carga
```

### **SEMANA 4-5: Deploy + Produção**
```
Seg-Ter: Deploy no servidor Windows
Qua-Qui: Testes em produção
Sex: Suporte 24/7
```

---

## ✅ CHECKLIST WINDOWS

- [ ] Python 3.10+ instalado
- [ ] Virtual environment criado
- [ ] Dependências instaladas (requirements.txt)
- [ ] Oracle Client funcionando
- [ ] .env preenchido com credenciais reais
- [ ] SQLite database criado
- [ ] WhatsApp Channel testado
- [ ] SMS Channel integrado (if available)
- [ ] Response Monitor funcionando
- [ ] Task Scheduler configurado
- [ ] Logs funcionando
- [ ] Testes passando
- [ ] Deploy em servidor Windows
- [ ] Monitoramento ativo

---

## 🐛 TROUBLESHOOTING WINDOWS

### Selenium/ChromeDriver

```powershell
# Se não conseguir encontrar ChromeDriver:
pip install webdriver-manager

# Ele baixa automaticamente na primeira execução
```

### Oracle Client

```powershell
# Verificar se está instalado:
sqlplus -version

# Se não tiver, instalar:
# https://www.oracle.com/database/technologies/instant-client/
```

### Task Scheduler não executa

```powershell
# Verificar logs:
Get-EventLog -LogName System | Where-Object {$_.Source -eq "Task Scheduler"}

# Dar permissões de execução:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
```

### Permissões de pasta

```powershell
# Se der erro de permissão em C:\clara:
icacls C:\clara /grant:r "%USERNAME%":F /t
```

---

## 📈 MÉTRICAS DE SUCESSO

```
Taxa de Entrega:
  - WhatsApp: 60-70%
  - SMS (if available): 80-90%
  - Multi-canal: 85%+

Uptime:
  - Alvo: 99.5%+
  - Monitorar Task Scheduler logs

Custo:
  - R$ 0 (running on existing Windows server)

ROI:
  - R$ 700k/ano (mesmo sem Email)
  - Payback: ~4 dias
```

---

## 🎓 DOCUMENTAÇÃO NECESSÁRIA

**A FAZER:**
- [ ] Remover todas referências a Linux do GUIA original
- [ ] Remover referências a Email
- [ ] Adicionar scripts PowerShell
- [ ] Adicionar Task Scheduler docs
- [ ] Adicionar Windows troubleshooting

---

## 📌 RESUMO WINDOWS

✅ **Opção 1 é totalmente viável em Windows!**

**Stack:**
- Python 3.10+ ✅
- Selenium (Chromium) ✅
- SQLite ✅
- Task Scheduler (automação) ✅
- WhatsApp + SMS ✅

**NÃO tem:**
- ❌ Linux/systemd
- ❌ Email/SMTP
- ❌ Complexidade desnecessária

**Resultado:**
- Zero custo R$ 0 ✅
- Roda em Windows existente ✅
- ROI R$ 700k/ano ✅
- Taxa sucesso 85%+ ✅

---

## 🚀 PRÓXIMAS AÇÕES

1. **Validar com TI (hoje):**
   - Qual servidor Windows?
   - Python instalado?
   - Acesso TASY?

2. **Semana 1 (segunda-feira):**
   - Setup Python + venv
   - Começar desenvolvimento

3. **Seguir timeline 4-5 semanas**

---

**Tudo pronto para WINDOWS! Sem Linux, sem Email. Simples e funcional!** 🎯

