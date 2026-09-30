# 🚀 GUIA COMPLETO - IMPLEMENTAR CLARA COM N8N
## Da Automação Manual à Orquestração Inteligente

**Recomendação:** Use N8n para modernizar o sistema CLARA mantendo 100% da funcionalidade + melhorias

---

## ❓ POR QUE N8N?

### Comparação: Python RPA vs N8n

| Aspecto | Python RPA (Atual) | N8n (Recomendado) |
|--------|------------------|------------------|
| **Desenvolvimento** | Código manual | Visual/Low-code |
| **Manutenção** | Desenvolvedor necessário | Analista de negócios |
| **Escalabilidade** | Sequencial (lento) | Paralela (rápido) |
| **Confiabilidade** | Manual (reativo) | Automática com retry |
| **Monitoramento** | Arquivo log.txt | Dashboard em tempo real |
| **Integrações** | Código custom | 400+ conectores nativos |
| **WhatsApp** | Web RPA (risco) | WhatsApp Business API (oficila!) |
| **Agendamento** | Cron externo | Integrado |
| **Versionamento** | Git manual | Automático |
| **Backup** | Manual | Cloud automático |
| **Custo anual** | ~$0 (dev time ~120h/ano) | ~$1,500-3,000 |
| **ROI** | Médio | Alto (economia de tempo) |

**Conclusão:** N8n economiza ~$15k/ano em desenvolvimento + aumenta confiabilidade

---

## 🏗️ ARQUITETURA N8N PARA CLARA

### Workflow Principal

```
┌──────────────────────────────────────────────────────────────────────┐
│                    N8N WORKFLOW: "CLARA Lembretes"                   │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  [START]                                                            │
│    │                                                               │
│    ├─────────────────────────────────────────────────────────────┤
│    │ ⏰ TRIGGER: Executar a cada 4 horas (configurável)         │
│    │   ou manualmente via webhook                              │
│    └──────────────────────┬──────────────────────────────────────┘
│                           │
│    ┌──────────────────────▼──────────────────────┐
│    │ 1. CONECTAR ORACLE                         │
│    │    - Ler credenciais do .env                │
│    │    - Executar QUERY_AGENDAMENTOS_72H        │
│    │    - Resultado: 0-100 agendamentos          │
│    └──────────────────────┬──────────────────────┘
│                           │
│    ┌──────────────────────▼──────────────────────┐
│    │ 2. TRANSFORMAR DADOS                       │
│    │    - Normalizar campos (trim, upper, etc)  │
│    │    - Calcular data formatada               │
│    │    - Extrair primeiro nome do paciente     │
│    │    - Remover duplicatas (NR_SEQ + TELE)   │
│    └──────────────────────┬──────────────────────┘
│                           │
│    ┌──────────────────────▼──────────────────────┐
│    │ 3. VALIDAR TELEFONE                        │
│    │    - Usar função JavaScript do validator   │
│    │    - Filter: Apenas celulares válidos      │
│    │    - Log: Invalidades c/ motivo            │
│    └──────────────────────┬──────────────────────┘
│                           │
│    ┌──────────────────────▼──────────────────────┐
│    │ 4. SPLIT: Para cada paciente...             │
│    │                                             │
│    │    ┌───────────────────────────────────┐   │
│    │    │ a) Enviar via WhatsApp            │   │
│    │    │    - Conectar WhatsApp Business   │   │
│    │    │    - Template: "Lembrete Agendamento" │
│    │    │    - Variáveis: Paciente/Data/Medico │
│    │    │    - Webhook: Rastrear entrega    │   │
│    │    │    - Log: timestamp + status      │   │
│    │    └───────────────────────────────────┘   │
│    │                                             │
│    │    ┌───────────────────────────────────┐   │
│    │    │ b) Aguardar 5 minutos             │   │
│    │    │    - Sleep: 5min                   │   │
│    │    └───────────────────────────────────┘   │
│    │                                             │
│    │    ┌───────────────────────────────────┐   │
│    │    │ c) Verificar Resposta             │   │
│    │    │    - Ler mensagens não lidas      │   │
│    │    │    - Se contém "1" ou "sim"      │   │
│    │    │    - Flag: respondeu = true       │   │
│    │    │    - Else: respondeu = false      │   │
│    │    └───────────────────────────────────┘   │
│    │                                             │
│    │    ┌───────────────────────────────────┐   │
│    │    │ d) Se confirmou (respondeu=true)  │   │
│    │    │    - UPDATE TASY status = 'N'    │   │
│    │    │    - Log: "Confirmado!"           │   │
│    │    │    - Enviar mensagem agradecimento│   │
│    │    │ Else                              │   │
│    │    │    - Enviar lembrete alternatiwvo │   │
│    │    │    - Agendar retry em +2h         │   │
│    │    └───────────────────────────────────┘   │
│    │                                             │
│    │    ┌───────────────────────────────────┐   │
│    │    │ e) Registrar no Google Sheets     │   │
│    │    │    (auditoria)                     │   │
│    │    └───────────────────────────────────┘   │
│    │                                             │
│    └──────────────────────┬──────────────────────┘
│                           │
│    ┌──────────────────────▼──────────────────────┐
│    │ 5. RESUMO & NOTIFICAÇÕES                   │
│    │    - Contar: Enviados / Confirmados / Falhas│
│    │    - Enviar Slack: Relatório executivo     │
│    │    - Email: Alert se > 5 falhas            │
│    │    - Google Sheets: Dashboard atualizado   │
│    └──────────────────────┬──────────────────────┘
│                           │
│    ┌──────────────────────▼──────────────────────┐
│    │ [END] Executar novamente em 4 horas        │
│    └──────────────────────────────────────────────┘
│                                                  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 📋 PASSO A PASSO: IMPLEMENTAR EM N8N

### **FASE 1: Setup (1-2 dias)**

#### 1.1 Provisionar N8n

**Opção A: N8n Cloud (Recomendado para começar)**
```bash
1. Ir em: https://n8n.io/
2. Sign up (usar email corporativo HSF)
3. Criar projeto: "CLARA"
4. Plano: "Pro" ($25/mês) ou "Starter" ($12/mês)
5. Ativar suporte a webhooks
```

**Opção B: N8n Self-Hosted (Para produção)**
```bash
# Instalar Docker
docker run -d \
  -p 5678:5678 \
  -e DB_TYPE=postgres \
  -e DB_HOST=seu_postgres \
  -e DB_NAME=n8n \
  --name n8n \
  n8nio/n8n

# Acessar em: http://localhost:5678
```

#### 1.2 Conectar Banco de Dados Oracle

No N8n:
1. **Credentials** → **Create New**
2. **Type:** Oracle Database
3. Preencher:
   ```
   Host: 192.168.5.9
   Port: 1521
   Database: TASYPRD
   User: TASY
   Password: [do .env]
   ```
4. **Test connection** → ✅ Success
5. **Save**

#### 1.3 Conectar WhatsApp Business API

1. **Credentials** → **Create New**
2. **Type:** WhatsApp Business
3. Obter token em: https://developers.facebook.com/
   ```
   Workspace ID: [sua conta Meta]
   Phone Number ID: [seu número verificado]
   API Token: [seu token]
   ```
4. **Test** → ✅ Success
5. **Save**

#### 1.4 Conectar Google Sheets (para auditoria)

1. **Credentials** → **Create New**
2. **Type:** Google Sheets
3. **Authenticate** com conta Google corporativa
4. Criar planilha "CLARA_Auditoria" com colunas:
   ```
   Data | Hora | Paciente | Telefone | Status | Motivo
   ```

---

### **FASE 2: Criar Workflow (3-5 dias)**

#### 2.1 Node 1: Timer (Trigger)

```
Configuração:
- Type: "Interval"
- Interval: 4 (horas)
- Timezone: America/Sao_Paulo

Output esperado:
{
  "execution_timestamp": "2024-01-15T10:00:00Z"
}
```

#### 2.2 Node 2: Query Oracle

```
Type: Oracle Database

SQL Query:
-- Usar a query melhorada do passo anterior
SELECT ... FROM AGENDA_CONSULTA_V WHERE ...

Configuração:
- Timeout: 30 segundos
- Tratamento de erro: Continue
```

Output: Array de 0-100 agendamentos

#### 2.3 Node 3: Transform Data

```javascript
// JavaScript Node (processar cada linha)

return {
  nr_seq_agenda: $json.NR_SEQ_AGENDA,
  dt_agenda: new Date($json.DT_AGENDA),
  dt_agenda_formatada: formatarData($json.DT_AGENDA),
  nome_paciente: $json.NM_PACIENTE.split(' ')[0], // Primeiro nome
  telefone: $json.TELEFONE,
  especialidade: $json.DS_ESPECIALIDADE,
  medico: $json.NM_MEDICO_RESP,
  cd_agenda: $json.CD_AGENDA,
};

function formatarData(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString('pt-BR') + ' às ' + 
         date.toLocaleTimeString('pt-BR');
}
```

#### 2.4 Node 4: Validar Telefone (Function)

```javascript
// N8n Function Node

const { TelefoneValidator } = require('./validators');

const items = $input.getAll();

items.forEach((item) => {
  const resultado = TelefoneValidator.validar(item.json.telefone);
  
  item.json.telefone_valido = resultado.valido;
  item.json.telefone_normalizado = resultado.numero_normalizado;
  item.json.motivo_invalido = !resultado.valido ? resultado.mensagem : null;
});

return items;
```

#### 2.5 Node 5: Filter (Apenas válidos)

```
Type: "If" (Conditional)

Condição:
- telefone_valido == true

Branches:
- TRUE → Continue
- FALSE → Skip + Log
```

#### 2.6 Node 6: Split (Loop)

```
Type: "Split in Batches"
- Batch size: 1 (processar um de cada vez)
- Timeout: 30 minutos
```

Cada iteração processa um paciente individual

#### 2.7 Node 7a: Enviar WhatsApp

```
Type: WhatsApp Business

Message Type: Template
Template: "lembrete_agendamento"
Phone: {{$json.telefone_normalizado}}

Variables:
- {{nome_paciente}}
- {{dt_agenda_formatada}}
- {{especialidade}}
- {{medico}}

Webhook para tracking:
- On delivery: mark_sent = true
- On failure: retry_count++
```

#### 2.7b: Wait (5 minutos)

```
Type: Wait
Duration: 5 minutes
```

#### 2.7c: Verificar Resposta

```javascript
// HTTP Request Node

GET https://api.whatsapp.com/messages?phone={{telefone}}
Headers:
  Authorization: Bearer {{whatsapp_token}}
  
Extrair:
- messages[0].body
- Check if contains "1" or "sim" or "confirmado"
```

#### 2.7d: Atualizar TASY (Condicional)

```sql
-- Se respondeu com "1":
UPDATE agenda_consulta
SET 
  ie_status_agenda = 'N',
  ds_confirmacao = 'WHATSAPP',
  dt_confirmacao = SYSDATE,
  nm_usuario = 'CLARA'
WHERE nr_sequencia = {{nr_seq_agenda}}
```

Se falhar → Retry 3x com backoff exponencial

#### 2.8 Node 8: Log em Google Sheets

```
Type: Google Sheets

Sheet: CLARA_Auditoria
Operation: Append row

Data:
- Data: {{now}}
- Hora: {{hour}}
- Paciente: {{nome_paciente}}
- Telefone: {{telefone_normalizado}}
- Status: {{respondeu ? "Confirmado" : "Pendente"}}
- Motivo: {{erro_motivo}}
```

#### 2.9 Node 9: Resumo & Notificações

```javascript
// Calcular métricas
const all_items = $input.getAll();
const confirmados = all_items.filter(i => i.respondeu).length;
const erros = all_items.filter(i => i.erro).length;
const pendentes = all_items.length - confirmados - erros;

return {
  total: all_items.length,
  confirmados,
  erros,
  pendentes,
  taxa_sucesso: ((confirmados / all_items.length) * 100).toFixed(1) + '%'
};
```

#### 2.10 Node 10: Notificar via Slack

```
Type: Slack

Channel: #clara-alertas
Message:
📊 RELATÓRIO CLARA - {{now}}
✅ Confirmados: {{confirmados}}
⏳ Pendentes: {{pendentes}}
❌ Erros: {{erros}}
📈 Taxa de Sucesso: {{taxa_sucesso}}

Se erros > 5:
🚨 ALERTA: {{erros}} pacientes com falha!
Revisar: https://n8n.com/executions/{{execution_id}}
```

---

### **FASE 3: Testes (2-3 dias)**

#### 3.1 Teste Unitário de Cada Node

```
1. Timer → Verifica timestamp
2. Oracle → Verifica estrutura de dados retornados
3. Transform → Verifica formatação de datas/nomes
4. Validador → Testa com números válidos/inválidos
5. Filter → Verifica que filtra corretamente
6. WhatsApp → Mock da API, verifica payload
7. Wait → Verifica delay correto
8. Update TASY → Teste com nr_seq fictício
9. Google Sheets → Verifica row foi adicionada
10. Slack → Verifica message foi enviada
```

#### 3.2 Teste End-to-End

```
Cenário 1: Sucesso Completo
- Enviar para 5 pacientes com telefones válidos
- Simular resposta "1" para 3
- Verificar: 3 atualizados em TASY, 2 pendentes em Sheets

Cenário 2: Com Falhas
- 2 pacientes sem telefone
- 1 telefone inválido
- Verificar: 3 logs com motivos em Sheets, 2 Slack alerts

Cenário 3: Timeout
- Desligar banco de dados
- Verifica: Retry 3x, depois skip + log
```

#### 3.3 Teste de Carga

```
- Simular 100 agendamentos
- Processar em paralelo
- Medir tempo total (deve ser < 10 minutos)
```

---

## 🔒 SEGURANÇA EM N8N

### Credenciais Seguras

```
1. Usar Encrypted Credentials (N8n armazena hash)
2. Não expor tokens em logs
3. Usar IP Whitelist se self-hosted
4. Habilitar 2FA na conta N8n
5. Usar API keys ao invés de senhas
6. Rotacionar tokens a cada 90 dias
```

### Backup & Recuperação

```
1. N8n Cloud: Backup automático diário
2. N8n Self-Hosted: 
   - Export workflow como JSON (versionado no Git)
   - Database backup PostgreSQL 1x/semana
   - Snapshots de VM 1x/mês
```

### Conformidade LGPD

```
N8n Features:
✅ Pode deletar dados históricos (retention policy)
✅ Audit logs de quem acessou o quê
✅ Encryption at rest + in transit
✅ Não armazena dados de pacientes (apenas IDs)
```

---

## 📊 DASHBOARD N8N

Criar dashboard com:

```
1. Taxa de Confirmação (%)
   - Hoje
   - Esta semana
   - Este mês
   - Comparação período anterior

2. Tempo Médio de Resposta
   - Em minutos
   - By especialidade

3. Agendamentos por Status
   - Confirmado
   - Pendente
   - Falha
   - Não resposta

4. Pacientes em Risco
   - Não confirmaram após 24h
   - Ação: Re-enviar lembrete

5. Performance
   - Execuções bem-sucedidas
   - Taxa de erro
   - Tempo médio de execução
```

---

## 💰 ORÇAMENTO & TIMELINE

### Custos

```
N8n Cloud (recomendado):
- Plano Pro: $25/mês = $300/ano
- WhatsApp Business API: $0,0439 por mensagem
  → ~500 mensagens/mês = ~$22/mês = $264/ano
- Google Workspace (sheets): Já existe = $0
- TOTAL: ~$564/ano

Desenvolvimento:
- Setup N8n: 2 dias = $1,600
- Criar workflow: 3-4 dias = $2,400
- Testes: 2-3 dias = $1,600
- Treinamento: 1 dia = $800
- TOTAL SETUP: $6,400
```

### Timeline

```
Semana 1: Setup + Configuração (2-3 dias)
Semana 2: Criar workflow + Testes (3-4 dias)
Semana 3: QA + Treinamento (2-3 dias)
Semana 4: Deploy Produção (1 dia)

Total: 4 semanas = ~1 Sprint
```

---

## ✅ CHECKLIST IMPLEMENTAÇÃO N8N

- [ ] Criar conta N8n Cloud
- [ ] Conectar Oracle Database
- [ ] Conectar WhatsApp Business API
- [ ] Conectar Google Sheets
- [ ] Criar Node 1: Timer
- [ ] Criar Node 2: Query Oracle
- [ ] Criar Node 3: Transform Data
- [ ] Criar Node 4: Validar Telefone
- [ ] Criar Node 5: Filter
- [ ] Criar Node 6: Split
- [ ] Criar Node 7: WhatsApp + Wait + Check
- [ ] Criar Node 8: Update TASY
- [ ] Criar Node 9: Google Sheets
- [ ] Criar Node 10: Resumo
- [ ] Criar Node 11: Slack Notification
- [ ] Testar com 5 pacientes reais
- [ ] Testar falhas e retries
- [ ] Testar carga (100 pacientes)
- [ ] Criar alertas Slack
- [ ] Documentar workflow
- [ ] Treinar usuários
- [ ] Deploy em produção
- [ ] Monitorar por 1 semana
- [ ] Otimizações finais

---

## 🎓 TREINAMENTO DE USUÁRIOS

**Quem precisa treinar:**
1. Admin de TI: Manutenção de N8n
2. Gestor de Agendamentos: Usar dashboard
3. Suporte: Entender logs e alertas

**Materiais:**
1. Guia de Troubleshooting
2. Vídeo tutorial 10min
3. Documento de FAQs
4. Contato de suporte

---

## 🚀 PRÓXIMAS MELHORIAS (Futuro)

Após sucesso do MVP:

1. **IA para previsão:**
   - Quem não vai vir (no-show)
   - Enviar SMS adicional 24h antes

2. **Multi-canal:**
   - Fallback para SMS se WhatsApp falhar
   - Email para idosos
   - Ligação automática 2h antes

3. **Analytics Avançado:**
   - Taxa de no-show histórica
   - Correlação: especialidade vs confirmação
   - Previsão de demand por slot

4. **Integração com App:**
   - Paciente confirma no app (push notification)
   - Reagendamento automático se cancelar

---

**Conclusão:** N8n é a solução moderna que o HSF merece.  
Rápida, confiável, escalável e sem necessidade de programmers.

---

**Preparado por:** Análise Sistema CLARA  
**Versão:** 1.0  
**Recomendação:** Implementar N8n como próximo passo
