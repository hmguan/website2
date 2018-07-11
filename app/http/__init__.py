from flask import Blueprint
http_main=Blueprint('http_main',__name__)
from . import httpview