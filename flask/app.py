from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 供前端展示的爱好列表（checkbox）
hobbies_list = ["健身运动", "摄影", "打游戏"]

# 修改数据库配置
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'bysj.db')
db = SQLAlchemy(app)

class Major(db.Model):
    __tablename__ = 'majors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(10), nullable=False)

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.String(10), primary_key=True)
    id_card = db.Column(db.String(18), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    schedule = db.Column(db.String(50), nullable=False)
    major_id = db.Column(db.Integer, db.ForeignKey('majors.id'), nullable=False)
    accept_other_major = db.Column(db.Boolean, nullable=False)
    bed_pref = db.Column(db.String(50), nullable=False)
    dorm_size = db.Column(db.Integer, nullable=False)
    hobbies = db.Column(db.String(255), nullable=False)
    dorm_id = db.Column(db.Integer, db.ForeignKey('dormitories.id'))

    # 添加关系
    major = db.relationship('Major', backref=db.backref('students', lazy=True))
    dorm = db.relationship('Dormitory', backref=db.backref('students', lazy=True))

class Dormitory(db.Model):
    __tablename__ = 'dormitories'
    id = db.Column(db.Integer, primary_key=True)
    building = db.Column(db.String(50), nullable=False)
    room_number = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)

    @property
    def occupied_beds(self):
        return len([bed for bed in self.beds if bed.student_id is not None])

class Bed(db.Model):
    __tablename__ = 'beds'
    id = db.Column(db.Integer, primary_key=True)
    bed_number = db.Column(db.Integer, nullable=False)
    dorm_id = db.Column(db.Integer, db.ForeignKey('dormitories.id'), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    student_id = db.Column(db.String(10), db.ForeignKey('students.student_id'), nullable=True)

    # 添加关系
    student = db.relationship('Student', backref=db.backref('bed', uselist=False))
    dorm = db.relationship('Dormitory', backref=db.backref('beds', lazy=True))

def get_db():
    """获取一个带有 Row 工厂的 SQLite 连接"""
    db_path = os.path.join(basedir, 'app.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        id_card = request.form['id_card']
        gender = request.form['gender']
        major_id = request.form['major']
        schedule = request.form['schedule']
        dorm_size = request.form['dorm_size']
        bed_pref = request.form['bed_pref']
        accept_other_major = 'accept_other_major' in request.form
        hobbies = request.form.getlist('hobby')

        # 生成学号（年份+专业代码+4位序号）
        year = datetime.now().year
        major = Major.query.get(major_id)
        last_student = Student.query.filter(
            Student.student_id.like(f'{year}{major.code}%')
        ).order_by(Student.student_id.desc()).first()

        if last_student:
            last_number = int(last_student.student_id[-4:])
            new_number = str(last_number + 1).zfill(4)
        else:
            new_number = '0001'

        student_id = f'{year}{major.code}{new_number}'

        # 创建新学生
        student = Student(
            student_id=student_id,
            name=name,
            id_card=id_card,
            gender=gender,
            major_id=major_id,
            schedule=schedule,
            dorm_size=dorm_size,
            bed_pref=bed_pref,
            accept_other_major=accept_other_major,
            hobbies=','.join(hobbies)
        )

        db.session.add(student)
        db.session.commit()

        flash(f'注册成功！您的学号是：{student_id}，请记住此学号用于登录。', 'success')
        return redirect(url_for('login'))

    majors = Major.query.all()
    return render_template('register.html', majors=majors, hobbies_list=hobbies_list)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        sid = request.form.get('student_id', '').strip()
        student = Student.query.filter_by(student_id=sid).first()
        if student:
            return redirect(url_for('profile', student_id=sid))
        flash('未找到该学号，请先注册。')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/profile/<student_id>')
def profile(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        flash('未找到该学号，请先登录。')
        return redirect(url_for('login'))
    
    # 获取专业信息
    major = Major.query.get(student.major_id)
    student.major_name = major.name if major else None
    
    # 获取宿舍信息
    if student.dorm_id:
        dorm = Dormitory.query.get(student.dorm_id)
        if dorm:
            student.building = dorm.building
            student.room_number = dorm.room_number
            student.dorm_capacity = dorm.capacity
    
    return render_template('profile.html', student=student)


@app.route('/assign_dorm/<student_id>', methods=['GET', 'POST'])
def assign_dorm(student_id):
    if request.method == 'POST':
        # 获取学生信息
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            flash('学生不存在', 'error')
            return redirect(url_for('index'))
            
        # 获取学生性别
        gender = student.gender
        
        # 获取该性别下所有可用的宿舍
        dorms = Dormitory.query.filter_by(gender=gender).all()
        if not dorms:
            flash('没有可用的宿舍', 'error')
            return redirect(url_for('profile', student_id=student_id))
            
        # 选择第一个可用的宿舍
        dorm = dorms[0]
        
        # 找到该宿舍的第一个空闲床位
        bed = Bed.query.filter_by(dorm_id=dorm.id, student_id=None).first()
        if not bed:
            flash('该宿舍已满', 'error')
            return redirect(url_for('profile', student_id=student_id))
            
        # 更新床位和学生信息
        bed.student_id = student.student_id
        bed.status = '已占用'
        student.dorm_id = dorm.id
        
        db.session.commit()
        
        flash('宿舍分配成功', 'success')
        return redirect(url_for('profile', student_id=student_id))
        
    # GET 请求处理
    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        flash('学生不存在', 'error')
        return redirect(url_for('index'))
    
    # 获取专业信息
    major = Major.query.get(student.major_id)
    student.major_name = major.name if major else None
    
    # 获取宿舍信息
    if student.dorm_id:
        dorm = Dormitory.query.get(student.dorm_id)
        if dorm:
            student.building = dorm.building
            student.room_number = dorm.room_number
            student.dorm_capacity = dorm.capacity
        
    return render_template('profile.html', student=student)


@app.route('/dorm_status')
def dorm_status():
    # 获取筛选参数
    building = request.args.get('building', '')
    capacity = request.args.get('capacity', '')
    gender = request.args.get('gender', '')
    occupancy = request.args.get('occupancy', '')
    
    # 构建查询
    query = Dormitory.query
    
    # 应用筛选条件
    if building:
        query = query.filter(Dormitory.building.like(f'%{building}%'))
    if capacity:
        query = query.filter(Dormitory.capacity == int(capacity))
    if gender:
        query = query.filter(Dormitory.gender == gender)
    
    # 获取所有宿舍信息
    dorms = query.all()
    dorm_details = []
    
    for dorm in dorms:
        # 获取该宿舍的所有床位信息
        beds = Bed.query.filter_by(dorm_id=dorm.id).all()
        bed_details = []
        
        for bed in beds:
            student = None
            if bed.student_id:
                student = Student.query.filter_by(student_id=bed.student_id).first()
            
            bed_detail = {
                'bed_number': bed.bed_number,
                'student_name': student.name if student else None,
                'major_name': student.major.name if student and student.major else None
            }
            bed_details.append(bed_detail)
        
        # 计算入住率
        occupancy_rate = dorm.occupied_beds / dorm.capacity * 100
        
        # 根据入住率筛选
        if occupancy:
            if occupancy == 'empty' and occupancy_rate > 0:
                continue
            elif occupancy == 'partial' and (occupancy_rate == 0 or occupancy_rate == 100):
                continue
            elif occupancy == 'full' and occupancy_rate < 100:
                continue
        
        dorm_detail = {
            'dorm': dorm,
            'beds': bed_details,
            'occupancy_rate': occupancy_rate
        }
        dorm_details.append(dorm_detail)
    
    # 获取所有可用的筛选选项
    buildings = db.session.query(Dormitory.building).distinct().all()
    buildings = [b[0] for b in buildings]
    
    capacities = db.session.query(Dormitory.capacity).distinct().all()
    capacities = [c[0] for c in capacities]
    
    return render_template('dorm_status.html', 
                         dorm_details=dorm_details,
                         buildings=buildings,
                         capacities=capacities,
                         current_building=building,
                         current_capacity=capacity,
                         current_gender=gender,
                         current_occupancy=occupancy)

@app.route('/student_status/<student_id>')
def student_status(student_id):
    # 使用 SQLAlchemy 查询替代原生 SQL
    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        flash('未找到该学生信息')
        return redirect(url_for('index'))
    
    # 获取专业信息
    major = Major.query.get(student.major_id)
    student.major_name = major.name if major else None
    
    # 获取宿舍信息
    if student.dorm_id:
        dorm = Dormitory.query.get(student.dorm_id)
        if dorm:
            student.building = dorm.building
            student.room_number = dorm.room_number
            student.dorm_capacity = dorm.capacity
            
            # 获取床位信息
            bed = Bed.query.filter_by(student_id=student_id).first()
            if bed:
                student.bed_number = bed.bed_number
    
    # 获取同宿舍的其他学生信息
    roommates = []
    if student.dorm_id:
        roommates = Student.query.filter(
            Student.dorm_id == student.dorm_id,
            Student.student_id != student_id
        ).all()
        
        # 获取室友的专业和床位信息
        for roommate in roommates:
            major = Major.query.get(roommate.major_id)
            roommate.major_name = major.name if major else None
            
            bed = Bed.query.filter_by(student_id=roommate.student_id).first()
            if bed:
                roommate.bed_number = bed.bed_number
    
    return render_template('student_status.html', student=student, roommates=roommates)

@app.route('/search_student', methods=['POST'])
def search_student():
    student_id = request.form.get('student_id')
    if not student_id:
        flash('请输入学号')
        return redirect(url_for('index'))
    return redirect(url_for('student_status', student_id=student_id))

if __name__ == '__main__':
    app.run(debug=True)
