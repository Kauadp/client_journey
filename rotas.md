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
         /loja/{id}   /vip-lounge   /hub-juquita   /acao-guerrilha   /boas-vindas
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