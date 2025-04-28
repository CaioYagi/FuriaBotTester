import telebot
import requests
import json
import atexit
from newsapi import NewsApiClient


bot = telebot.TeleBot("8080855422:AAFZEO19Aryh0JElba_Gi8KX9w9EQtnCOvg")
newsapi_key = '43985f5d94b340468a03bfbcf3ed2f59'

newsapi = NewsApiClient(api_key=newsapi_key)
def get_top_news(country):
    top_headlines = newsapi.get_top_headlines(country=country)
    articles = top_headlines['articles']
    return articles

def get_twitch_access_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials",
        "redirect_uri": "https://ngrok.com/r/iep "
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()["access_token"]

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

#comando /start
@bot.message_handler(commands=['start'])
def start(msg: telebot.types.Message):
    bot.reply_to(msg, "Olá, sou o BotFuria! Como posso ajudar? Aqui estão alguns comandos que você pode usar:\n\n"
                      "/ajuda - Para obter ajuda\n"
                      "/dica - Para receber uma dica aleatória\n"
                      "/equipes - Para saber mais sobre as equipes da Furia\n"
                      "/info - Para saber mais sobre mim\n"
                      "/influencia - Para saber mais sobre os influenciadores da Furia\n"
                      "/twitch - Para saber mais sobre a Furia na Twitch\n"
                      "/links - Para obter links da Fúria\n")


# Adicionando um novo comando 'dica'
@bot.message_handler(commands=['dica'])
def dica(msg: telebot.types.Message):
    dicas = [
        "Já comprou a camiseta da Furia com a Adidas?FICOU LINDAAA!!! Dá uma olhada lá no [site!] (https://www.furia.gg) \n",
        "A Furia tem uma comunidade incrível de fãs! Dá uma olhada lá no nosso [Instagram](https://www.instagram.com/furiagg) \n",
        "A Furia já participou de vários campeonatos internacionais! [clique aqui para saber mais](https://pt.wikipedia.org/wiki/Furia_Esports)\n",
        "A Furia tem uma equipe de jogadores talentosos e dedicados! para saber mais use o comando /equipes \n",
        "Você sabia que a Furia tem uma equipe de Futebol de 7? Eles competem na Kings League!\n [clique aqui](https://youtube.com/@furiaf.c.?si=9P_ZQmZcRGer7z__) para ver mais o conteudo prensente no youtube \n Ou caso você queira acessar o Instagram da equipe de Futebol de 7 [clique aqui](https://www.instagram.com/furia.football/) \n",
        "A Furia também realiza eventos e torneios para os fãs! acesse o:\n X / Twitter \n [clique aqui](https://x.com/FURIA) \n ou o Instagram \n [clique aqui](https://www.instagram.com/furiagg) \n",
        "Você sabia que Furia tem uma equipe de VALORANT? Eles são incríveis!\nAcesse o canal do [Youtube](https://www.youtube.com/@FURIAggVAL)\nAcesse o [Twitter / X](https://x.com/FURIA)\n Acesse o [Instagram](https://www.instagram.com/furiagg) \n Acesse o [TikTok](https://www.tiktok.com/@furiagg) \n",
        "A Furia é conhecida por sua presença forte nas redes sociais! Siga-nos no [Instagram](https://www.instagram.com/furiagg) \n",
        "A Furia tem uma equipe de CS:GO incrível! Eles competem em torneios internacionais e são muito respeitados na cena!\n Acesse o canal do [Youtube](https://www.youtube.com/@FURIAggCS)\nAcesse o [Twitter / X](https://x.com/FURIA)\n Acesse o [Instagram](https://www.instagram.com/furiagg) \n Acesse o [TikTok](https://www.tiktok.com/@furiagg) \n",
        "A Furia é uma das principais organizações de esports do Brasil! Eles têm uma base de fãs incrível e são conhecidos por seu espírito competitivo!\n Acesse o canal do [Youtube](https://www.youtube.com/@FURIAggCS)\nAcesse o [Twitter / X](https://x.com/FURIA)\n Acesse o [Instagram](https://www.instagram.com/furiagg) \n Acesse o [TikTok](https://www.tiktok.com/@furiagg) \n",
        "A Furia tem uma equipe de League of Legends que compete em torneios nacionais e internacionais! Eles são conhecidos por seu estilo de jogo agressivo e emocionante!\n Acesse o canal do [Youtube](https://www.youtube.com/@FURIAggLOL)\nAcesse o [Twitter / X](https://x.com/FURIA)\n Acesse o [Instagram](https://www.instagram.com/furiagg) \n Acesse o [TikTok](https://www.tiktok.com/@furiagg) \n",
    ]
    from random import choice
    parse_mode = 'Markdown' 
    bot.reply_to(msg, choice(dicas), parse_mode=parse_mode)

# Comando 'ajuda' atualizado
@bot.message_handler(commands=['ajuda'])
def ajuda(msg: telebot.types.Message):
    bot.reply_to(msg, "Estou aqui para ajudar! Aqui estão alguns comandos que você pode usar:\n\n"
                      "/start - Para iniciar uma conversa comigo\n"
                      "/info - Para saber mais sobre mim\n"
                      "/dica - Para receber uma dica aleatória\n"
                      "/equipes - Para saber mais sobre as equipes da Furia\n"
                      "/ajuda - Para ver esta mensagem de ajuda novamente")

# Comando 'equipes' atualizado
@bot.message_handler(commands=['equipes'])
def equipes(msg: telebot.types.Message):
    bot.reply_to(msg, "As equipes da Furia são formadas por jogadores talentosos e dedicados.\n\n")
    bot.reply_to(msg, "Aqui estão algumas das equipes:\n\n"
                      "1. Furia CS:GO - A equipe de Counter-Strike: Global Offensive. Para ver o canal do [youtube] (https://www.youtube.com/channel/UCXXXX) /csgo para saber mais.\n"
                      "2. Furia VALORANT - A equipe de VALORANT \n"
                      "3. Furia League of Legends - A equipe de League of Legends\n"
                      "4. Furia Futebol de 7 - A equipe de Futebol de 7(Kings League)\n\n"
                      "Para mais informações sobre cada equipe, use o comando /valorant, /csgo, /lol, /freefire ou /fut7\n\n")
    parse_mode = 'Markdown'
@bot.message_handler(commands=['valorant'])
def valorant(msg: telebot.types.Message):
    bot.reply_to(msg, "Você sabia que Furia tem uma equipe de VALORANT? Eles são incríveis!\nAcesse o canal do [Youtube](https://www.youtube.com/@FURIAggVAL)\nAcesse o [Twitter / X](https://x.com/FURIA)\n Acesse o [Instagram](https://www.instagram.com/furiagg) \n Acesse o [TikTok](https://www.tiktok.com/@furiagg) \n")

@bot.message_handler(commands=['csgo'])
def csgo(msg: telebot.types.Message):
    bot.reply_to(msg, "A Furia tem uma equipe de CS:GO incrível! Eles competem em torneios internacionais e são muito respeitados na cena!\n Acesse o canal do [Youtube](https://www.youtube.com/@FURIAggCS)\nAcesse o [Twitter / X](https://x.com/FURIA)\n Acesse o [Instagram](https://www.instagram.com/furiagg) \n Acesse o [TikTok](https://www.tiktok.com/@furiagg) \n")

@bot.message_handler(commands=['lol'])
def lol(msg: telebot.types.Message):
    bot.reply_to(msg, "A Furia tem uma equipe de League of Legends que compete em torneios nacionais e internacionais! Eles são conhecidos por seu estilo de jogo agressivo e emocionante!\n Acesse o canal do [Youtube](https://www.youtube.com/@FURIAggLOL)\nAcesse o [Twitter / X](https://x.com/FURIA)\n Acesse o [Instagram](https://www.instagram.com/furiagg) \n Acesse o [TikTok](https://www.tiktok.com/@furiagg) \n")


@bot.message_handler(commands=['fut7'])
def fut7(msg: telebot.types.Message):
        bot.reply_to(msg, "A Furia tem uma equipe de Futebol de 7 que compete na Kings League! Eles são conhecidos por seu estilo de jogo agressivo e emocionante!\n Acesse o canal do [Youtube](https://youtube.com/@furiaf.c.?si=9P_ZQmZcRGer7z__)\nAcesse o [Twitter / X](https://x.com/FURIA)\n Acesse o [Instagram](https://www.instagram.com/furia.football/) \n Acesse o [TikTok](https://www.tiktok.com/@furiagg) \n")



@bot.message_handler(func=lambda msg: True)  # Captura todas as mensagens
def comandos_sem_barra(msg: telebot.types.Message):
    texto = msg.text.lower()  # Converte o texto para minúsculas para facilitar a comparação

    # Lista de palavras que acionam o comando 'start'
    palavras_start = ['oi', 'ola', 'olá', 'oii', 'eai', 'salve', 'salveee''salvee', 
                      'boa', 'bomdia', 'boanoite', 'boa tarde', 'bom dia', 
                      'boa noite', 'boatarde', 'tudo bem', 'tudo certo', 'tudobem',
                      'tudocerto', 'tudo certo?', 'tudo bem?', 'oi bot', 'ola bot',]

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

bot.infinity_polling()