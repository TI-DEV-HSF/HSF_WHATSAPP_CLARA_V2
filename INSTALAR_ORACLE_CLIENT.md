# 📦 Como Instalar Oracle Instant Client para CLARA

## Problema
O TASY usa autenticação com verificação tipo `0x939`, que requer **Oracle Instant Client** em Thick Mode. Sem ele, `oracledb` não consegue conectar.

## Solução

### Opção 1: Download Direto (Recomendado)

1. **Acessar Oracle**
   - Ir para: https://www.oracle.com/database/technologies/instant-client/downloads.html
   - Selecionar: **Microsoft Windows (x64)**
   - Fazer download de: **instantclient-basic-windows.x64-21.13.0.0.0dbru.zip** (ou versão 19)

2. **Descompactar**
   - Extrair o ZIP em: `C:\instantclient_21_13`
   - Verificar que existe: `C:\instantclient_21_13\oci.dll`

3. **Testar**
   - Abrir PowerShell em `C:\Projetos\HSF\HSF_WHATSAPP_CLARA_V2`
   - Rodar: `.\venv\Scripts\python.exe src\tasy_connector.py`
   - Deve funcionar agora!

### Opção 2: Procurar em Outro Projeto HSF

Se outro projeto (ex: AGILIS, SISTEMA_AGILIS) já tem Oracle Client instalado:

```powershell
# Procurar por oci.dll em todo o sistema
dir C:\ -recurse -name "oci.dll" -ErrorAction SilentlyContinue

# Se encontrar em algum lugar como "C:\oracle\product\19.0.0\client_1\bin"
# O tasy_connector.py vai detectar automaticamente!
```

### Opção 3: Usar Variável de Ambiente PATH

Se o Oracle Client está em um local customizado:

1. Adicionar em `.env`:
   ```
   ORACLE_CLIENT_PATH=C:\caminho\do\oracle\instantclient
   ```

2. Modificar `tasy_connector.py` linha 31:
   ```python
   oracledb.init_oracle_client(lib_dir=os.getenv('ORACLE_CLIENT_PATH', caminho))
   ```

---

## Versões Suportadas
- ✅ Oracle Instant Client 19.x
- ✅ Oracle Instant Client 21.x
- ✅ Oracle Instant Client 23.x

**Importante:** Usar versão de **64-bit** (windows.x64)

---

## Após Instalar

1. **Testar Conexão**
   ```powershell
   cd C:\Projetos\HSF\HSF_WHATSAPP_CLARA_V2
   .\venv\Scripts\Activate.ps1
   python src\tasy_connector.py
   ```

2. **Deve mostrar**
   ```
   ✅ Oracle Client carregado em Thick Mode: C:\instantclient_21_13
   🔗 Conectando ao TASY: 192.168.5.9:1521/TASYPRD...
   ✅ Conectado ao TASY com sucesso!
   ```

---

## Links Úteis
- Oracle Instant Client: https://www.oracle.com/database/technologies/instant-client/
- Python oracledb Docs: https://python-oracledb.readthedocs.io/
- Troubleshooting: https://python-oracledb.readthedocs.io/en/latest/user_guide/troubleshooting.html#dpy-3015
