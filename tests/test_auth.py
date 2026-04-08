import bcrypt

def test_login_page_loads(client):
    response = client.get('/auth/login')
    assert response.status_code == 200

def test_successful_login(client, mock_db):
    mock_db.fetchone.return_value = {
        'id': 10000008,
        'email': 'student@regs.edu',
        'password': bcrypt.hashpw(b"password123", bcrypt.gensalt()),
        'role': 3,
        'fname': 'Test'
    }
    response = client.post('/auth/login', data={'email': 'student@regs.edu', 'password': 'password123'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/'

def test_failed_login(client, mock_db):
    mock_db.fetchone.return_value = None
    response = client.post('/auth/login', data={'email': 'nobody@regs.edu', 'password': 'wrongpassword'})
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data

def test_logout(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 10000008
        sess['email'] = 'student@regs.edu'
    
    response = client.get('/auth/logout')
    assert response.status_code == 302
    assert response.headers['Location'] == '/auth/login'
    
    with client.session_transaction() as sess:
        assert 'user_id' not in sess

def test_registration_existing_email(client, mock_db):
    mock_db.fetchone.return_value = {'id': 12345} # Simulates email already exists
    response = client.post('/auth/register', data={
        'fname': 'John', 'lname': 'Doe', 'mname': '',
        'email': 'existing@regs.edu', 'password': 'password123',
        'track': 'MS', 'admit_year': '2023', 'line_one': '123 St',
        'city': 'City', 'state': 'ST', 'zip': '12345', 'country_code': 'US'
    })
    assert b"Email already exists" in response.data