
 

from flask import Flask, render_template, request, jsonify
import os
import sqlite3
import openai
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import Document
 
app = Flask(__name__)
app.secret_key = "79b2f5b603efa31bce02c15158c006dc"

# Carregar variáveis de ambiente
load_dotenv()
app = Flask(__name__)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
 
# Inicializar banco de dados
 
def init_db():
    connection = sqlite3.connect("chatbot.db", check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_input TEXT,
        bot_response TEXT
    )
    """
                   
    """
    CREATE TABLE IF NOT EXISTS cadastro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        telefone TEXT NOT NULL,
        senha TEXT NOT NULL
    )
                   
    """               
                   )
    connection.commit()
    return connection
 
db_connection = init_db()
 
def save_interaction(user_input, bot_response):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO interactions (user_input, bot_response) VALUES (?, ?)", (user_input, bot_response))
    db_connection.commit()
 
def get_interactions():
    cursor = db_connection.cursor()
    cursor.execute("SELECT user_input, bot_response FROM interactions ORDER BY id ASC")
    return cursor.fetchall()
 
# Processamento de PDF
 
def read_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        return " ".join([page.extract_text() for page in reader.pages])
    except Exception as e:
        print(f"Erro ao ler o PDF: {e}")
        return ""
 
def split_text(text, max_tokens=1000):
    paragraphs = text.split("\n")
    chunks, current_chunk = [], ""
    for paragraph in paragraphs:
        if len(current_chunk + paragraph) > max_tokens:
            chunks.append(current_chunk)
            current_chunk = paragraph
        else:
            current_chunk += "\n" + paragraph
    if current_chunk:
        chunks.append(current_chunk)
    return chunks
 
def generate_response(user_input, previous_context):
    try:
        llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        prompt_template = """VOCÊ É UM PROFESSOR ESPECIALISTA NO ASSUNTO TRATADO NO ARQUIVO ANEXADO, INDEPENDENTE DE QUAL FOR O ASSUNTO. VOCÊ DEVE ENSINAR O USUÁRIO ATÉ QUE O MESMO SE SINTA UM ESPECIALISTA NO ASSUNTO.
   
        ESTILO E TOM:
        VOCÊ DEVE TER UM TOM AMIGÁVEL E DEVE ENSINAR DA FORMA MAIS CLARA POSSÍVEL PARA QUE SEJA CLARO AO USUÁRIO AQUILO O QUE ELE QUER APRENDER.
   
        REGRAS:
        1° NUNCA FAZER A MESMA PERGUNTA DURANTE OS TESTES;
        2° VOCÊ DEVE INICIAR FAZENDO UM TESTE COM 3 PERGUNTAS(UMA DE CADA VEZ);
            - 1° PERGUNTA: O QUE VOCÊ JÁ SABE SOBRE O ASSUNTO?
            - 2° PERGUNTA: QUAL É A SUA MAIOR DIFICULDADE SOBRE O ASSUNTO?
            - 3° VOCÊ PREFERE APRENDER DE QUE FORMA?
        3° APÓS O USUÁRIO RESPONDER ESSAS 3 PERGUNTAS E VOCÊ ARMAZENA-LAS, PERGUNTE: COMO VOCÊ QUER COMEÇAR?;
        4° VOCÊ FARÁ UMA PERGUNTA POR VEZ. OU SEJA, PARA FAZER A PERGUNTA SEGUINTE O USUÁRIO TERÁ QUE RESPONDER A PERGUNTA ANTERIOR;
        5° VOCÊ DEVE ORIENTAR O USUÁRIO PROGRESSIVAMENTE E NÃO ENTREGAR O CONTEÚDO DE UMA VEZ;
        6° SUA MISSÃO É FAZER COM QUE O USUÁRIO SE TORNE UM ESPECIALISTA NO ASSUNTO.
   
   
        FORMATO:
        O FORMATO DE ENSINO DEVE SER CLARO PARA O USUÁRIO.
        CONVERSA ATUAL:
        {context}
        MENSAGEM DO USUÁRIO:
        {message}"""
        prompt = PromptTemplate(input_variables=["message", "context"], template=prompt_template)
        chain = LLMChain(llm=llm, prompt=prompt)
        return chain.run({"message": user_input, "context": previous_context})
    except Exception as e:
        print(f"Erro ao gerar resposta: {e}")
        return "Desculpe, não consegui processar sua solicitação."
 
@app.route('/')
def home():
    return render_template('index.html')
 
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    interactions = get_interactions()
    previous_context = "\n".join([f"Usuário: {u}\nBot: {b}" for u, b in interactions])
    response = generate_response(user_input, previous_context)
    save_interaction(user_input, response)
    return jsonify({"response": response})
 
@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"message": "Nenhum arquivo enviado."}), 400
   
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "Nome do arquivo inválido."}), 400
   
    pdf_text = read_pdf(file)
    return jsonify({"message": "PDF processado com sucesso.", "content": pdf_text})
 
if __name__ == '__main__':
    app.run(debug=True)