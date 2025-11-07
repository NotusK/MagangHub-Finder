from flask import Flask, render_template, request, jsonify
import requests
import json
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        jurusan = request.form.get('jurusan')
        kode_provinsi = request.form.get('provinsi')
        target_kabupaten = request.form.getlist('kabupaten[]')
        
        base_url = "https://maganghub.kemnaker.go.id/be/v1/api/list/vacancies-aktif"
        limit = 100
        page = 1
        found_positions = []

        while True:
            url = f"{base_url}?order_by=jumlah_kuota&order_direction=DESC&page={page}&limit={limit}&kode_provinsi={kode_provinsi}"
            response = requests.get(url)
            
            if response.status_code != 200:
                break
            
            try:
                data = response.json()
            except:
                break
            
            jobs = data.get("data", [])
            if not jobs:
                break
            
            for item in jobs:
                id_posisi = item.get("id_posisi", "")
                posisi = item.get("posisi", "")
                jumlah_kuota = item.get("jumlah_kuota", "")
                jumlah_terdaftar = item.get("jumlah_terdaftar", "")
                
                program_studi_raw = item.get("program_studi", "[]")
                try:
                    program_studi_list = json.loads(program_studi_raw)
                except:
                    program_studi_list = []
                
                program_titles = [ps.get("title", "") for ps in program_studi_list]
                
                perusahaan = item.get("perusahaan", {})
                nama_perusahaan = perusahaan.get("nama_perusahaan", "")
                nama_kabupaten = perusahaan.get("nama_kabupaten", "")
                
                if any(jurusan.lower() in title.lower() for title in program_titles) and \
                   any(kab in nama_kabupaten.upper() for kab in target_kabupaten):
                    found_positions.append({
                        "id_posisi": id_posisi,
                        "nama_perusahaan": nama_perusahaan,
                        "nama_kabupaten": nama_kabupaten,
                        "posisi": posisi,
                        "jumlah_kuota": jumlah_kuota,
                        "jumlah_terdaftar": jumlah_terdaftar,
                    })
            
            time.sleep(0.5)
            page += 1
            
            # Safety limit
            if page > 50:
                break
        
        return jsonify({
            'count': len(found_positions),
            'results': found_positions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)