Projeto a 2ª Avaliação da Disciplina de Coding 

Grupo: 

Davi Da Rocha Cardoso - 03367865
Lucas Henrique Do Nascimento De Aquino - 03361343
Paulo Henrique Silva de Freitas - 03368584

# Casa da Sogra Locações (porque ninguém aguenta ficar muito tempo) - Sistema de Gerenciamento de Locadora de Casas de Temporada

##  Descrição e Objetivos
O Casa da Sogra Locações é um sistema de gerenciamento via terminal desenvolvido em Python puro para automatizar o controle de uma locadora de casas de veraneio/temporada. O projeto aplica conceitos de modularização, funções, estruturas de dados em memória (listas e dicionários), validações de regras de negócio e desenvolvimento colaborativo via Git/GitHub.

## Funcionalidades
- Gerenciamento de Clientes (CRUD): Cadastro com validação de CPF único e idade mínima (maioridade), listagem, atualização de dados e exclusão protegida.

- Gerenciamento de Casas (CRUD): Cadastro de imóveis com localização, capacidade máxima de hóspedes, valor da diária e controle de unidades disponíveis; consulta, edição e exclusão.

- Controle de Locações: Aluguel de casas com baixa automática de unidades disponíveis, validação da capacidade máxima de hóspedes e encerramento (checkout) com cálculo de multa por atraso na saída.

- Relatórios Gerenciais: Resumo de clientes, catálogo de casas, unidades disponíveis vs. alugadas, histórico de locações e faturamento total.

## Regras de Negócio Implementadas

1. Unicidade: Não permite cadastrar dois clientes com o mesmo CPF ou duas casas com o mesmo nome.

2. Capacidade Máxima: Bloqueia automaticamente a locação caso a quantidade de hóspedes informada exceda a capacidade máxima da casa.

3. Limite Simultâneo: Cada cliente pode manter no máximo 3 casas alugadas ao mesmo tempo.

4. Desconto Combo: Clientes que já possuem uma locação ativa ganham 15% de desconto ao alugar casas adicionais.

5. Multa por Atraso: No checkout, cada dia de atraso na saída gera multa de R$ 50,00 + o valor de 1 diária da casa.

6. Integridade de Dados: Impede excluir clientes com locações pendentes ou casas que possuam unidades alugadas no momento.

##  Organização do Código

- `app.py`: Arquivo principal responsável pelo menu e navegação do sistema.
- `dados.py`: Listas em memória (`clientes`, `casas`, `locacoes`) para armazenamento volátil dos dados.
- `clientes.py`: Módulo com funções de CRUD e validações de clientes.
- `casas.py`: Módulo com funções de CRUD do catálogo e unidades disponíveis das casas de temporada.
- `locacoes.py`: Módulo com regras de negócio de aluguel, checkout, multas e relatórios.
