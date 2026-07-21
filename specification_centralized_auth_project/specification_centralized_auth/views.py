from django.http import JsonResponse
from django.conf import settings
from jose import jwk
import os

# Create your views here.

def jwks(request):
    """
    Provides the JSON Web Key Set (JWKS) for verifying JWTs.
    """
    # Construct the path to the public key file
    key_path = os.path.join(settings.BASE_DIR, 'public_key.pem')

    with open(key_path, 'rb') as f:
        public_key = f.read()

    # Convert the PEM public key to a JWK
    key = jwk.construct(public_key, algorithm='RS256')
    jwk_dict = key.to_dict()
    jwk_dict['kid'] = '1' # Key ID
    jwk_dict['use'] = 'sig' # Usage: signature

    return JsonResponse({'keys': [jwk_dict]})
