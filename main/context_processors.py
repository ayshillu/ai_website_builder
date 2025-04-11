def user_context(request):
    """
    Add user information to all templates context.
    """
    return {
        'is_authenticated': 'auth_token' in request.session,
        'user_email': request.session.get('user_email', None),
    } 