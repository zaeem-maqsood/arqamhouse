import os
import decimal
from PIL import Image
from datetime import datetime, timedelta
from django.urls import reverse
from django.conf import settings
from django.db.models import Q
from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_save