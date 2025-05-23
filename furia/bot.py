import telebot
import requests
import json
import atexit
import asyncio
import random
import twitchAPI
from twitchAPI.twitch import Twitch
import time
import threading
import sqlite3

# Conectar ao banco de dados (ou criar se não existir)
conn = sqlite3.connect('bot_furia.db')  # Nome do arquivo do banco de dados
cursor = conn.cursor()

# Criar a tabela 'usuarios'
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    user_id INTEGER PRIMARY KEY,  -- ID único do usuário
    idioma TEXT DEFAULT 'pt',     -- Idioma preferido do usuário (padrão: português)
    autorizado INTEGER DEFAULT 0  -- Status de autorização (0 = não autorizado, 1 = autorizado)
)
''')

# Confirmar as alterações e fechar a conexão
conn.commit()
conn.close()

print("Tabela 'usuarios' criada com sucesso!")

conn = sqlite3.connect('bot_furia.db')
cursor = conn.cursor()

# Listar todas as tabelas no banco de dados
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tabelas = cursor.fetchall()

print("Tabelas no banco de dados:", tabelas)

conn.close()

bot = telebot.TeleBot("8080855422:AAEeQc9bJbXElycdJ1hMZxI8RrbeFVrWJMk")

twitch = Twitch("0v1tqtpk3qys3c6u71nwrwp7t7zzvl", "k17uu0ggt74h8vxkeuewlnwi6c0zmd")
twitch.authenticate_app([])
TARGET_CHANNEL = [
    'gafallen',
    'brino',
    'mount',
    'paulanobre',
    'sofiaespanha',
    'xarola_',
    'otsukaxd',
    'mwzera',
    'jxmo',
    'furiatv',
    'fittipaldibrothers',
    'breeze_fps',
    'immadness',
    'gabssf',
    'pokizgames',
    'kscerato',
    'ikee',
    'chelok1ng',
    'qckv',
    'raf1nhafps',
    'crisguedes',
    'yuurih',
    'khalil_fps',
    'vaxlon',
    'daaygamer_',
    'rafaelmoraesgm',
    'yanxnz_',
    'herdszz',
    'havocfps1',
    'ablej',
    'izaa',
    'xeratricky',
    'upluanleal',
    'ivdmaluco',
    'igoorctg',
    'dhinoff',
    'omanelzin_',
    'kaah',
    'guerri',
    'kheyze7',
    'anamariabrogui',
    'maestropierre',
    'afternobelo',
    'zarakicoach',
    'highs',
    'murillomellobr',
    'dezorganizada',
    'livinhazika',
    'kvondoom',
    # Páginas oficiais da Furia para jogos
    'furiagg',
    'furiaggcs',
    'furiagglol',
    'furiaggval',
    'furiagg_r6',
    'furiaf.c'
]

def get_twitch_access_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": "0v1tqtpk3qys3c6u71nwrwp7t7zzvl",
        "client_secret": "k17uu0ggt74h8vxkeuewlnwi6c0zmd",
        "grant_type": "client_credentials"
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    token = response.json()["access_token"]
    print(f"Access Token: {token}")  # Log para depuração
    return token

# Dicionário para armazenar o consentimento dos usuários (substitua por um banco de dados em produção)
usuarios_autorizados = {}

# Salvar autorizações em um arquivo
def salvar_autorizacoes():
    with open("autorizacoes.json", "w") as f:
        json.dump(usuarios_autorizados, f)

# Carregar autorizações do arquivo
def carregar_autorizacoes():
    global usuarios_autorizados
    try:
        with open("autorizacoes.json", "r") as f:
            usuarios_autorizados = json.load(f)
    except FileNotFoundError:
        usuarios_autorizados = {}

# Carregar autorizações ao iniciar o bot
carregar_autorizacoes()

# Salvar autorizações ao encerrar o bot
atexit.register(salvar_autorizacoes)

# Função para enviar notificações
def enviar_notificacao(mensagem):
    conn = sqlite3.connect('bot_furia.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM usuarios WHERE autorizado = 1')
    usuarios_autorizados = [row[0] for row in cursor.fetchall()]
    conn.close()

    for user_id in usuarios_autorizados:
        try:
            bot.send_message(user_id, mensagem)
        except Exception as e:
            print(f"Erro ao enviar mensagem para o usuário {user_id}: {e}")

# Comando para pedir autorização
@bot.message_handler(commands=['autorizar'])
def autorizar(msg: telebot.types.Message):
    user_id = msg.from_user.id
    usuarios_autorizados[user_id] = True  # Armazena o consentimento do usuário
    bot.reply_to(msg, "Você autorizou o recebimento de notificações. Obrigado!")

# Comando para cancelar a autorização
@bot.message_handler(commands=['cancelar'])
def cancelar(msg: telebot.types.Message):
    user_id = msg.from_user.id
    if user_id in usuarios_autorizados:
        del usuarios_autorizados[user_id]  # Remove o consentimento do usuário
        bot.reply_to(msg, "Você cancelou o recebimento de notificações. Não enviaremos mais atualizações.")
    else:
        bot.reply_to(msg, "Você não está autorizado a receber notificações.")

# Variável global para armazenar o idioma dos usuários
idiomas_usuarios = {}  # Armazena o idioma de cada usuário (user_id)

# Função para alternar o idioma para inglês
@bot.message_handler(commands=['english'])
def english(msg: telebot.types.Message):
    user_id = msg.from_user.id
    idiomas_usuarios[user_id] = "en"  # Define o idioma do usuário como inglês
    bot.reply_to(msg, "Language switched to English! You will now receive notifications and responses in English.")
    
    # Mostrar os comandos disponíveis em inglês
    bot.reply_to(msg, "Here are some commands you can use:\n\n"
                      "/help - To get help\n"
                      "/tip - To receive a random tip\n"
                      "/teams - To learn more about Furia's teams\n"
                      "/info - To learn more about me\n"
                      "/influencers - To learn more about Furia's influencers\n"
                      "/links - To get Furia's links\n"
                      "/portugues - To change the language to Portuguese\n"
                      "/notify - To activate live notifications\n"
                      "/cancel - To cancel live notifications\n")

# Função para alternar o idioma para português
@bot.message_handler(commands=['portugues'])
def portugues(msg: telebot.types.Message):
    user_id = msg.from_user.id
    idiomas_usuarios[user_id] = "pt"  # Define o idioma do usuário como português
    bot.reply_to(msg, "Idioma alterado para Português! Agora você receberá notificações e respostas em Português.")
    
    # Mostrar os comandos disponíveis em português
    bot.reply_to(msg, "Aqui estão alguns comandos que você pode usar:\n\n"
                      "/ajuda - Para obter ajuda\n"
                      "/dica - Para receber uma dica aleatória\n"
                      "/equipes - Para saber mais sobre as equipes da Furia\n"
                      "/info - Para saber mais sobre mim\n"
                      "/influencia - Para saber mais sobre os influenciadores da Furia\n"
                      "/links - Para obter links da Furia\n"
                      "/english - Para mudar o idioma para inglês\n"
                      "/notificar - Para ativar notificações de lives\n"
                      "/cancelar - Para cancelar notificações de lives\n")

@bot.message_handler(commands=['links'])
def links(msg: telebot.types.Message):
    user_id = msg.from_user.id
    if idiomas_usuarios.get(user_id, "pt") == "en":
        bot.reply_to(msg, "Here are some important links related to Furia:\n\n"
                          "1. Official Website: [Furia](https://www.furia.gg)\n"
                          "2. Instagram: [Furia Instagram](https://www.instagram.com/furiagg)\n"
                          "3. Twitter: [Furia Twitter](https://x.com/FURIA)\n"
                          "4. YouTube: [Furia YouTube](https://www.youtube.com/@FURIA)\n"
                          "5. Discord: [Furia Discord](https://discord.gg/furia)\n")
    else:
        bot.reply_to(msg, "Aqui estão alguns links importantes relacionados à Furia:\n\n"
                          "1. Site Oficial: [Furia](https://www.furia.gg)\n"
                          "2. Instagram: [Furia Instagram](https://www.instagram.com/furiagg)\n"
                          "3. Twitter: [Furia Twitter](https://x.com/FURIA)\n"
                          "4. YouTube: [Furia YouTube](https://www.youtube.com/@FURIA)\n"
                          "5. Discord: [Furia Discord](https://discord.gg/furia)\n")


# Comando /start atualizado
@bot.message_handler(commands=['start'])
def start(msg: telebot.types.Message):
    user_id = msg.from_user.id
    if idiomas_usuarios.get(user_id, "pt") == "en":
        bot.reply_to(msg, "Hello, I'm BotFuria! How can I help you? Here are some commands you can use:\n\n"
                          "/help - To get help\n"
                          "/tip - To receive a random tip\n"
                          "/teams - To learn more about Furia's teams\n"
                          "/info - To learn more about me\n"
                          "/influencers - To learn more about Furia's influencers\n"
                          "/links - To get Furia's links\n"
                          "/portugues - Para mudar o idioma para português\n"
                          "/notify - To activate live notifications\n"
                          "/cancel - To cancel live notifications\n")

    else:
        bot.reply_to(msg, "Olá, sou o BotFuria! Como posso ajudar? Aqui estão alguns comandos que você pode usar:\n\n"
                          "/ajuda - Para obter ajuda\n"
                          "/dica - Para receber uma dica aleatória\n"
                          "/equipes - Para saber mais sobre as equipes da Furia\n"
                          "/info - Para saber mais sobre mim\n"
                          "/influencia - Para saber mais sobre os influenciadores da Furia\n"
                          "/links - Para obter links da Fúria\n"
                          "/english - To change language\n"
                          "/notificar - Para ativar notificações de lives\n"
                          "/cancelar - Para cancelar notificações de lives\n")

# Comando /ajuda ou /help atualizado
@bot.message_handler(commands=['ajuda', 'help'])
def ajuda(msg: telebot.types.Message):
    user_id = msg.from_user.id
    if idiomas_usuarios.get(user_id, "pt") == "en":
        bot.reply_to(msg, "I'm here to help! Here are some commands you can use:\n\n"
                          "/start - To start a conversation with me\n"
                          "/info - To learn more about me\n"
                          "/tip - To receive a random tip\n"
                          "/teams - To learn more about Furia's teams\n"
                          "/help - To see this help message again")
    else:
        bot.reply_to(msg, "Estou aqui para ajudar! Aqui estão alguns comandos que você pode usar:\n\n"
                          "/start - Para iniciar uma conversa comigo\n"
                          "/info - Para saber mais sobre mim\n"
                          "/dica - Para receber uma dica aleatória\n"
                          "/equipes - Para saber mais sobre as equipes da Furia\n"
                          "/ajuda - Para ver esta mensagem de ajuda novamente")

# Comando /dica ou /tip atualizado
@bot.message_handler(commands=['dica', 'tip'])
def dica(msg: telebot.types.Message):
    user_id = msg.from_user.id
    if idiomas_usuarios.get(user_id, "pt") == "en":
        tips = [
            "Have you bought Furia's Adidas jersey? Check it out on the [website!](https://www.furia.gg)",
            "Furia has an amazing community of fans! Check out our [Instagram](https://www.instagram.com/furiagg)",
            "Furia has participated in several international championships! [Click here to learn more](https://pt.wikipedia.org/wiki/Furia_Esports)",
            "Furia has a team of talented and dedicated players! To learn more, use the /teams command.",
            "Did you know that Furia has a 7-a-side football team? They compete in the Kings League! [Click here](https://youtube.com/@furiaf.c.?si=9P_ZQmZcRGer7z__) to see more content on YouTube.",
            "Furia also hosts events and tournaments for fans! Check out our [Twitter](https://x.com/FURIA) or [Instagram](https://www.instagram.com/furiagg).",
            "Did you know that Furia has a VALORANT team? They are amazing! Check out their [YouTube channel](https://www.youtube.com/@FURIAggVAL).",
            "Furia is known for its strong presence on social media! Follow us on [Instagram](https://www.instagram.com/furiagg).",
            "Furia has an incredible CS:GO team! They compete in international tournaments and are highly respected in the scene! Check out their [YouTube channel](https://www.youtube.com/@FURIAggCS).",
            "Furia has a League of Legends team that competes in national and international tournaments! Check out their [YouTube channel](https://www.youtube.com/@FURIAggLOL).",
        ]
        bot.reply_to(msg, random.choice(tips), parse_mode='Markdown')
    else:
        dicas = [
            "Já comprou a camiseta da Furia com a Adidas? Dá uma olhada no [site!](https://www.furia.gg)",
            "A Furia tem uma comunidade incrível de fãs! Dá uma olhada no nosso [Instagram](https://www.instagram.com/furiagg)",
            "A Furia já participou de vários campeonatos internacionais! [Clique aqui para saber mais](https://pt.wikipedia.org/wiki/Furia_Esports)",
            "A Furia tem uma equipe de jogadores talentosos e dedicados! Para saber mais, use o comando /equipes.",
            "Você sabia que a Furia tem uma equipe de Futebol de 7? Eles competem na Kings League! [Clique aqui](https://youtube.com/@furiaf.c.?si=9P_ZQmZcRGer7z__) para ver mais no YouTube.",
            "A Furia também realiza eventos e torneios para os fãs! Confira no [Twitter](https://x.com/FURIA) ou no [Instagram](https://www.instagram.com/furiagg).",
            "Você sabia que a Furia tem uma equipe de VALORANT? Eles são incríveis! Confira no [YouTube](https://www.youtube.com/@FURIAggVAL).",
            "A Furia é conhecida por sua presença forte nas redes sociais! Siga-nos no [Instagram](https://www.instagram.com/furiagg).",
            "A Furia tem uma equipe de CS:GO incrível! Confira no [YouTube](https://www.youtube.com/@FURIAggCS).",
            "A Furia tem uma equipe de League of Legends que compete em torneios nacionais e internacionais! Confira no [YouTube](https://www.youtube.com/@FURIAggLOL).",
        ]
        bot.reply_to(msg, random.choice(dicas), parse_mode='Markdown')

# Comando 'equipes' atualizado
@bot.message_handler(commands=['equipes', 'teams'])
def equipes(msg: telebot.types.Message):
    user_id = msg.from_user.id
    if idiomas_usuarios.get(user_id, "pt") == "en":
        bot.reply_to(msg, "Furia's teams are formed by talented and dedicated players.\n")
        bot.reply_to(msg, "Here are some of the teams:\n\n"
                          "1. Furia CS:GO - The Counter-Strike: Global Offensive team.\n"
                          "2. Furia VALORANT - The VALORANT team.\n"
                          "3. Furia League of Legends - The League of Legends team.\n"
                          "4. Furia 7-a-side Football - The 7-a-side football team (Kings League).\n"
                          "5. Furia Rainbow Six - The Rainbow Six Siege team.\n"
                          "For more information about each team, use the command /valorant, /csgo, /lol, /fut7 or /r6\n\n")
    else:
        bot.reply_to(msg, "As equipes da Furia são formadas por jogadores talentosos e dedicados.\n")
        bot.reply_to(msg, "Aqui estão algumas das equipes:\n\n"
                          "1. Furia CS:GO - A equipe de Counter-Strike: Global Offensive.\n"
                          "2. Furia VALORANT - A equipe de VALORANT.\n"
                          "3. Furia League of Legends - A equipe de League of Legends.\n"
                          "4. Furia Futebol de 7 - A equipe de Futebol de 7(Kings League).\n"
                          "5. Furia Rainbow Six - A equipe de Rainbow Six Siege.\n"
                          "Para mais informações sobre cada equipe, use o comando /valorant, /csgo, /lol, /fut7 ou /r6\n\n")

@bot.message_handler(commands=['valorant'])
def valorant(msg: telebot.types.Message):
    user_id = msg.from_user.id
    if idiomas_usuarios.get(user_id, "pt") == "en":
        bot.reply_to(msg, "Did you know that Furia has a VALORANT team? They are amazing!\nCheck out their [YouTube channel](https://www.youtube.com/@FURIAggVAL)\nCheck out their [Twitter](https://x.com/FURIA)\nCheck out their [Instagram](https://www.instagram.com/furia.valorant/?hl=pt-br)\nCheck out their [TikTok](https://www.tiktok.com/@furiagg)\n")
    else:
        bot.reply_to(msg, "Você sabia que Furia tem uma equipe de VALORANT? Eles são incríveis!\nAcesse o canal do [Youtube](https://www.youtube.com/@FURIAggVAL)\nAcesse o [Twitter / X](https://x.com/FURIA)\n Acesse o [Instagram](https://www.instagram.com/furia.valorant/?hl=pt-br) \n Acesse o [TikTok](https://www.tiktok.com/@furiagg) \n")

@bot.message_handler(commands=['csgo'])
def csgo(msg: telebot.types.Message):
    user_id = msg.from_user.id
    if idiomas_usuarios.get(user_id, "pt") == "en":
        bot.reply_to(msg, "Furia has an incredible CS:GO team! They compete in international tournaments and are highly respected in the scene!\nCheck out their [YouTube channel](https://www.youtube.com/@FURIAggCS)\nCheck out their [Twitter](https://x.com/FURIA)\nCheck out their [Instagram](https://www.instagram.com/furiagg)\nCheck out their [TikTok](https://www.tiktok.com/@furiagg)\n")
    else:
        bot.reply_to(msg, "A Furia tem uma equipe de CS:GO incrível! Eles competem em torneios internacionais e são muito respeitados na cena!\n Acesse o canal do [Youtube](https://www.youtube.com/@FURIAggCS)\nAcesse o [Twitter / X](https://x.com/FURIA)\n Acesse o [Instagram](https://www.instagram.com/furiagg) \n Acesse o [TikTok](https://www.tiktok.com/@furiagg) \n")

@bot.message_handler(commands=['lol'])
def lol(msg: telebot.types.Message):
    user_id = msg.from_user.id
    if idiomas_usuarios.get(user_id, "pt") == "en":
        bot.reply_to(msg, "Furia has a League of Legends team that competes in national and international tournaments! They are known for their aggressive and exciting playstyle!\nCheck out their [YouTube channel](https://www.youtube.com/@FURIAggLOL)\nCheck out their [Twitter](https://x.com/FURIA)\nCheck out their [Instagram](https://www.instagram.com/furia.lol/?hl=pt-br)\nCheck out their [TikTok](https://www.tiktok.com/@furiagg)\n")
    else:
        bot.reply_to(msg, "A Furia tem uma equipe de League of Legends que compete em torneios nacionais e internacionais! Eles são conhecidos por seu estilo de jogo agressivo e emocionante!\n Acesse o canal do [Youtube](https://www.youtube.com/@FURIAggLOL)\nAcesse o [Twitter / X](https://x.com/FURIA)\n Acesse o [Instagram](https://www.instagram.com/furia.lol/?hl=pt-br \n Acesse o [TikTok](https://www.tiktok.com/@furiagg) \n")

@bot.message_handler(commands=['fut7'])
def fut7(msg: telebot.types.Message):
    user_id = msg.from_user.id
    if idiomas_usuarios.get(user_id, "pt") == "en":
        bot.reply_to(msg, "Furia has a 7-a-side football team that competes in the Kings League! They are known for their aggressive and exciting playstyle!\nCheck out their [YouTube channel](https://youtube.com/@furiaf.c.?si=9P_ZQmZcRGer7z__)\nCheck out their [Twitter](https://x.com/FURIA)\nCheck out their [Instagram](https://www.instagram.com/furia.football/)\nCheck out their [TikTok](https://www.tiktok.com/@furiagg)\n")
    else:
        bot.reply_to(msg, "A Furia tem uma equipe de Futebol de 7 que compete na Kings League! Eles são conhecidos por seu estilo de jogo agressivo e emocionante!\n Acesse o canal do [Youtube](https://youtube.com/@furiaf.c.?si=9P_ZQmZcRGer7z__)\nAcesse o [Twitter / X](https://x.com/FURIA)\n Acesse o [Instagram](https://www.instagram.com/furia.football/) \n Acesse o [TikTok](https://www.tiktok.com/@furiagg) \n")

@bot.message_handler(commands=['r6'])
def r6(msg: telebot.types.Message):
    user_id = msg.from_user.id
    if idiomas_usuarios.get(user_id, "pt") == "en":
        bot.reply_to(msg, "Furia has a Rainbow Six Siege team that competes in national and international tournaments! They are known for their aggressive and exciting playstyle!\nCheck out their [YouTube channel](https://www.youtube.com/@FURIAggR6)\nCheck out their [Twitter](https://x.com/FURIA)\nCheck out their [Instagram](https://www.instagram.com/furia.r6/?hl=pt-br)\nCheck out their [TikTok](https://www.tiktok.com/@furiagg)\n")
    else:
        bot.reply_to(msg, "A Furia tem uma equipe de Rainbow Six Siege que compete em torneios nacionais e internacionais! Eles são conhecidos por seu estilo de jogo agressivo e emocionante!\n Acesse o canal do [Youtube](https://www.youtube.com/@FURIAggR6)\nAcesse o [Twitter / X](https://x.com/FURIA)\n Acesse o [Instagram](https://www.instagram.com/furia.r6/?hl=pt-br) \n Acesse o [TikTok](https://www.tiktok.com/@furiagg) \n")

@bot.message_handler(func=lambda msg: True)  # Captura todas as mensagens
def comandos_sem_barra(msg: telebot.types.Message):
    texto = msg.text.lower()  # Converte o texto para minúsculas para facilitar a comparação

    # Lista de palavras que acionam o comando 'start'
    palavras_start = ['oi', 'ola', 'olá', 'oii', 'eai', 'salve', 'salveee''salvee', 
                      'boa', 'bomdia', 'boanoite', 'boa tarde', 'bom dia', 
                      'boa noite', 'boatarde', 'tudo bem', 'tudo certo', 'tudobem',
                      'tudocerto', 'tudo certo?', 'tudo bem?', 'oi bot', 'ola bot','opa', 'eai bot',
                      'salve bot', 'salveee bot', 'salvee bot', 'boa bot', 'bomdia bot', 'Opa', 'Oi',
                      'Olá','Oi bot','Oi Bot','Ola bot','Ola Bot','Eai bot','Eai Bot','Salve bot','Salve Bot',
                      'Boa bot','Boa Bot','Bomdia bot','Bomdia Bot','Boanoite bot','Boanoite Bot','Boatarde bot','Boatarde Bot',
                      'Bom dia bot','Bom dia Bot','Boa noite bot','Boa noite Bot','Boa tarde bot','Boa tarde Bot',
                      'Tudo bem bot','Tudo bem Bot','Tudo certo bot','Tudo certo Bot','Tudobem bot','Tudobem Bot',
                      'hi','hello','hey','hi bot','hello bot','hey bot',
                      'hi Bot','hello Bot','hey Bot','Hi bot','Hello bot','Hey bot',
                      'começar','começar','começar bot','começar Bot','Começar bot','Começar Bot',
                      'Começar','Começar Bot','Começar bot','Começar Bot','começar bot','começar Bot',
                      'oii tudo bem?'  'oii tudo certo?','oii tudo bem bot?','oii tudo certo bot?', 'oi tudo bem?', 'oi tudo certo?',
                      'oi tudo bem bot?','oi tudo certo bot?','ola tudo bem?','ola tudo certo?','ola tudo bem bot?','ola tudo certo bot?',
                      'Oii tudo bem?','Oii tudo certo?','Oii tudo bem bot?','Oii tudo certo bot?','Ola tudo bem?','Ola tudo certo?',
                      'Oi tudo bem?','Oi tudo certo?','Oi tudo bem bot?','Oi tudo certo bot?','Ola tudo bem?','Ola tudo certo?',
                        'Ola tudo bem bot?','Ola tudo certo bot?','Eai tudo bem?','Eai tudo certo?','Eai tudo bem bot?','Eai tudo certo bot?',
                        'Eai tudo bem?','Eai tudo certo?','Eai tudo bem bot?','Eai tudo certo bot?','Salve tudo bem?','Salve tudo certo?',
                        'Salve tudo bem bot?','Salve tudo certo bot?','Salveee tudo bem?','Salveee tudo certo?','Salvee tudo bem?',
                        'Salvee tudo certo?','Salveee tudo bem bot?','Salveee tudo certo bot?','Salvee tudo bem bot?','Salvee tudo certo bot?',
                        
                      ]

    if texto in palavras_start:
        start(msg)  # Chama a função do comando /start
    elif texto == "info":
        info(msg)  # Chama a função do comando /info
    elif texto == "dica":
        dica(msg)  # Chama a função do comando /dica
    elif texto == "ajuda":
        ajuda(msg)  # Chama a função do comando /ajuda
    elif texto == "equipes":
        equipes(msg)  # Chama a função do comando /equipes
    elif texto == "valorant":
        valorant(msg)  # Chama a função do comando /valorant
    else:
        bot.reply_to(msg, "Desculpe, não entendi. Tente usar um dos comandos disponíveis ou peça ajuda com 'ajuda'.")

@bot.message_handler(commands=['influencia'])
def influencia(msg: telebot.types.Message):
    bot.reply_to(msg, "A Furia tem uma equipe de influenciadores que criam conteúdo incrível para os fãs!\n\n"
                      "Aqui estão alguns dos influenciadores:\n\n"
                      "1. Gafallen - [Twitch](https://www.twitch.tv/gafallen)\n"
                      "2. Brino - [Twitch](https://www.twitch.tv/brino)\n"
                      "3. Mount - [Twitch](https://www.twitch.tv/mount)\n"
                      "4. Paula Nobre - [Twitch](https://www.twitch.tv/paulanobre)\n"
                      "5. Sofia Espanha - [Twitch](https://www.twitch.tv/sofiaespanha)\n"
                      "6. Xarola_ - [Twitch](https://www.twitch.tv/xarola_)\n"
                      "7. OtsukaXD - [Twitch](https://www.twitch.tv/otsukaxd)\n"
                      "8. Mwzera - [Twitch](https://www.twitch.tv/mwzera)\n"
                      "9. Jxmo - [Twitch](https://www.twitch.tv/jxmo)\n"
                      "10. FURIAtv - [Twitch](https://www.twitch.tv/furiatv)\n"
                      "11. FittipaldiBrothers - [Twitch](https://www.twitch.tv/fittipaldibrothers)\n"
                      "12. Breeze_FPS - [Twitch](https://www.twitch.tv/breeze_fps)\n"
                      "13. ImMadness - [Twitch](https://www.twitch.tv/immadness)\n"
                      "14. Gabssf - [Twitch](https://www.twitch.tv/gabssf)\n"
                      "15. PokizGames - [Twitch](https://www.twitch.tv/pokizgames)\n"
                      "16. Kscerato - [Twitch](https://www.twitch.tv/kscerato)\n"
                      "17. Ikee - [Twitch](https://www.twitch.tv/ikee)\n"
                      "18. Chelok1ng - [Twitch](https://www.twitch.tv/chelok1ng)\n"
                      "19. Qckv - [Twitch](https://www.twitch.tv/qckv)\n"
                      "20. Raf1nhafps - [Twitch](https://www.twitch.tv/raf1nhafps)\n"
                      "21. Crisguedes - [Twitch](https://www.twitch.tv/crisguedes)\n"
                      "22. Yuurih - [Twitch](https://www.twitch.tv/yuurih)\n"
                      "23. Khalil_FPS - [Twitch](https://www.twitch.tv/khalil_fps)\n"
                      "24. Vaxlon - [Twitch](https://www.twitch.tv/vaxlon)\n"
                      "25. Daaygamer_ - [Twitch](https://www.twitch.tv/daaygamer_)\n"
                      "26. RafaelMoraesGM - [Twitch](https://www.twitch.tv/rafaelmoraesgm)\n"
                      "27. Yanxnz_ - [Twitch](https://www.twitch.tv/yanxnz_)\n"
                      "28. Herdszz - [Twitch](https://www.twitch.tv/herdszz)\n"
                      "29. Havocfps1 - [Twitch](https://www.twitch.tv/havocfps1)\n"
                      "30. AbleJ - [Twitch](https://www.twitch.tv/ablej)\n"
                      "31. Izaa - [Twitch](https://www.twitch.tv/izaa)\n"
                      "32. Xeratricky - [Twitch](https://www.twitch.tv/xeratricky)\n"
                      "33. Upluanleal - [Twitch](https://www.twitch.tv/upluanleal)\n"
                      "34. IVDMALUCO - [Twitch](https://www.twitch.tv/ivdmaluco)\n"
                      "35. Igoorctg - [Twitch](https://www.twitch.tv/igoorctg)\n"
                      "36. DhinoFF - [Twitch](https://www.twitch.tv/dhinoff)\n"
                      "37. OManelzin_ - [Twitch](https://www.twitch.tv/omanelzin_)\n"
                      "38. Kaah - [Twitch](https://www.twitch.tv/kaah)\n"
                      "39. Guerri - [Twitch](https://www.twitch.tv/guerri)\n"
                      "40. Kheyze7 - [Twitch](https://www.twitch.tv/kheyze7)\n"
                      "41. AnaMariaBrogui - [Twitch](https://www.twitch.tv/anamariabrogui)\n"
                      "42. MaestroPierre - [Twitch](https://www.twitch.tv/maestropierre)\n"
                      "43. AfterNoBelo - [Twitch](https://www.twitch.tv/afternobelo)\n"
                      "44. ZarakiCoach - [Twitch](https://www.twitch.tv/zarakicoach)\n"
                      "45. Highs - [Twitch](https://www.twitch.tv/highs)\n"
                      "46. MurilloMelloBR - [Twitch](https://www.twitch.tv/murillomellobr)\n"
                      "47. Dezorganizada - [Twitch](https://www.twitch.tv/dezorganizada)\n"
                      "48. Livinhazika - [Twitch](https://www.twitch.tv/livinhazika)\n"
                      "49. Kvondoom - [Twitch](https://www.twitch.tv/kvondoom)\n"                      )
    
# Declaração da variável TARGET_CHANNEL
# Lista de streamers da Furia
    TARGET_CHANNEL = [
    'gafallen',
    'brino',
    'mount',
    'paulanobre',
    'sofiaespanha',
    'xarola_',
    'otsukaxd',
    'mwzera',
    'jxmo',
    'furiatv',
    'fittipaldibrothers',
    'breeze_fps',
    'immadness',
    'gabssf',
    'pokizgames',
    'kscerato',
    'ikee',
    'chelok1ng',
    'qckv',
    'raf1nhafps',
    'crisguedes',
    'yuurih',
    'khalil_fps',
    'vaxlon',
    'daaygamer_',
    'rafaelmoraesgm',
    'yanxnz_',
    'herdszz',
    'havocfps1',
    'ablej',
    'izaa',
    'xeratricky',
    'upluanleal',
    'ivdmaluco',
    'igoorctg',
    'dhinoff',
    'omanelzin_',
    'kaah',
    'guerri',
    'kheyze7',
    'anamariabrogui',
    'maestropierre',
    'afternobelo',
    'zarakicoach',
    'highs',
    'murillomellobr',
    'dezorganizada',
    'livinhazika',
    'kvondoom',
    
]

# Lista de páginas oficiais de jogos
TARGET_CHANNEL = [
    'valorant_br',
    'rainbowsix_br',
    'lol_br',
    'csgo_br',
]

# Função para verificar se os streamers estão ao vivo e filtrar pelo título
def verificar_lives():
    access_token = get_twitch_access_token()
    headers = {
        "Client-ID": "0v1tqtpk3qys3c6u71nwrwp7t7zzvl",
        "Authorization": f"Bearer {access_token}"
    }
    url = "https://api.twitch.tv/helix/streams"

    # Dividir a lista de streamers em lotes de até 100 (limite da API da Twitch)
    streamers_ao_vivo = []
    for i in range(0, len(TARGET_CHANNEL), 100):
        batch = TARGET_CHANNEL[i:i + 100]  # Lote de até 100 streamers
        params = [("user_login", streamer) for streamer in batch]  # Enviar múltiplos valores como lista de tuplas
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Filtrar lives pelo título
        for stream in data["data"]:
            titulo = stream["title"].lower()
            if "furia" in titulo or "fur" in titulo:
                streamers_ao_vivo.append({
                    "user_name": stream["user_name"],
                    "title": stream["title"],
                    "viewer_count": stream["viewer_count"]
                })

    # Retorna uma lista de streamers que estão ao vivo e com títulos relevantes
    return streamers_ao_vivo

@bot.message_handler(commands=['notificar', 'notify'])
def notificar(msg: telebot.types.Message):
    print(f"Comando recebido: {msg.text}")  # Log para depuração
    user_id = msg.from_user.id
    print(f"ID do usuário: {user_id}")  # Log para depuração
    idioma = idiomas_usuarios.get(user_id, "pt")  # Obtém o idioma do usuário (padrão: português)
    
    # Verifica se o usuário já está autorizado
    conn = sqlite3.connect('bot_furia.db')
    cursor = conn.cursor()
    cursor.execute('SELECT autorizado FROM usuarios WHERE user_id = ?', (user_id,))
    resultado = cursor.fetchone()
    
    if resultado is None or resultado[0] == 0:  # Usuário não está autorizado ou não existe
        adicionar_usuario(user_id, idioma=idioma, autorizado=1)
        if idioma == "en":
            bot.reply_to(msg, "You have activated live notifications! We will send updates whenever a Furia-related stream goes live.")
        else:
            bot.reply_to(msg, "Você ativou as notificações de lives! Enviaremos atualizações sempre que uma live relacionada à Furia estiver ao vivo.")
    else:
        if idioma == "en":
            bot.reply_to(msg, "You are already subscribed to receive live notifications!")
        else:
            bot.reply_to(msg, "Você já está inscrito para receber notificações de lives!")
    
    conn.close()

# Função para enviar notificações sobre lives
def enviar_notificacoes_lives():
    while True:
        try:
            streamers_ao_vivo = verificar_lives()
            if streamers_ao_vivo:
                # Obter usuários autorizados do banco de dados
                conn = sqlite3.connect('bot_furia.db')
                cursor = conn.cursor()
                cursor.execute('SELECT user_id, idioma FROM usuarios WHERE autorizado = 1')
                usuarios_autorizados = cursor.fetchall()
                conn.close()
                
                for user_id, idioma in usuarios_autorizados:
                    if idioma == "en":
                        mensagem = "🔴 **Live on Twitch!**\nThe following streams related to Furia are live now:\n\n"
                        mensagem += "\n".join([f"- {stream['user_name']} (Viewers: {stream['viewer_count']})\nTitle: {stream['title']}" for stream in streamers_ao_vivo])
                        mensagem += "\n\nVisit Twitch to watch!"
                    else:
                        mensagem = "🔴 **Live na Twitch!**\nAs seguintes lives relacionadas à Furia estão ao vivo agora:\n\n"
                        mensagem += "\n".join([f"- {stream['user_name']} (Espectadores: {stream['viewer_count']})\nTítulo: {stream['title']}" for stream in streamers_ao_vivo])
                        mensagem += "\n\nAcesse a Twitch para assistir!"
                    
                    try:
                        bot.send_message(user_id, mensagem, parse_mode='Markdown')
                    except Exception as e:
                        print(f"Erro ao enviar mensagem para o usuário {user_id}: {e}")
            
            time.sleep(300)  # Verifica a cada 5 minutos
        except Exception as e:
            print(f"Erro ao verificar lives: {e}")
            time.sleep(300)  # Aguarda 5 minutos antes de tentar novamente

# Inicia a verificação de lives em uma thread separada
threading.Thread(target=enviar_notificacoes_lives, daemon=True).start()

def adicionar_usuario(user_id, idioma='pt', autorizado=1):
    conn = sqlite3.connect('bot_furia.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO usuarios (user_id, idioma, autorizado)
        VALUES (?, ?, ?)
    ''', (user_id, idioma, autorizado))
    conn.commit()
    conn.close()

def listar_usuarios_autorizados():
    conn = sqlite3.connect('bot_furia.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM usuarios WHERE autorizado = 1')
    usuarios = [row[0] for row in cursor.fetchall()]
    conn.close()
    return usuarios

def atualizar_idioma(user_id, idioma):
    conn = sqlite3.connect('bot_furia.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE usuarios SET idioma = ? WHERE user_id = ?', (idioma, user_id))
    conn.commit()
    conn.close()

def remover_usuario(user_id):
    conn = sqlite3.connect('bot_furia.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM usuarios WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def atualizar_autorizacao(user_id, autorizado):
    conn = sqlite3.connect('bot_furia.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE usuarios SET autorizado = ? WHERE user_id = ?', (autorizado, user_id))
    conn.commit()
    conn.close()

@bot.message_handler(commands=['cancelar', 'cancel'])
def cancelar(msg: telebot.types.Message):
    user_id = msg.from_user.id
    idioma = idiomas_usuarios.get(user_id, "pt")  # Obtém o idioma do usuário (padrão: português)
    
    # Verifica se o usuário está autorizado
    conn = sqlite3.connect('bot_furia.db')
    cursor = conn.cursor()
    cursor.execute('SELECT autorizado FROM usuarios WHERE user_id = ?', (user_id,))
    resultado = cursor.fetchone()
    
    if resultado and resultado[0] == 1:  # Usuário está autorizado
        atualizar_autorizacao(user_id, autorizado=0)
        if idioma == "en":
            bot.reply_to(msg, "You have canceled live notifications. We will no longer send updates.")
        else:
            bot.reply_to(msg, "Você cancelou o recebimento de notificações. Não enviaremos mais atualizações.")
    else:
        if idioma == "en":
            bot.reply_to(msg, "You are not subscribed to receive notifications.")
        else:
            bot.reply_to(msg, "Você não está inscrito para receber notificações.")
    
    conn.close()

if __name__ == "__main__":
    streamers_ao_vivo = verificar_lives()
    print(f"Streamers ao vivo: {streamers_ao_vivo}")

    bot.infinity_polling()