import os as __os
from App.settings import ROOT_DIR

APP_ID = '90f5a57a-37f1-4551-8a8b-c6d93701ab62'

SECRET_KEY_BYTES = b"_test__sEcReT__KEY__wvngSV2xB4lmmWxkq8dsgMk="

DB_CONNECTION = {}

DEBUG = True

PASSFILES_FOLDER = __os.path.join(ROOT_DIR, 'Data', 'TestPassFiles')
