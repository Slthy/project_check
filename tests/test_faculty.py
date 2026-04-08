def test_faculty_view_courses(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 10000001
        sess['role'] = 2

    mock_db.fetchall.return_value = [
        {'o_id': 1, 'dept': 'CS', 'number': '500', 'name': 'Adv CS', 'credits': 3, 'semester': 'Fall', 'year': 2024, 'day': 'W', 'start_time': '14:00', 'end_time': '16:00'}
    ]
    
    response = client.get('/faculty_instructor/courses')
    assert response.status_code == 200
    assert b"Adv CS" in response.data

def test_faculty_submit_grade_valid(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 10000001
        sess['role'] = 2

    mock_db.fetchone.return_value = {'enroll_id': 5, 'grade': 'IP'}
    
    response = client.post('/faculty_instructor/submit_grade/5', data={'grade': 'A'}, follow_redirects=True)
    assert b"Grade submitted successfully" in response.data

    update_call = mock_db.execute.call_args_list[1]
    assert 'UPDATE enrollment SET grade' in update_call[0][0]

def test_faculty_submit_grade_invalid(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 10000001
        sess['role'] = 2

    response = client.post('/faculty_instructor/submit_grade/5', data={'grade': 'Z'}, follow_redirects=True)
    assert b"Invalid grade selected" in response.data