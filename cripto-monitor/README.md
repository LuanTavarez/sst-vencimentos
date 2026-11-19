# Monitor Cripto (Binance + Telegram)

Agente que roda **no seu computador**, fora do Claude. Ele lê a sua conta Binance em modo **somente leitura**, aplica as regras do plano (`config.json`) e manda relatórios e alertas para o seu **Telegram** no celular.

- **Somente leitura:** o código só faz requisições GET. Não cria ordens, não cancela ordens e não faz saques.
- **Sem dependências:** precisa só do Python 3.10 ou mais novo. Não é preciso instalar pacotes.
- **Sem segredos no código:** as chaves ficam no arquivo `.env`, que o Git ignora.

## O que ele faz

| Comando | O que faz |
|---|---|
| `python -m monitor relatorio` | Relatório completo, explicado abaixo |
| `python -m monitor watch` | Fica ligado e checa a cada 5 min. Manda alerta na hora quando o BTC chega perto ou toca 60k/58k/52k/46k/40k, volta acima da MM200s ou de 80k, cai mais de 8% em 24h, ou quando uma altcoin chega a menos de 10% do seu preço médio. O mesmo alerta não se repete por 12h |
| `python -m monitor watch --uma-vez` | Faz uma única checagem de alertas. Use no agendador do Windows |
| `python -m monitor teste-telegram` | Manda uma mensagem de teste |

O relatório completo traz:
- o sinal do plano (**MANTER PLANO / ATENÇÃO / AÇÃO**);
- o BTC com a MM200s calculada pelos dados da própria Binance, o fechamento semanal, a queda desde o topo e o RSI semanal;
- a carteira (Spot e Earn Flexível) em US$ e R$, com o resultado de cada moeda contra o seu preço médio;
- as ordens de compra de BTC abertas e quais níveis do plano estão sem ordem;
- o ETH/BTC;
- o radar de altcoins: as 40 maiores em volume, com força contra o BTC em 28 dias, acima da EMA 50 e com o RSI. Memecoins ficam de fora, e só vira **CANDIDATA** com o BTC acima da MM200s.

## Instalação (Windows, cerca de 15 minutos)

1. **Instale o Python** pelo site python.org. Na instalação, marque **"Add Python to PATH"**.
2. **Baixe esta pasta** `cripto-monitor`. No GitHub: Code → Download ZIP, depois extraia.
3. **Crie a chave da Binance (somente leitura):**
   - Binance → Perfil → **Gerenciamento de API** → Criar API.
   - Marque **apenas "Habilitar leitura"**. **Não** marque trading nem saques.
   - Em "Restringir acesso a IPs confiáveis", coloque o IP do seu computador (pesquise "qual meu ip" no Google).
4. **Crie o bot do Telegram:**
   - No Telegram, fale com **@BotFather**, mande `/newbot` e copie o **token**.
   - Mande "oi" para o seu bot novo.
   - Abra `https://api.telegram.org/bot<TOKEN>/getUpdates` e copie o número em `"chat":{"id": ...}`.
5. **Configure:** copie `env.exemplo` para um arquivo chamado `.env` e preencha as 4 linhas.
6. **Teste:** abra o Prompt de Comando dentro da pasta e rode:
   ```
   python -m monitor teste-telegram
   python -m monitor relatorio
   ```
7. **Agende** no Agendador de Tarefas do Windows (Criar Tarefa Básica):
   - Relatório às 08:45 e às 19:45, diariamente:
     - Programa: `python`
     - Argumentos: `-m monitor relatorio`
     - "Iniciar em": a pasta `cripto-monitor`
   - Alertas a cada 15 min:
     - Gatilho diário, repetindo a cada 15 minutos
     - Argumentos: `-m monitor watch --uma-vez`

## Onde rodar

- **No seu computador ou num servidor no Brasil:** funciona.
- **GitHub Actions ou servidores nos EUA:** não funciona. A Binance bloqueia IPs dos EUA (HTTP 451), e o próprio monitor avisa com uma mensagem clara se isso acontecer.
- **Computador desligado:** para alertas 24h, use uma VPS barata no Brasil ou um Raspberry Pi. Nesse caso, rode `python -m monitor watch` com o `nohup` ou como serviço do sistema.

## Ajustar o plano

Tudo fica em `config.json`: os níveis das ordens, suportes e resistências, a confirmação, os alvos de venda, os preços médios e a lista de moedas ignoradas no radar. Depois de cada compra relevante, atualize o seu preço médio.

## Testes

```
python -m unittest discover -s tests -v
```

---
Ferramenta educativa. Não é recomendação de investimento.
