from app import app, db, Major, Dormitory, Bed, Student

# 在应用上下文中运行
with app.app_context():
    # 删除所有表
    db.drop_all()
    
    # 创建所有表
    db.create_all()

    # 添加完整的60个专业数据
    majors = [
        {'name': '计算机科学与技术', 'code': '01'},
        {'name': '软件工程', 'code': '02'},
        {'name': '人工智能', 'code': '03'},
        {'name': '数据科学', 'code': '04'},
        {'name': '网络工程', 'code': '05'},
        {'name': '信息安全', 'code': '06'},
        {'name': '物联网工程', 'code': '07'},
        {'name': '数字媒体技术', 'code': '08'},
        {'name': '智能科学与技术', 'code': '09'},
        {'name': '电子与计算机工程', 'code': '10'},
        {'name': '机械工程', 'code': '11'},
        {'name': '土木工程', 'code': '12'},
        {'name': '化学工程与工艺', 'code': '13'},
        {'name': '环境工程', 'code': '14'},
        {'name': '电气工程及其自动化', 'code': '15'},
        {'name': '自动化', 'code': '16'},
        {'name': '通信工程', 'code': '17'},
        {'name': '生物医学工程', 'code': '18'},
        {'name': '材料科学与工程', 'code': '19'},
        {'name': '数学与应用数学', 'code': '20'},
        {'name': '物理学', 'code': '21'},
        {'name': '化学', 'code': '22'},
        {'name': '生物科学', 'code': '23'},
        {'name': '经济学', 'code': '24'},
        {'name': '金融学', 'code': '25'},
        {'name': '国际经济与贸易', 'code': '26'},
        {'name': '法学', 'code': '27'},
        {'name': '社会学', 'code': '28'},
        {'name': '汉语言文学', 'code': '29'},
        {'name': '英语', 'code': '30'},
        {'name': '日语', 'code': '31'},
        {'name': '新闻学', 'code': '32'},
        {'name': '广告学', 'code': '33'},
        {'name': '历史学', 'code': '34'},
        {'name': '哲学', 'code': '35'},
        {'name': '教育学', 'code': '36'},
        {'name': '心理学', 'code': '37'},
        {'name': '学前教育', 'code': '38'},
        {'name': '小学教育', 'code': '39'},
        {'name': '体育教育', 'code': '40'},
        {'name': '音乐学', 'code': '41'},
        {'name': '美术学', 'code': '42'},
        {'name': '设计学类', 'code': '43'},
        {'name': '临床医学', 'code': '44'},
        {'name': '口腔医学', 'code': '45'},
        {'name': '护理学', 'code': '46'},
        {'name': '药学', 'code': '47'},
        {'name': '中医学', 'code': '48'},
        {'name': '中药学', 'code': '49'},
        {'name': '管理科学', 'code': '50'},
        {'name': '工商管理', 'code': '51'},
        {'name': '市场营销', 'code': '52'},
        {'name': '会计学', 'code': '53'},
        {'name': '财务管理', 'code': '54'},
        {'name': '人力资源管理', 'code': '55'},
        {'name': '旅游管理', 'code': '56'},
        {'name': '电子商务', 'code': '57'},
        {'name': '物流管理', 'code': '58'},
        {'name': '公共事业管理', 'code': '59'},
        {'name': '行政管理', 'code': '60'}
    ]

    for major_data in majors:
        major = Major(name=major_data['name'], code=major_data['code'])
        db.session.add(major)

    # 添加宿舍数据
    dormitories = []
    
    # 男生宿舍 A-M
    for building in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']:
        # 1-3层：4人间
        for floor in range(1, 4):
            for room in range(1, 9):
                dormitories.append({
                    'building': f'{building}栋',
                    'room_number': floor * 100 + room,
                    'capacity': 4,
                    'gender': '男'
                })
        
        # 4-5层：6人间
        for floor in range(4, 6):
            for room in range(1, 9):
                dormitories.append({
                    'building': f'{building}栋',
                    'room_number': floor * 100 + room,
                    'capacity': 6,
                    'gender': '男'
                })
        
        # 6层：8人间
        for room in range(1, 9):
            dormitories.append({
                'building': f'{building}栋',
                'room_number': 600 + room,
                'capacity': 8,
                'gender': '男'
            })
    
    # 女生宿舍 N-Z
    for building in ['N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
        # 1-3层：4人间
        for floor in range(1, 4):
            for room in range(1, 9):
                dormitories.append({
                    'building': f'{building}栋',
                    'room_number': floor * 100 + room,
                    'capacity': 4,
                    'gender': '女'
                })
        
        # 4-5层：6人间
        for floor in range(4, 6):
            for room in range(1, 9):
                dormitories.append({
                    'building': f'{building}栋',
                    'room_number': floor * 100 + room,
                    'capacity': 6,
                    'gender': '女'
                })
        
        # 6层：8人间
        for room in range(1, 9):
            dormitories.append({
                'building': f'{building}栋',
                'room_number': 600 + room,
                'capacity': 8,
                'gender': '女'
            })

    for dorm_data in dormitories:
        dorm = Dormitory(**dorm_data)
        db.session.add(dorm)
        db.session.flush()  # 获取 dorm.id
        
        # 为每个宿舍创建床位
        for bed_number in range(1, dorm_data['capacity'] + 1):
            bed = Bed(
                bed_number=bed_number,
                dorm_id=dorm.id,
                status='空闲'
            )
            db.session.add(bed)

    # 提交所有更改
    db.session.commit()

    print("数据库初始化完成！")