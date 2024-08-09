from flask import Flask, render_template, request,redirect, url_for, jsonify, session 
from flask_sqlalchemy import SQLAlchemy
from bert_QA import *

from os import path
import json

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PAGE_SIZE'] = 1
app.config['SECRET_KEY'] = 'KL-2024'


ALLOWED_EXTENSIONS = set(["json"])

tokenizer, model = init()

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
    question = db.Column(db.String)
    answer_text = db.Column(db.String)
    answer_start = db.Column(db.Integer)
    paragraph_id = db.Column(db.Integer, db.ForeignKey('paragraph.id'))
    active = db.Column(db.Integer, default=0)  # Thêm cột mới "active" với giá trị mặc định là 0
    fake_id = db.Column(db.String)  # Thêm cột mới "active" với giá trị mặc định là 0
    def __init__(self, question, answer_text, answer_start, paragraph_id):
        self.question = question
        self.answer_text = answer_text 
        self.answer_start = answer_start
        self.paragraph_id = paragraph_id
        self.fake_id = ""

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




class QAversion(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String)
    qas_answer_id = db.Column(db.Integer)

 

    def __init__(self, question, qas_answer_id):
        self.question = question
        self.qas_answer_id = qas_answer_id

    def __repr__(self):
        return str(self.id)





def get_para(para_id = 1):


    if para_id:
        paragraph = Paragraph.query.filter(Paragraph.id == para_id).first()

    return paragraph


def get_qas_answer(id_qs=None):
    if id_qs:
        qas_answer = QASAnswers.query.filter_by(id=id_qs).first()
    return qas_answer
    
def get_title(para_id):
    tittle = Title.query.filter()



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
                        question = qa['question']
                        answer_text = qa['answers'][0]['text']
                        answer_start = qa['answers'][0]['answer_start']
                        qas_answer = QASAnswers(question, answer_text, answer_start, paragraph.id)
                        db.session.add(qas_answer)
                        db.session.commit()
        except KeyError as e:
            key_error = "Wrong formatting, choose another file"
            return  redirect(url_for('index'))
    else:
        return  redirect(url_for('index'))
    id_para = 1
    id_qs =1          

    return redirect(url_for('display',id_para=id_para,file_name=file_name,id_qs=id_qs))  

pa = 0
qe = 0
@app.route('/upload_json/<int:id_para>,<string:file_name>,<int:id_qs>')
def display(id_para, file_name, id_qs):

    


    current_paragraph = get_para(id_para)
    if id_qs:
        qas_answer = get_qas_answer(id_qs)
    else:
        qas_answer = QASAnswers.query.filter(id_para == QASAnswers.paragraph_id, QASAnswers.id < qas_answer.id).order_by(QASAnswers.id.desc()).first()
    # total_ans = int(QASAnswers.query.count() )+1
    total_columns = Paragraph.query.count()
    title_id = current_paragraph.title_id
    pa = id_para
    qe = id_qs
    current_paragraph_str = f'{id_para}/{total_columns}'
    title = db.session.query(Title).get(title_id)

    a = QASAnswers.query.filter(id_para == QASAnswers.paragraph_id, QASAnswers.id < qas_answer.id).order_by(QASAnswers.id.desc()).first()
    question = request.args.get('question')
    # ans_start = request.args.get('ans_start')

    if question is not None:
        predicted_answer = predict_answer(model, tokenizer,question,current_paragraph.context)
        
    else:
        predicted_answer = predict_answer(model, tokenizer,qas_answer.question,current_paragraph.context)
    answer = request.args.get('selected_text')
    if answer is not None:
        F1 = round(calculate_f1(predicted_answer, answer),2)
    else:
        F1 = round(calculate_f1(predicted_answer, qas_answer.answer_text),2)
    
    # if request.args.get('file_name') is not None:
    #     file_name = request.args.get('file_name')
    total_ans = QASAnswers.query.count()
    total_ans1 = QASAnswers.query.filter_by(active=1).count()


    return render_template('index2.html', current_paragraph=current_paragraph, file_name=file_name, title=title, qas_answer=qas_answer,question=question, current_paragraph_str=current_paragraph_str, noofQuestion=noofQuestion,total_ans=total_ans,predicted_answer=predicted_answer,F1=F1,answer=answer,total_ans1 =total_ans1)


@app.route('/predict_answer', methods=['PUT'])
def predict():
    data = request.json
    question = data.get('question')
    id_para = data.get('id_para')
    id_qs = data.get('id_qs')
    answer = data.get('answer')
    # file_name = str(data.get('file_name'))
    file_name = session.get('file_name')
    # ans_start = data.get('start_offset')
    original_question =  get_qas_answer(id_qs).question
    
    if question != original_question:
        new_qa_version = QAversion(question=question, qas_answer_id=id_qs)
        db.session.add(new_qa_version)
        db.session.commit()


    redirect_url = url_for('display', id_para=id_para, file_name=file_name, id_qs=id_qs, question=question,answer=answer)

    # Trả về một phản hồi JSON chứa đường dẫn mới để chuyển hướng
    return jsonify({'redirect_url': redirect_url})

@app.route('/send_selected_text', methods=['POST'])
def send_ans():
    data = request.json
    selected_text = data.get('selected_text')
    id_para = data.get('id_para')
    id_qs = data.get('id_qs')
    
    # file_name = data.get('file_name')
    # file_name = str(data.get('file_name'))
    question = data.get('question')
    file_name = session.get('file_name')
    ans_start = data.get('start_offset')
    
    redirect_url = url_for('display', id_para=id_para, file_name=file_name, id_qs=id_qs, selected_text=selected_text,question=question)

    # Trả về một phản hồi JSON chứa đường dẫn mới để chuyển hướng
    return jsonify({'redirect_url': redirect_url})

from flask import request

@app.route('/save_qa_changes', methods=['POST'])
def save_qa_changes():
    # Lấy dữ liệu từ request
    data = request.json
    
    question = data.get('question')
    answer = data.get('answer')
    qa_id = data.get('qa_id')
    ans_start = data.get('startOffset')
    fake_id = data.get('fake_id')
    # Tìm câu hỏi và câu trả lời cần chỉnh sửa
    qas_answer = QASAnswers.query.get(qa_id)
    # para = Paragraph.query.get(qas_answer.paragraph_id)
    # print(para.context)
    # answer_start = sentence_position(answer,para.context)
    # print("123")
    print(fake_id)

    if qas_answer:
        # Cập nhật câu hỏi và câu trả lời
        if question is not None:
            qas_answer.question = question
        qas_answer.answer_text = answer
        qas_answer.active = 1  # Đánh dấu là đã chỉnh sửa
        qas_answer.answer_start = ans_start
        qas_answer.fake_id = fake_id
        # Lưu thay đổi vào cơ sở dữ liệu
        db.session.commit()




       



        # Trả về một phản hồi JSON để xác nhận rằng thay đổi đã được lưu
        return jsonify({'message': 'Changes saved successfully.'}), 200
    else:
        # Trả về một phản hồi JSON báo lỗi nếu không tìm thấy câu hỏi và câu trả lời
        return jsonify({'message': 'QASAnswer not found.'}), 404

@app.route('/export_json')
def export_json():
    file_name = session.get('file_name')
    file_name_annotated = file_name.split(".json")[0] + '_annotated.json' 

    titles_with_active_answers = (
        Title.query
        .join(Paragraph)
        .join(QASAnswers)
        .filter(QASAnswers.active == 1)
        .distinct()  # Đảm bảo chỉ lấy các tiêu đề duy nhất
        .all()
    )

    data = []
    evaluate_data = []

    for title in titles_with_active_answers:
        title_data = {
            "title": title.title_text,
            "paragraphs": []
        }
        paragraphs_with_active_answers = Paragraph.query.join(QASAnswers).filter(QASAnswers.active == 1).all()

        for paragraph in paragraphs_with_active_answers:
            paragraph_data = {
                "context": paragraph.context,
                "qas": []
            }

            for qas_answer in paragraph.qas_answers:
                if qas_answer.active == 1:
                    wrong_objects = QAversion.query.filter(QAversion.qas_answer_id == qas_answer.id).all()
                    blank_qs = []
                    
                    for ob in wrong_objects:
                        blank_qs.append({"question": ob.question})
                    
                    evaluate_data.append({"id": qas_answer.fake_id, "qs": blank_qs})

                    qas_data = {
                        "question": qas_answer.question,
                        "answers": [
                            {
                                "text": qas_answer.answer_text,
                                "answer_start": qas_answer.answer_start
                            }
                        ],
                        "id": qas_answer.fake_id
                    }
                    paragraph_data["qas"].append(qas_data)
            
            title_data["paragraphs"].append(paragraph_data)
        
        data.append(title_data)
        
    evaluate_dataname = file_name.split(".json")[0] + "_evaluate.json"
    
    return jsonify({"files": [
                        {"file_name": file_name_annotated, "data": data},
                        {"file_name": evaluate_dataname, "data": evaluate_data}
                    ]})


@app.route('/create_answer/<int:id_para>,<string:file_name>,<int:id_qs>')
def display2(id_para, file_name, id_qs):
    new_qas_answer = QASAnswers(question="", answer_text="", answer_start="", paragraph_id=id_para)
    db.session.add(new_qas_answer)
    db.session.commit()
    return redirect(url_for('display',id_para=id_para,file_name=file_name,id_qs=id_qs))


if __name__ == '__main__':

    app.run(debug=True)

