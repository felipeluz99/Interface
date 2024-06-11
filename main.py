from pyowm.owm import OWM
from flask import Flask, render_template, redirect, request
import json

app = Flask(__name__)
chave = "b2e13de0494d15838803adaf4b1182ce"

#with open("estado.json","w") as arq:
 # estado=[{"luzes":[{"luz sala":"acesa","luz cozinha":"apagada","luz quarto":"apagada","luz banheiro":"acesa"}]},{"temperatura":25},{"umidade":20, "janela":"aberta"},{"modo":"auto"}]
 # json.dump(estado,arq,indent=4)

def salva_estado(estado):
  with open("estado.json","w") as arq:
    json.dump(estado,arq,indent=4)


def estado_atual():
  try:
    with open("estado.json","r") as arq:
      settings = json.load(arq)
    return settings
  except json.JSONDecodeError:
    return None
  except FileNotFoundError:
    return None


def config_atual():
  try:
    with open("settings.json","r") as arq:
      settings = json.load(arq)
    return settings
  except json.JSONDecodeError:
    return None
  except FileNotFoundError:
    return None
  

@app.route("/")
def home():
  config = config_atual()
  estado = estado_atual()
  return render_template("home.html", settings=config, estado=estado)


@app.route("/settings")
def settings():
  config = config_atual()
  return render_template("settings.html", settings = config)


@app.route("/salvar", methods=["POST", "GET"])
def salva():
  if request.method == "POST":
    temp_max = request.form["temp_max"]
    temp_min = request.form["temp_min"]
    umidade = request.form["umidade"]
    preferencias = [{
        "temp_max": temp_max,
        "temp_min": temp_min
    }, {
        "umidade": umidade
    }]
    with open("settings.json", "w") as arq:
      json.dump(preferencias, arq, indent=4)
  return redirect(request.referrer)


@app.route("/altera_modo/<string:modo>")
def altera_modo(modo):
  novo = "manual" if modo == "auto" else "auto"
  estado = estado_atual()
  if estado is not None:
    for i in estado:
      if "modo" in i:
        i["modo"] = novo
  with open("estado.json","w") as arq:
    json.dump(estado,arq,indent=4)
  return redirect("/") 


@app.route("/altera_luz/<string:luz>/<string:modo>")
def altera_luz(luz, modo):
  novo = "apagada" if modo == "acesa" else "acesa"
  estado = estado_atual()
  if estado is not None:
    estado[0]["luzes"][0][luz] = novo
  with open("estado.json","w") as arq:
    json.dump(estado,arq,indent=4)
  return redirect("/")


@app.route("/altera_temp/<int:temp>/<string:acao>")
def altera_temp(temp, acao):
  if acao=="up" and temp<=29:
    temp+=1
  elif acao=="down" and temp>=19:
    temp-=1
  estado = estado_atual()
  if estado is not None:
    estado[1]["temperatura"] = temp
    salva_estado(estado)
  return redirect(request.referrer)

  
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=80)
