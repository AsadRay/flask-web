from flask import render_template, request, current_app
from flask_mail import Message
from app import db, mail
from app.errors import bp  # import the errors blueprint


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()

    # Send email manually
    msg = Message("CHITCHAT Application Error",
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[current_app.config['ADMIN_EMAIL']])
    msg.body = f"""
500 Internal Server Error

URL: {request.url}
Error: {error}
User Agent: {request.user_agent}
    """
    try:
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Failed to send error email: {e}")

    return render_template('errors/500.html'), 500
