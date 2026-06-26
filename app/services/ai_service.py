from google import genai
from google.genai import types
from sqlalchemy.orm import Session
from app.models import Transaction
from app.config import settings
import json
from datetime import date

class AIService:
    def __init__(self, db: Session):
        self.db = db
        # Inicializa o cliente oficial da Google usando a nova biblioteca google-genai
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def interpretar_gasto_texto(self, texto_usuario: str, contas_usuario: list) -> dict:
        """
        Recebe uma frase em linguagem natural, analisa e extrai os dados estruturados
        da transação financeira combinando com as contas reais do banco.
        """
        # Mapeia as contas reais do usuário para que o Gemini saiba os IDs disponíveis
        mapeamento_contas = [
            {"id": str(c.id), "nome_conta": c.name, "tipo": c.type} 
            for c in contas_usuario
        ]

        # Engenharia de Prompt Estrita para estruturação de dados
        system_instruction = (
            "Você é um interpretador de dados financeiros avançado e intolerante a erros. "
            "Seu objetivo é extrair dados estruturados de uma frase contendo um gasto ou receita.\n\n"
            "Regras de Ouro:\n"
            "1. Identifique o valor total absoluto (sempre positivo no JSON).\n"
            "2. Se o usuário disser que parcelou (ex: 'em 12x', '10 vezes'), extraia o número de parcelas. Se for à vista, o padrão é 1.\n"
            "3. Deduza a categoria mais adequada entre: ['Geral', 'Alimentação', 'Transporte', 'Lazer', 'Eletrônicos', 'Saúde'].\n"
            "4. Com base nas contas reais fornecidas, associe ao ID da conta que mais se aproxima do que o usuário digitou. "
            "Se ele não citar nenhuma conta ou banco, use o ID da primeira conta da lista por padrão.\n\n"
            "Você deve responder OBRIGATORIAMENTE no formato JSON abaixo, sem textos extras ou Markdown:\n"
            "{\n"
            "  \"description\": \"Nome limpo do estabelecimento ou product\",\n"
            "  \"total_amount\": 150.00,\n"
            "  \"total_installments\": 1,\n"
            "  \"account_id\": \"uuid-da-conta-escolhida\",\n"
            "  \"category\": \"Alimentação\",\n"
            "  \"is_recurring\": false\n"
            "}"
        )

        prompt = f"Contas disponíveis: {json.dumps(mapeamento_contas)}\nFrase do usuário: '{texto_usuario}'"

        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.1
            ),
        )

        try:
            return json.loads(response.text)
        except Exception:
            return {
                "description": texto_usuario,
                "total_amount": 0.0,
                "total_installments": 1,
                "account_id": mapeamento_contas[0]["id"] if mapeamento_contas else "",
                "category": "Geral",
                "is_recurring": False
            }

    async def gerar_insights_preditivos(self, user_id) -> dict:
        """
        Analisa as parcelas futuras salvas no banco e gera relatórios automáticos.
        """
        hoje = date.today()
        transacoes_futuras = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.due_date >= hoje
        ).all()

        dados_higienizados = [
            {
                "descricao": t.description,
                "valor": t.amount,
                "vencimento": t.due_date.isoformat(),
                "categoria": t.category,
                "numero_parcela": t.installment_number
            } for t in transacoes_futuras
        ]

        system_instruction = (
            "Você é um Diretor Financeiro (CFO) de bolso pessoal e analista de dados especialista. "
            "Sua tarefa é analisar o array JSON de despesas futuras e parcelas do usuário e retornar exatamente "
            "três insights preditivos altamente acionáveis.\n\n"
            "Você deve responder OBRIGATORIAMENTE no formato JSON abaixo, não adicione nenhum texto explicativo fora do JSON:\n"
            "{\n"
            "  \"score_saude\": 85,\n"
            "  \"insights\": [\n"
            "    {\n"
            "      \"titulo\": \"Alerta de Acúmulo\",\n"
            "      \"descricao\": \"Texto detalhado explicando o risco ou oportunidade encontrada nas parcelas.\",\n"
            "      \"impacto\": \"Alto\"\n"
            "    }\n"
            "  ]\n"
            "}"
        )

        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Transações parceladas: {json.dumps(dados_higienizados)}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.2
            ),
        )

        try:
            return json.loads(response.text)
        except Exception:
            return {
                "score_saude": 50,
                "insights": [{"titulo": "Erro de Análise", "descricao": "A IA gerou um formato inválido.", "impacto": "Baixo"}]
            }
