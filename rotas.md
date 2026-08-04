                         Visitante
                             │
                             ▼
                  /form/entrada (Cadastro)
                             │
      ┌──────────────────────┼──────────────────────┐
      │                      │                      │
      ▼                      ▼                      ▼
 Gera código           Salva usuário         Envia e-mail
      │                      │                      │
      └──────────────────────┴──────────────────────┘
                             │
                             ▼
                     Página de confirmação
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
         /loja/{id}   /vip-lounge   /entrada-juquita   /acao-guerrilha   /boas-vindas  /cenografia  /dentro-lojas  /estacionamento  /saida-juquita  /saida-nps
                │            │            │
                └──────┬─────┴─────┬──────┘
                       ▼
               Atualiza pontuação
                       │
                       ▼
          /usuario-pontuacao
                       │
                       ▼
               Consulta de pontos

────────────────────────────────────────────────────────

                    Área Administrativa

/admin/login
      │
      ▼
   /admin
      │
 ┌────┼───────────────┐
 │    │               │
 ▼    ▼               ▼
Nova Loja      Novo Brinde     Resgate