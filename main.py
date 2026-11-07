
import os
from collections import deque
from statistics import mean

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

resultats = deque(maxlen=100)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bienvenue sur Moyer Crash Stats !\n\n"
        "Commandes disponibles :\n"
        "/ajouter 2.5 - enregistrer un multiplicateur\n"
        "/historique - voir les derniers résultats saisis\n"
        "/stats - consulter les statistiques\n"
        "/effacer - vider l'historique en mémoire\n\n"
        "Les résultats sont saisis manuellement. "
        "Ils ne prédisent pas les prochains tours."
    )


async def ajouter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Utilise : /ajouter 2.5"
        )
        return

    try:
        valeur = float(context.args[0].replace(",", "."))
        if not 1 <= valeur <= 1000000:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "Entre un multiplicateur valide, par exemple /ajouter 1.75"
        )
        return

    resultats.append(valeur)
    await update.message.reply_text(
        f"Résultat enregistré : {valeur:.2f}x\n"
        f"Résultats en mémoire : {len(resultats)}"
    )


async def historique(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not resultats:
        await update.message.reply_text(
            "Aucun résultat enregistré. Utilise /ajouter 2.5"
        )
        return

    lignes = [f"{i}. {v:.2f}x" for i, v in enumerate(resultats, 1)]
    await update.message.reply_text(
        "Historique (100 résultats maximum) :\n" + "\n".join(lignes)
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not resultats:
        await update.message.reply_text(
            "Pas encore de données. Utilise /ajouter 2.5"
        )
        return

    petits = sum(v < 2 for v in resultats)
    await update.message.reply_text(
        f"STATISTIQUES\n"
        f"Nombre de résultats : {len(resultats)}\n"
        f"Moyenne : {mean(resultats):.2f}x\n"
        f"Minimum : {min(resultats):.2f}x\n"
        f"Maximum : {max(resultats):.2f}x\n"
        f"Résultats inférieurs à 2x : {petits}\n\n"
        "Ces statistiques décrivent uniquement les données saisies. "
        "Elles ne prédisent pas le prochain résultat."
    )


async def effacer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resultats.clear()
    await update.message.reply_text(
        "Historique en mémoire effacé."
    )


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("La variable TELEGRAM_BOT_TOKEN est absente.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ajouter", ajouter))
    app.add_handler(CommandHandler("historique", historique))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("effacer", effacer))
    app.run_polling()


if __name__ == "__main__":
    main()
