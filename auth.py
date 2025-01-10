from jose import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer
from auth0.authentication import GetToken
from auth0.management import Auth0
import os
import requests
from dotenv import load_dotenv

load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_IDENTIFIER = os.getenv("API_IDENTIFIER")
AUTH0_MANAGEMENT_API_TOKEN = os.getenv("AUTH0_MANAGEMENT_API_TOKEN")
ALGORITHMS = ["RS256"]

http_bearer = HTTPBearer()

def get_auth0_client():
    return Auth0(AUTH0_DOMAIN, AUTH0_MANAGEMENT_API_TOKEN)

def verify_jwt(token: str):
    try:
        header = jwt.get_unverified_header(token)
        rsa_key = get_rsa_key(header)
        payload = jwt.decode(token, rsa_key, algorithms=ALGORITHMS, audience=API_IDENTIFIER, issuer=f"https://{AUTH0_DOMAIN}/")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTClaimsError:
        raise HTTPException(status_code=401, detail="Invalid claims")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_rsa_key(header):
    jwks = requests.get(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json").json()
    for key in jwks["keys"]:
        if key["kid"] == header["kid"]:
            return {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    raise HTTPException(status_code=401, detail="Invalid header")