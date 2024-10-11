import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Load Firebase credentials from environment variable
firebase_credentials_json = os.getenv('FIREBASE_CREDENTIALS')
# firebase_credentials={
#   "type": "service_account",
#   "project_id": "grievence-system",
#   "private_key_id": "57a880e2167c56558709c46ece5949c4421fcfa2",
#   "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCxiELYGEn37aj9\nbcMUifrxeY6C00VVCxdC+JRRtLS4ch4lxNNOo4URdUSFFNAsgakq9Jybw3jZyblv\nvVuqBNX4j8Z19OiSGDb3+DBDozQgg043KHJF0t8/3jRbO2ziLdwGpCEUFxsB/zyz\n5MUiDQt525uxNJ8Y1UP/KOLUNIHXa5oJoRx9Ub3vZEcwplr/Rlmqh/G7huta9Dl4\nMIQrDkWDRgXnTcjLr5sG1EzRgga/sceVgGp8xr4TVWYZuNYEoPq2Wm7Jho1j5v/z\niunaBQctx1HFfF6MbsrROSbe+2Z12dRv7sYAdNHipOWeBZ9dtjfD67CnXz7dL32h\nIneYA1QJAgMBAAECggEADUNAuyQVYpA+r7AjgsVMGf4ax2tBIrlRY49uhSwa1Cyy\nU+AAaT+OEV/RXp/PbYPCP5NGn9xaiuqnD9H1px31XjxfdzB0r3VfpebEtEjc/BDT\nJwu+fbjjNMJE5wvpdnw2k8hvMDEJs3x97HKKx6Bx2wis+PAVcqV8DvPe/jtt98nS\nDtDz10/uXOQpO+xuB7KgYSbu7DPaV9pfwFQe1qGQfJPOSTkWj4U+h7iHnnJYzlWm\nw1XzeEUg19GpexPsc5lyuIaEr3pMgJ1CKtj1ZjETpKHH3nXrG8qCPBJ83O20HgCw\n4rwrR6QwCcLP/LrPF+4H/15Ql6mlHemfhvxchZEQAQKBgQDtVA16YILWoSA55n8B\nk3kM3vQmdXH7fspjWaEmrwmFYaUJAPEhy8eJRAFeecK9FZEroHKOeo5kN1ze6Zdn\nmEVV6IxNir2bTT33a2tJyT7kVkpxRizOCjWWIbvEE9IuXw5otXWthCv/N0KMTnsW\nXeCtlbRe2FnvB4tbQXLHLOHQ2QKBgQC/f+B2LVfPNd9W5/mnAlsZkKIDKX4BpzX8\n4UkiXDTmtlHHg0HkdUADso8zanfMI4Pl8eEp59X9/iP2oF7yNoHMBV/YJb1xhJTP\nOBCNtGjCVYfviyOPlSvsZMkMp3ikPDC1K5F1/E/zZ3htab91nUP5lZ/lkxY2V2FX\nDD26W1yesQKBgATkca6vJKNWCPsIlF+s8ZbhVbkhPKtJjtSDeX35p8GXJLbNzSq8\nL63VuA2BhxEsy6RRl2r2fc71ETYLLLLXAb7mn1XN4WC9M+TQ0xJfUquUV86D+tJ4\nhWhF48AEBJYuIXbpHrbn/ZwyQG3yBDmOz93kMyatYRU7W5UTAVG3zCPpAoGAczq0\nSwgPvVySTk352De/r4trIXH3I3GFN+wrwKQxJN5yKRZfMOQop9DrACpBebGpLVU1\ngqzBBDvHUiC/4QlRYv2c5YgYDVWU4Xe/5jS3kLA8wrQ7qqs9Kdqfa6DeJB0fxfQ4\nbAFt7m3FdjjafyApheY1t8Og6wP7S5DPF/LfsZECgYBtDcLwUZ1b3GMz848Rw2jy\nNwXhWTxL4N6RDv1Fc8WIsuzbqpsuJ8sdz8jDpQZT2MWijAxPSfZ6dqIoyUhCUMAT\nR1DXnj99ABdZyTaMx5IUR/QTLlXRp0cCOvZ+GxZG9ocwyOmwIyxr9cJtdVEOTimc\nORlEi1IhpgdU75ej6+h4Kw==\n-----END PRIVATE KEY-----\n",
#   "client_email": "firebase-adminsdk-f0yue@grievence-system.iam.gserviceaccount.com",
#   "client_id": "113653777798595111266",
#   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#   "token_uri": "https://oauth2.googleapis.com/token",
#   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#   "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-f0yue%40grievence-system.iam.gserviceaccount.com",
#   "universe_domain": "googleapis.com"
# }
# firebase_credentials_json=json.dumps(firebase_credentials)
if not firebase_credentials_json:
    raise Exception("FIREBASE_CREDENTIALS environment variable not set")

# Parse the credentials from the environment variable
cred_dict = json.loads(firebase_credentials_json)

# Initialize Firebase using the in-memory credentials
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()
