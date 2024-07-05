from time import strftime
from pyowm.owm import OWM
from flask import Flask, config, render_template, redirect, request
import json
import requests
from datetime import datetime
import mqqt


app = Flask(__name__)
chave = "b2e13de0494d15838803adaf4b1182ce"
lat = -22.90
long = -43.19
url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&appid={chave}"
resposta = requests.get(url)
dados_tempo = resposta.json()



#print(dados_tempo)

#with open("estado.json","w") as arq:
# estado=[{"luzes":[{"luz sala":"acesa","luz cozinha":"apagada","luz quarto":"apagada","luz banheiro":"acesa"}]},{"temperatura":25},{"umidade":20, "janela":"aberta"},{"modo":"auto"}]
# json.dump(estado,arq,indent=4)


def kelvin_para_celcius(temp):
  return temp - 273.15


def previsao_tempo():
  data = datetime.now()
  data = data.strftime("%d/%m/%Y")
  tipo_tempo = dados_tempo["weather"][0]["main"]
  temp_atual = round(kelvin_para_celcius(dados_tempo["main"]["temp"]), 1)
  temp_min = round(kelvin_para_celcius(dados_tempo["main"]["temp_min"]), 1)
  temp_max = round(kelvin_para_celcius(dados_tempo["main"]["temp_max"]), 1)
  cidade = dados_tempo["name"]
  umidade = dados_tempo["main"]["humidity"]
  previsao = {
      "data": data,
      "cidade": cidade,
      "tipo_tempo": tipo_tempo,
      "temp_atual": temp_atual,
      "temp_max": temp_max,
      "temp_min": temp_min,
      "umidade": umidade
  }
  return previsao


def salva_estado(estado):
  with open("estado.json", "w") as arq:
    json.dump(estado, arq, indent=4)


def estado_atual():
  try:
    with open("estado.json", "r") as arq:
      settings = json.load(arq)
    return settings
  except json.JSONDecodeError:
    return None
  except FileNotFoundError:
    return None


def config_atual():
  try:
    with open("settings.json", "r") as arq:
      settings = json.load(arq)
    return settings
  except json.JSONDecodeError:
    return None
  except FileNotFoundError:
    return None


@app.route("/")
def home():
  previsao = previsao_tempo()
  config = config_atual()
  estado = estado_atual()
  return render_template("home.html",
                         settings=config,
                         estado=estado,
                         previsao=previsao)


@app.route("/settings")
def settings():
  config = config_atual()
  return render_template("settings.html", settings=config)


@app.route("/salvar", methods=["POST", "GET"])
def salva():
  if request.method == "POST":
    temp_max = request.form["temp_max"]
    temp_min = request.form["temp_min"]
    umidade = request.form["umidade"]
    horario_acender = request.form["horario_acender"]
    horario_apagar = request.form["horario_apagar"]
    preferencias = [{
        "temp_max": temp_max,
        "temp_min": temp_min
    }, {
        "umidade": umidade
    }, {
        "horario_luzes": [horario_acender,horario_apagar]
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
        print(f"Controle alterado para {novo}")
  with open("estado.json", "w") as arq:
    json.dump(estado, arq, indent=4)
  return redirect("/")


@app.route("/altera_luz/<string:luz>/<string:modo>")
def altera_luz(luz, modo):
  novo = "apagada" if modo == "acesa" else "acesa"
  estado = estado_atual()
  if estado is not None:
    estado[0]["luzes"][0][luz] = novo
    print(f"{luz} {novo}")
  with open("estado.json", "w") as arq:
    json.dump(estado, arq, indent=4)
  return redirect("/")


@app.route("/altera_temp/<int:temp>/<string:acao>")
def altera_temp(temp, acao):
  if acao == "up" and temp <= 29:
    temp += 1
    print(f"Temperatura aumentada para {temp}")
  elif acao == "down" and temp >= 19:
    temp -= 1
    print(f"Temperatura diminuída para {temp}")
  estado = estado_atual()
  if estado is not None:
    estado[1]["temperatura"] = temp
    salva_estado(estado)
  return redirect(request.referrer)


@app.route("/altera_janela/<string:modo>")
def altera_janela(modo):
  novo = "fechada" if modo == "aberta" else "aberta"
  estado = estado_atual()
  if estado is not None:
    estado[2]["janela"] = novo
    salva_estado(estado)
    print(f"Janela {novo}")
  return redirect(request.referrer)


@app.route("/teste")
def teste():
  return render_template("teste.html")

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=80)
