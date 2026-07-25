from django.db import models

# Create your models here.
class FAQ(models.Model):
    question=models.TextField(max_length=2550)
    answer=models.TextField()

    def __str__(self):
        return self.question