from app import db
from app.api import bp
from app.api.auth import basic_auth

@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    if user is None:
        return {'error': 'Authentication failed'}, 401
    token = user.get_token()
    db.session.commit()
    return {'token': token}
    