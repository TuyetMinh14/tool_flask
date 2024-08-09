from flask import Flask, render_template, request,redirect, url_for, jsonify, session 
from flask_sqlalchemy import SQLAlchemy


from os import path
import json

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PAGE_SIZE'] = 1
app.config['SECRET_KEY'] = 'KL-2024'

FILE_NAME = None
ALLOWED_EXTENSIONS = set(["json"])

# tokenizer, model = init()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)
noofQuestion = 1


class Title(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_text = db.Column(db.String)
    paragraphs = db.relationship('Paragraph', backref='title', lazy=True)

    def __init__(self, title_text):
        self.title_text = title_text

    def __repr__(self):
        return self.id 

class Paragraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    context = db.Column(db.String)
    title_id = db.Column(db.Integer, db.ForeignKey('title.id'))
    qas_answers = db.relationship('QASAnswers', backref='paragraph', lazy=True)


    def get_all_qas_answers(self):
        return QASAnswers.query.filter_by(paragraph_id=self.id).all()
    def __init__(self, context, title_id):
        self.context = context
        self.title_id = title_id

    def __repr__(self):
        return str(self.id)

    @property
    def has_prev(self):
        return self.prev_para is not None

    @property
    def has_next(self):
        return self.next_para is not None

    def get_count(self):
        return db.session.query(Paragraph).count()

    def prev_para(self):
        count = self.get_count()
        pid = self.id
        while count > 0:
            prev_post = None
            pid -= 1
            if db.session.query(Paragraph).get(pid) is not None:
                prev_post = db.session.query(Paragraph).get(pid)
                break
            else:
                count -= 1
        return prev_post

    def next_para(self):
        count = self.get_count()
        pid = self.id
        while count > 0:
            next_post = None
            pid += 1
            if db.session.query(Paragraph).get(pid) is not None:
                next_post = db.session.query(Paragraph).get(pid)
                break
            else:
                count -= 1
        return next_post

    def get_min_qas_answer(self):
        min_qs = QASAnswers.query.filter_by(paragraph_id=self.id).order_by(QASAnswers.id).first()
        return min_qs if min_qs.id else None
    
    


class QASAnswers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    answer_start = db.Column(db.Integer, nullable=False)
    paragraph_id = db.Column(db.Integer, db.ForeignKey('paragraph.id'), nullable=False)
    qa_id = db.Column(db.String(100), nullable=False)
    check = db.Column(db.Boolean, default=None) 



   

    def __init__(self, question, answer_text, answer_start, paragraph_id,qa_id,check):
        self.question = question
        self.answer_text = answer_text 
        self.answer_start = answer_start
        self.paragraph_id = paragraph_id
        self.qa_id = qa_id
        self.check = check

    def __repr__(self):
        return str(self.id)
    

    @property
    def has_prev(self):
        return self.prev_qs is not None

    @property
    def has_next(self):
        return self.next_qs is not None


    def get_count(self, paragraph_id):
        return QASAnswers.query.filter_by(paragraph_id=paragraph_id).count()

    def prev_qs(self, paragraph_id):
        prev_qas_answer = QASAnswers.query.filter(QASAnswers.paragraph_id == paragraph_id, QASAnswers.id < self.id).order_by(QASAnswers.id.desc()).first()
        return prev_qas_answer if prev_qas_answer else None


    def next_qs(self,paragraph_id):
        next_qas_answer = QASAnswers.query.filter(QASAnswers.paragraph_id == paragraph_id, QASAnswers.id > self.id).order_by(QASAnswers.id).first()
        return next_qas_answer if next_qas_answer else None

    
    def get_max_paragraph_id():
        max_id = db.session.query(db.func.max(QASAnswers.id)).scalar()
        return max_id
    
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(200), nullable=False)




class QAversion(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String)
    qas_answer_id = db.Column(db.Integer)

 

    def __init__(self, question, qas_answer_id):
        self.question = question
        self.qas_answer_id = qas_answer_id

    def __repr__(self):
        return str(self.id)


@app.route('/restore_history')
def restore_history():
    # Lấy bản ghi đầu tiên từ bảng Para
    para_record = Paragraph.query.first()
    file = File.query.first()

    if para_record and file:
        id = para_record.id
        file_name = file.file_name
        return redirect(url_for('display', id_para=id, file_name=file_name))
    else:
        return redirect(url_for('homepage'))
    
    


def get_para(para_id = 1):
    if para_id:
        paragraph = Paragraph.query.filter(Paragraph.id == para_id).first()

    return paragraph


# def get_qas_answer(id_qs=None):
#     if id_qs:
#         qas_answer = QASAnswers.query.filter_by(id=id_qs).first()
#     return qas_answer
    
def get_title(id):
    title_record = Title.query.filter_by(id=id).first()
    
    if title_record:
        print(f"Title found: {title_record.title_text}")
        return title_record.title_text
    else:
        print("Title not found")
        return "Title not found"





@app.route('/')
def index(key_error=None): 
    
    if not path.exists("instance/data.db"):
        db.create_all()
        print("created database") 
    file_name = "Homepage"
    

    

    return render_template('index.html')





@app.route('/upload_json', methods=['POST'])
def upload_json():
    
    uploaded_file = request.files['file']
    
    file_name = uploaded_file.filename
    session['file_name'] = file_name

    print(allowed_file(uploaded_file.filename))
    File.query.delete()
    new_file = File(file_name=file_name)
    db.session.add(new_file)
    db.session.commit()
    if uploaded_file.filename != "" and allowed_file(uploaded_file.filename):
        QASAnswers.query.delete()

        # Xoá toàn bộ dữ liệu từ bảng Paragraph
        Paragraph.query.delete()

        # Xoá toàn bộ dữ liệu từ bảng Title
        Title.query.delete()

        # Commit thay đổi vào CSDL
        db.session.commit()
        try:
            json_data = json.load(uploaded_file)
            

            for i in json_data:
                title_text = i['title']
                title = Title(title_text)
                db.session.add(title)
                db.session.commit()
                paragraph_text = i['paragraphs']

                for paragraph_data in paragraph_text:
                    context = paragraph_data['context']
                    paragraph = Paragraph(context, title.id)
                    db.session.add(paragraph)
                    db.session.commit()

                    qas = paragraph_data['qas']
                    for qa in qas:
                        qa_id = qa['id']
                        question = qa['question']
                        answer_text = qa['answers'][0]['text']
                        answer_start = qa['answers'][0]['answer_start']
                        
                        if 'check' in qa:
                            check = qa['check']
                        else:
                            check = None

                        qas_answer = QASAnswers(question=question, answer_text=answer_text, 
                                                answer_start=answer_start, paragraph_id=paragraph.id,
                                                qa_id=qa_id, check=check)
                        db.session.add(qas_answer)
                        db.session.commit()
        except KeyError as e:
            key_error = "Wrong formatting, choose another file"
            return  redirect(url_for('index'))
    else:
        return  redirect(url_for('index'))
    id_para = 1

    # add_link()
    return redirect(url_for('display',id_para=id_para,file_name=file_name))  

pa = 0
qe = 0
@app.route('/<int:id_para>,<string:file_name>', methods=['GET', 'POST'])
def display(id_para, file_name):
    # Lấy đoạn văn theo id_para
    paragraph = Paragraph.query.get(id_para)
    qas_answers = paragraph.get_all_qas_answers() if paragraph else []

    print("QAS Answers:", qas_answers) 

    # Tính tổng số cột và tiêu đề
    total_columns = Paragraph.query.count()
    title = get_title(paragraph.title_id)
    current_paragraph_str = f'{id_para}/{total_columns}'
    total_ans = QASAnswers.query.count()

    return render_template(
        'index2.html',
        current_paragraph=paragraph,
        title=title,
        qas_answers=qas_answers,
        total_ans1=total_ans,
        current_paragraph_str=current_paragraph_str,
        file_name=file_name,
        
    )



@app.route('/save_qa_changes', methods=['POST'])
def save_qa_changes():
    data = request.json  

    for item in data:
        qa_id = item['id']
        check = item['check']
        
        qas_answer = QASAnswers.query.get(qa_id)
        if qas_answer:
            qas_answer.check = check
            db.session.commit()

    return jsonify({'message': 'Changes saved successfully'})


@app.route('/export_json')
def export_json():
    if QASAnswers.query.filter(QASAnswers.check.is_(None)).first():
        return jsonify({"error": "Export failed: Some QASAnswers have NULL values for 'check'."}), 400

    file_name = File.query.first().file_name
    if file_name.endswith('.json'):
        file_name_annotated = file_name[:-5] + '_validated.json'
    else:
        file_name_annotated = file_name + '_validated.json'
    titles_with_active_answers = (
        Title.query
        .join(Paragraph)
        .join(QASAnswers)
        .distinct()
        .all()
    )

    data = []

    for title in titles_with_active_answers:
        title_data = {
            "title": title.title_text,
            "paragraphs": []
        }
            
        paragraphs_with_active_answers = (
            Paragraph.query
            .join(QASAnswers)
            .filter(Paragraph.title_id == title.id)  
            .all()
        )

        for paragraph in paragraphs_with_active_answers:
            paragraph_data = {
                "context": paragraph.context,
                "qas": []
            }

            for qas_answer in paragraph.qas_answers:
                if qas_answer:


                    qas_data = {
                        "question": qas_answer.question,
                        "answers": [
                            {
                                "text": qas_answer.answer_text,
                                "answer_start": qas_answer.answer_start
                            }
                        ],
                        "id": qas_answer.qa_id,
                        "check":qas_answer.check
                    }
                    paragraph_data["qas"].append(qas_data)
            
            title_data["paragraphs"].append(paragraph_data)
        
        data.append(title_data)



    return jsonify({"files": [
                        {"file_name": file_name_annotated, "data": data},
                    ]})




import socket
from contextlib import closing

def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]



if __name__ == '__main__':
    ports = find_free_port()
    app.run(debug=True, host='0.0.0.0',port=ports)

