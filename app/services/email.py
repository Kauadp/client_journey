import os
import resend

resend.api_key = os.environ["RESEND_API_KEY"]

def enviar_email_passaporte(nome: str, email: str, id_public: str) -> bool:
    try:
        resend.Emails.send({
            "from": "Exagerado <passaporte@SEUDOMINIO.com>",
            "to": email,
            "subject": "Seu Passaporte Exagerado",
            "html": f"""
                <h2>Prontinho, {nome}!</h2>
                <p>Esse é o seu código do Passaporte Exagerado — guarda ele, você vai
                precisar informar nas lojas e ativações do evento.</p>
                <p style="font-size: 28px; font-weight: bold; letter-spacing: 4px;">
                    {id_public}
                </p>
            """,
        })
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False