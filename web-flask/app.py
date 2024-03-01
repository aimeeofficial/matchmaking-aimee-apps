from flask import Flask, request, session, render_template
import pickle
from firebase_admin import credentials, firestore, initialize_app

# Template Flask
app = Flask(__name__)
app.secret_key = 'd4ng3r_z0n3'

# Untuk menghubungkan aplikasi dengan firebase
cred = credentials.Certificate('aimee-firebase-adminsdk.json')
initialize_app(cred)

db = firestore.client()

# Mengambil data 'StartupList' di firebase
collection_ref = db.collection('StartupList')

# Mengakses model yang sudah ditrain
model_file = open('model.pkl', 'rb')
model = pickle.load(model_file, encoding='bytes')

# Membuat list businessModel
businessModel = ['B2B','B2C','Hybrid B2B and B2C','Retail dan Distributor','SaaS']

# Membuat list province
province = ['Kalimantan Selatan','Aceh','Bali','Banten','Bengkulu','DI Yogyakarta','DKI Jakarta','Gorontalo','Jambi','Jawa Barat','Jawa Tengah','Jawa Timur','Kalimantan Barat','Kalimantan Selatan','Kalimantan Tengah','Kalimantan Timur','Kalimantan Utara','Kepulauan Bangka Belitung','Kepulauan Riau','Lampung','Maluku','Maluku Utara','Nusa Tenggara Barat','Nusa Tenggara Timur','Riau','Sulawesi Barat','Sulawesi Selatan','Sulawesi Tengah','Sulawesi Tenggara','Sulawesi Utara','Sumatera Selatan','Sumatera Utara']

# Membuat list industrySector
industrySector = ['Agriculture','Aquaculture','Beauty','Blockchain','Consultant Services','Digital Business Development','EduTech','Electronic','Energy Distribution','Farms','Fashion','Fisheries','Food and Beverage','Food Processing','Graphic Design and Creative','Green Technology','Herbs','Hospitality','Internet','Open Journal System','Petshop','Production','Retail','Services','Sport and Music','Technology and Information','Textile']

# Mengakses directory /
@app.route('/')
def index():
    return render_template('index.html', business_model='')

# Mengakses directory /predict dengan method POST
@app.route('/predict', methods=['POST'])
def predict():
    # Mengambil data provinsi dan sektorIndustri di form html
    provinsi, sektorIndustri = [x for x in request.form.values()]

    # Membuat variabel session untuk di save di local web
    session['remembered_province'] = provinsi
    session['remembered_industrySector'] = sektorIndustri

    # Melakukan prediksi business model
    output = businessModel[model.predict([[provinsi,sektorIndustri]])[0]]
    
    # Melakukan filter data dari firebase
    query = collection_ref.where('provinsi', '==', province[int(provinsi)]).where('sektorIndustri', '==', industrySector[int(sektorIndustri)]).where('modelBisnis', '==', output)
    documents = query.stream()
    data = [doc.to_dict() for doc in documents]

    return render_template('index.html', business_model=output, matches_startup=data, remembered_province=session.get('remembered_province', ''), remembered_industrySector=session.get('remembered_industrySector', ''))

# Mengakses api
@app.route('/api/<int:provinsi>/<int:sektorIndustri>')
def get_api(provinsi,sektorIndustri):
    # Melakukan prediksi business model
    output = businessModel[model.predict([[provinsi,sektorIndustri]])[0]]

    # Melakkan filter data dari firebase
    query = collection_ref.where('provinsi', '==', province[int(provinsi)]).where('sektorIndustri', '==', industrySector[int(sektorIndustri)]).where('modelBisnis', '==', output)
    documents = query.stream()
    data = [doc.to_dict() for doc in documents]

    return data

if __name__ == '__main__':
    app.run(debug=False)
