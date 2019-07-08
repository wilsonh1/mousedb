import os

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect

from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "mousedb.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)

class Strains(db.Model):
    db.__tablename__ = 'strains'
    id = db.Column(db.String(20), primary_key=True)

    mice = db.relationship("Mice", back_populates="strains", cascade="all, delete, delete-orphan", order_by="Mice.dob, Mice.id")

class Mice(db.Model):
    db.__tablename__ = 'mice'
    id = db.Column(db.String(20), primary_key=True)
    count = db.Column(db.Integer)
    sex = db.Column(db.String(1))
    dob = db.Column(db.Date)
    notes = db.Column(db.String(200))
    sid = db.Column(db.String(20), db.ForeignKey('strains.id'))

    strains = db.relationship("Strains", back_populates="mice")

@app.route('/', methods=["GET", "POST"])
def home():
    if request.form:
        try:
            if request.form.get("strain"):
                mouse = Mice(id=request.form.get("id"), count=int(request.form.get("count")), sex=request.form.get("sex"), dob=datetime.strptime(request.form.get("dob"), '%Y-%m-%d'), notes=request.form.get("notes"))
                strain = Strains.query.filter_by(id=request.form.get("strain")).first()
                strain.mice.append(mouse)
                db.session.add(mouse)
            else:
                strain = Strains(id=request.form.get("id"))
                db.session.add(strain)
            db.session.commit()
        except Exception as e:
            print("Failed to add")
            print(e)
            db.session.rollback()
    strains = Strains.query.all()
    return render_template("home.html", strains=strains)

@app.route("/update", methods=["POST"])
def update():
    try:
        mouse = Mice.query.filter_by(id=request.form.get("oldid")).first()
        mouse.id = request.form.get("newid")
        mouse.count = request.form.get("newcount")
        if request.form.get("newsex"):
            mouse.sex = request.form.get("newsex")
        mouse.dob = datetime.strptime(request.form.get("newdob"), '%Y-%m-%d')
        db.session.commit()
    except Exception as e:
        print("Failed to update")
        print(e)
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    id = request.form.get("id")
    if request.form.get("table")=="strain":
        td = Strains.query.filter_by(id=id).first()
    else:
        td = Mice.query.filter_by(id=id).first()
    db.session.delete(td)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
