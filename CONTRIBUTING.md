# Guia de Contribuição para o Projeto HSF_WHATSAPP_CLARA

Agradecemos seu interesse em contribuir para o desenvolvimento da **CLARA**! Para garantir um processo colaborativo e eficiente, pedimos que siga as diretrizes abaixo.

## 💬 Como Começar

- **Crie uma Issue:** Antes de iniciar um novo trabalho, por favor, [crie uma issue](https://github.com/seu-usuario/seu-repositorio/issues) para descrever a funcionalidade que você deseja adicionar ou o bug que pretende corrigir. Isso ajuda a alinhar as ideias com os mantenedores do projeto.
- **Faça um Fork e Clone:** Faça um fork do repositório para sua conta pessoal e clone-o para sua máquina local.

## 🌿 Branching

Crie uma nova branch para cada funcionalidade ou correção de bug. Use um nome descritivo que siga um dos padrões abaixo:

- **Funcionalidade:** `feature/nome-da-funcionalidade` (ex: `feature/reagendamento-automatico`)
- **Correção de Bug:** `fix/descricao-do-bug` (ex: `fix/erro-leitura-excel`)
- **Documentação:** `docs/tema-da-documentacao` (ex: `docs/atualiza-readme`)

```bash
# Exemplo para uma nova funcionalidade
git checkout -b feature/nova-funcionalidade
```

## ✍️ Estilo de Código e Convenções

- **Padrão de Código:** O projeto segue o guia de estilo **PEP 8**. Recomendamos o uso de um linter como `flake8` ou `black` para garantir a consistência do código.
- **Nomenclatura:**
  - Funções e variáveis devem usar o padrão `snake_case` (ex: `enviar_mensagem`).
  - Mantenha os nomes claros e descritivos.
- **Logging:** Utilize a função `registrar_log()` para registrar as etapas importantes da execução. Isso é fundamental para a depuração e monitoramento do robô.
  ```python
  registrar_log("Iniciando o processo de envio de mensagens.")
  ```
- **Comentários:** Adicione comentários para explicar partes complexas do código ou a lógica por trás de uma decisão de implementação.

## 📦 Commits

Adote o padrão de [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) para as mensagens de commit. Isso torna o histórico de alterações mais legível e organizado.

**Formato:** `<tipo>(<escopo>): <descrição>`

- **Tipos comuns:**
  - `feat`: Uma nova funcionalidade.
  - `fix`: Uma correção de bug.
  - `docs`: Alterações na documentação.
  - `style`: Alterações que não afetam o significado do código (formatação, etc.).
  - `refactor`: Uma alteração de código que não corrige um bug nem adiciona uma funcionalidade.
  - `test`: Adição ou correção de testes.

**Exemplos:**

```
feat(whatsapp): Adiciona tratamento para mensagens de áudio
fix(database): Corrige erro de conexão com o Oracle em modo de espera
docs(readme): Atualiza a seção de instalação
```

## 🚀 Submetendo Alterações

1.  **Faça o commit das suas alterações** com uma mensagem clara e descritiva.
2.  **Envie suas alterações** para o seu fork:
    ```bash
    git push origin feature/nova-funcionalidade
    ```
3.  **Abra um Pull Request (PR)** no repositório principal. No PR, descreva as alterações que você fez e vincule a issue correspondente.

Agradecemos novamente por sua contribuição!
