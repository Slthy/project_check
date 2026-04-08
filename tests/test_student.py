def test_student_index_loads(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 10000008
        sess['role'] = 3

    mock_db.fetchall.side_effect = [
        [],  # current_schedule
        [],  # completed_cids
        [{'o_id': 1, 'c_id': 101, 'semester': 'Fall', 'year': 2024, 'dept': 'CS', 'number': '101', 'name': 'Intro', 'credits': 3, 'prereq1_id': None, 'prereq2_id': None, 'instructor': 'Dr. Smith', 'day': 'M', 'start_time': '10:00', 'end_time': '11:00'}],  # offerings
        []   # current_courses
    ]
    
    response = client.get('/student/')
    assert response.status_code == 200
    assert b"Intro" in response.data

def test_student_add_course_conflict(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 10000008
        sess['role'] = 3

    mock_db.fetchall.side_effect = [
        [{'day': 'M', 'start_time': '10:00:00', 'end_time': '11:00:00'}], # current schedule
        [], # completed_cids
        [{'day': 'M', 'start_time': '10:30:00', 'end_time': '11:30:00'}] # new_course_times
    ]
    mock_db.fetchone.side_effect = [
        {'c_id': 102}, # course_info
        {'prereq1_id': None, 'prereq2_id': None} # prereqs
    ]

    response = client.post('/student/add_course/2', follow_redirects=False)

    assert response.status_code == 302 
    assert response.headers['Location'] == '/student/'
    
    with client.session_transaction() as sess:
        flashes = dict(sess['_flashes'])
        assert "Time conflict" in flashes.get('error', '')

def test_student_drop_course(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 10000008
        sess['role'] = 3

    mock_db.rowcount = 1
    response = client.post('/student/drop_course/1', follow_redirects=True)
    
    assert mock_db.execute.called
    assert b"Course successfully dropped" in response.data