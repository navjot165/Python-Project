from django.db import models
from accounts.models import *
from accounts.constants import *


class ActionActivityLogs(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(User,on_delete=models.CASCADE,null=True, blank=True)
	api_url = models.CharField(max_length=1024, help_text='API URL',null=True, blank=True)
	headers = models.TextField(null=True, blank=True)
	body_data = models.TextField(null=True, blank=True)
	api_method = models.CharField(max_length=10, db_index=True,null=True, blank=True)
	ip_address = models.CharField(max_length=50,null=True, blank=True)
	api_response = models.TextField(null=True, blank=True)
	status_code = models.PositiveSmallIntegerField(help_text='Response status code', db_index=True,null=True, blank=True)
	created_on = models.DateTimeField(auto_now_add=True,null=True, blank=True)
	action_type = models.PositiveIntegerField(help_text='BACKEND OR API', choices=ACTION_TYPES, default=API_ACTION,null=True, blank=True)

	class Meta:
		managed=True
		default_permissions = ()
		db_table = 'action_activity_logs'