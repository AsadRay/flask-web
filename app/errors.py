from flask import render_template, request
from flask_mail import Message
from app import app, db, mail

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()

    # Send email manually
    msg = Message("Microblog Application Error",
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[app.config['ADMIN_EMAIL']])
    msg.body = f"""
500 Internal Server Error

URL: {request.url}
Error: {error}
User Agent: {request.user_agent}
    """
    try:
        mail.send(msg)
    except Exception as e:
        app.logger.error(f"Failed to send error email: {e}")

    return render_template('500.html'), 500
