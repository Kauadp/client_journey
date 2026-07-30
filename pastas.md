exagerado-ecossistema/
├── app/
│   ├── main.py                 # instancia o FastAPI, registra as rotas
│   ├── database.py              # conexão com Supabase (client ou psycopg)
│   ├── models.py                 # schemas Pydantic (validação de dados dos forms)
│   ├── routes/
│   │   ├── visitante.py         # rotas do passaporte (entrada, hub, lounge)
│   │   └── loja.py               # rotas de pontuação por loja
│   ├── services/
│   │   ├── pontuacao.py          # lógica de cálculo de pontos/multiplicadores
│   │   ├── public_code.py        # geração do código único
│   │   └── email.py              # disparo de e-mail + QR
│   └── templates/
│       ├── base.html             # layout base (Bootstrap CDN, header/footer)
│       ├── entrada.html
│       ├── hub_juquita.html
│       └── loja.html
├── static/                       # se precisar de algum CSS/imagem próprios depois
├── sql/
│   └── schema.sql                 # script de criação das tabelas no Supabase
├── requirements.txt
└── .env                            # credenciais do Supabase (nunca commitar)