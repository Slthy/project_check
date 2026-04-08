def test_gs_records_view(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 10000002
        sess['role'] = 1

    mock_db.fetchall.return_value = [
        {'id': 10000008, 'name': 'Student Name', 'email': 'student@regs.edu', 'track': 'MS', 'admit_year': 2023}
    ]
    
    response = client.get('/grad_secretary/records')
    assert response.status_code == 200
    assert b"Student Name" in response.data

def test_gs_submit_override(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 10000002
        sess['role'] = 1

    response = client.post('/grad_secretary/override-grades/10', data={'grade': 'B+'}, follow_redirects=True)
    assert b"Grade updated successfully" in response.data
    assert mock_db.execute.called