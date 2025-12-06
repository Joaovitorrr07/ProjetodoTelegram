from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime, timedelta
import emoji
agendamentos = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Eu sou seu bot")
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá, Mundo! 🚀")

async def agendar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) < 3:
        await update.message.reply_text('Uso correto: /agendar DD/MM/AAAA HH:MM DURAÇÃO')
        return
    try:

        agenda = context.args[0].split('/')
        horario = context.args[1].split(':')
        duracao = int(context.args[2])

        dia, mes, ano = int(agenda[0]), int(agenda[1]), int(agenda[2])
        hora, minutos = int(horario[0]), int(horario[1])

        horario_agendado = datetime(ano, mes, dia, hora, minutos)
        fim = horario_agendado + timedelta(minutes=duracao)

        evento = {"inicio": horario_agendado, "fim": fim}

        for evento in agendamentos:
            if horario_agendado < evento["fim"] and evento["inicio"] < fim:
                await update.message.reply_text('Você ja tem um evento marcado para esse horário!')
                return

        agendamentos.append({"inicio": horario_agendado, "fim": fim})
        await update.message.reply_text('Agendado com sucesso!')

    except ValueError:
        await update.message.reply_text('você digitou de forma incorreta! Tente: /agendar DD/MM/AAAA HH:MM DURAÇÃO')

async def consultar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) < 1:
        await update.message.reply_text('Uso correto: /consultar DD/MM/AAAA')
        return

    try:
        data_str = context.args[0]
        data_consultada = datetime.strptime(data_str, "%d/%m/%Y").date()
    except ValueError:
        await update.message.reply_text('Data inválida! Use o formato DD/MM/AAAA')
        return

    eventos_dia = []

    for eventos in agendamentos:
        if eventos["inicio"].date() == data_consultada:
            inicio = eventos["inicio"].strftime("%H:%M")
            fim = eventos["fim"].strftime("%H:%M")
            eventos_dia.append(f"{emoji.emojize('📌', language='pt')}Das {inicio} às {fim}")

    if eventos_dia:
        resposta = f'Eventos do dia:\n' + f'\n'.join(eventos_dia)
    else:
        resposta = 'Você não tem eventos para essa data.'

    await update.message.reply_text(resposta)

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) < 2:
        await update.message.reply_text('Forma correta: /cancelar DD/MM/AAAA HH:MM')
        return

    try:
        data = context.args[0]
        hora = context.args[1]
        data_cancel = datetime.strptime(f'{data} {hora}', "%d/%m/%Y %H:%M")
    except ValueError:
        await update.message.reply_text('Data inválida! Use o formato DD/MM/AAAA')
        return
    for eventos in agendamentos:
        if eventos["inicio"] == data_cancel:
            agendamentos.remove(eventos)
            await update.message.reply_text('Evento cancelado com sucesso!')
            return

    await update.message.reply_text('Não há eventos para essa data.')

async def sugerir(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) < 2:
        await update.message.reply_text('Forma correta: /sugerir DD/MM/AAAA DURAÇÃO')
        return
    try:
        data =context.args[0]
        minutos = int(context.args[1])
        data_desejada = datetime.strptime(data, '%d/%m/%Y').date()
    except ValueError:
        await update.message.reply_text('Data inválida! Use o formato DD/MM/AAAA')
        return

    inicio_dia = datetime(data_desejada.year, data_desejada.month, data_desejada.day, 7, 0)
    fim_dia = datetime(data_desejada.year, data_desejada.month, data_desejada.day, 20, 00)

    eventos_data = [
        evento for evento in agendamentos
        if evento["inicio"].date() == data_desejada
    ]
    eventos_data.sort(key = lambda x: x["inicio"])

    inicio_possivel = inicio_dia

    for evento in eventos_data:
        if evento["inicio"] - inicio_possivel >= timedelta(minutes= minutos):
            return await update.message.reply_text(f"Você pode agendar no dia {data} a partir de {inicio_possivel.strftime('%H:%M')}")
        else:
            inicio_possivel = max(inicio_possivel, evento["fim"])

    if fim_dia - inicio_possivel >= timedelta(minutes= minutos):
        await update.message.reply_text(f"Você pode agendar no dia {data} a partir de {inicio_possivel.strftime('%H:%M')}")

    else:
        await update.message.reply_text('Não há horário disponível para esse evento nessa data!')

def main():
    app = ApplicationBuilder().token("SEU TOKEN DO TELEGRAM").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(CommandHandler("agendar", agendar))
    app.add_handler(CommandHandler("consultar", consultar))
    app.add_handler(CommandHandler("cancelar", cancelar))
    app.add_handler(CommandHandler("sugerir", sugerir))
    app.run_polling()
if __name__ == "__main__":
    main()

