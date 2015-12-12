from social.backends.instagram import InstagramOAuth2


# Temporary fix
# Override default backend ACCESS_TOKEN_URL, original ACCESS_TOKEN_URL not working now
class InstagramOAuth2Override(InstagramOAuth2):
    ACCESS_TOKEN_URL = 'https://api.instagram.com/oauth/access_token'
