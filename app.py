from flask import Flask, render_template, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)
DATA_PATH = 'navarea.json'

def simular_coordenadas(i):
    lat = -23.0 + i * 0.05
    lon = -42.0 + i * 0.05
    return [[lat, lon], [lat, lon + 0.1], [lat + 0.1, lon + 0.1], [lat + 0.1, lon]]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alertas')
def alertas():
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except:
        return jsonify([])

@app.route('/atualizar')
def atualizar():
    url = 'https://www.marinha.mil.br/chm/sites/www.marinha.mil.br.chm/files/opt/avradio_318.json'
    try:
        r = requests.get(url, timeout=10)
        dados = r.json()
        alertas = []
        for i, item in enumerate(dados.get('avisos', [])[:5]):
            texto = item.get('descricao', '')
            titulo = item.get('numero', f'NAVAREA {i+1:03}')
            descricao = texto[:200] + '...' if len(texto) > 200 else texto
            poligono = simular_coordenadas(i)
            centro = [sum(p[0] for p in poligono)/4, sum(p[1] for p in poligono)/4]
            alertas.append({
                'titulo': titulo,
                'descricao': descricao,
                'data': item.get('data', datetime.now().isoformat()),
                'centro': centro,
                'cor': '#cc0000',
                'poligono': poligono
            })
        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(alertas, f, indent=2, ensure_ascii=False)
        return jsonify({'status': 'ok', 'total': len(alertas)})
    except Exception as e:
        return jsonify({'status': 'erro', 'mensagem': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
