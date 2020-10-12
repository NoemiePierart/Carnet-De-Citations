from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from citations.auth import login_required
from citations.db import get_db
from datetime import datetime

bp = Blueprint('passages', __name__)

@bp.route('/')
def home():
    return render_template("passages/home.html")

@bp.route('/passages/mes_citations/')
def mes_citations():
    db = get_db()
    
    # Export list of passages where user == current user
    if g.user == None: 
        passages=[]
    else :
        passages = db.execute("SELECT * FROM passages WHERE user_id=?", (g.user['id'],)).fetchall()

    return render_template("passages/mes_citations.html", passages=passages)

@bp.route('/passages/inspiration/')
def inspiration():
    db = get_db()
    
    # Export list of passages where user == user4(admin): 
    inspirations = db.execute("SELECT * FROM passages WHERE user_id=4").fetchall()

    return render_template("passages/inspiration.html", inspirations=inspirations)


@bp.route('/passages/create/', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':

        auteur = request.form["auteur"]
        livre = request.form["livre"]
        texte = request.form["texte"]
        annee_citation = int(request.form["annee_citation"])
        date_ajout = datetime.now()
        commentaire = "mon commentaire"
        error = None

        if not auteur:
            error = 'Merci de saisir un auteur'

        if not livre:
            error = 'Merci de saisir une oeuvre'

        if not texte:
            error = 'Merci de saisir un texte'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute("INSERT INTO passages (auteur, livre, texte, annee_citation, date_ajout, commentaire, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)", (auteur, livre, texte, annee_citation, date_ajout, commentaire, g.user['id']),
            )
            db.commit()
            message = "Votre citation a bien été ajoutée à votre carnet ! "
            passages = db.execute("SELECT * FROM passages WHERE user_id=?", (g.user['id'],)).fetchall()
            return render_template('passages/mes_citations.html', message=message, passages=passages)
            
    return render_template('passages/create.html')

def get_passage(id, check_user=True):
    passage = (
        get_db()
        .execute(
            "SELECT * FROM passages JOIN users ON users.id = passages.user_id WHERE passages.id = ?", 
            (id,),
        )
        .fetchone()
    )

    #if passage is None:
       # abort(404, "passage id {0} doesn't exist.".format(id))

    #if check_user and passage['user_id'] != g.user['id']:
        #abort(403)

    return passage

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    
    if request.method == "GET":

        db = get_db()
        passage = db.execute(
                "SELECT * FROM passages WHERE id = ?", 
                (id,),
            ).fetchone()
        old_auteur = passage['auteur']
        old_livre = passage['livre']
        old_texte = passage['texte']
        old_annee_citation = int(passage['annee_citation'])

        return render_template('passages/update.html', passage=passage, old_auteur=old_auteur, old_livre=old_livre, old_texte=old_texte, old_annee_citation=old_annee_citation)

    if request.method == "POST":
        passage = get_passage(id)
        new_auteur = request.form["auteur"]
        new_livre = request.form["livre"]
        new_texte = request.form["texte"]
        new_annee_citation = int(request.form["annee_citation"])
        new_date_ajout = datetime.now()
        new_commentaire = "mon commentaire"
        error = None

        if not new_auteur:
            error = 'Merci de saisir un auteur'

        if not new_livre:
            error = 'Merci de saisir une oeuvre'

        if not new_texte:
            error = 'Merci de saisir un texte'

        if error is not None:
            flash(error)

        else:
            db = get_db()
            db.execute("UPDATE passages SET auteur=?, livre=?, texte=?, annee_citation=?, commentaire=? WHERE id = ?", (new_auteur, new_livre, new_texte, new_annee_citation, new_commentaire, id,)
                )
            db.commit()
            message = "Votre citation a bien été modifiée ! "
            passages = db.execute("SELECT * FROM passages WHERE user_id=?", (g.user['id'],)).fetchall()
            return render_template('passages/mes_citations.html', message=message, passages=passages)

@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.
    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_passage(id)
    db = get_db()
    db.execute("DELETE FROM passages WHERE id = ?", (id,))
    db.commit()
    message = "Votre citation a bien été supprimée de votre carnet."
    passages = db.execute("SELECT * FROM passages WHERE user_id=?", (g.user['id'],)).fetchall()
    return render_template('passages/mes_citations.html', message=message, passages=passages)