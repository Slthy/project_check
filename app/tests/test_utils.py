def test_student_blocked_from_admin_panel(client):
    """A logged-in student should NOT be able to access the admin portal."""
    
    with client.session_transaction() as session:
        session['user_id'] = 88888888
        session['role'] = 3
        session['email'] = 'student@regs.edu'

    assert client.get('/system_admin/').status_code in [302, 403]

def test_guest_blocked_from_home(client):
    """An unauthenticated user should be redirected to login."""
    
    response = client.get('/')

    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']