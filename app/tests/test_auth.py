import bcrypt

def test_login_page_loads(client):
    """Ensure the login page HTML loads successfully."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b"email" in response.data.lower()

def test_successful_login(client, mock_db):
    """Test that providing correct credentials logs the user in."""

    mock_db.fetchone.return_value = {
        'id': 10000008,
        'email': 'student@regs.edu',
        'password': bcrypt.hashpw(b"password123", bcrypt.gensalt()),
        'role': 3,
        'fname': 'Test'
    }
    
    response = client.post('/auth/login', data={
        'email': 'student@regs.edu',
        'password': 'password123'
    })
    
    assert response.status_code == 302
    assert response.headers['Location'] == '/'

def test_failed_login(client, mock_db):
    """Test that bad credentials keep you on the login page."""

    mock_db.fetchone.return_value = None
    
    response = client.post('/auth/login', data={
        'email': 'nobody@regs.edu',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 200