from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# Load JSON file once at startup
with open('public/vacancies-aktif.json', 'r', encoding='utf-8') as f:
    all_jobs = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        jurusan = request.form.get('jurusan', '').lower()
        kode_provinsi = request.form.get('provinsi', '')
        target_kabupaten = [kab.upper() for kab in request.form.getlist('kabupaten[]')]

        found_positions = []

        for item in all_jobs:
            id_posisi = item.get("id_posisi", "")
            posisi = item.get("posisi", "")
            jumlah_kuota = item.get("jumlah_kuota", "")
            jumlah_terdaftar = item.get("jumlah_terdaftar", "")

            perusahaan = item.get("perusahaan", {})
            nama_perusahaan = perusahaan.get("nama_perusahaan", "")
            nama_kabupaten = perusahaan.get("nama_kabupaten", "")
            kode_prov = perusahaan.get("kode_provinsi", "")

            # Skip jobs from other provinces if kode_provinsi is specified
            if kode_provinsi and kode_prov != kode_provinsi:
                continue

            # Parse prodi
            program_studi_raw = item.get("program_studi", "[]")
            try:
                program_studi_list = json.loads(program_studi_raw)
            except:
                program_studi_list = []

            program_titles = [ps.get("title", "") for ps in program_studi_list]

            if any(jurusan in title.lower() for title in program_titles) and \
               any(kab in nama_kabupaten.upper() for kab in target_kabupaten):
                found_positions.append({
                    "id_posisi": id_posisi,
                    "nama_perusahaan": nama_perusahaan,
                    "nama_kabupaten": nama_kabupaten,
                    "posisi": posisi,
                    "jumlah_kuota": jumlah_kuota,
                    "jumlah_terdaftar": jumlah_terdaftar,
                })

        return jsonify({
            'count': len(found_positions),
            'results': found_positions
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
