from django.db import models

# Create your models here.
class UpdateMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Department(UpdateMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50,unique=True)

class Course(UpdateMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200,unique=False)
    code = models.CharField(max_length=20,unique=True)
    dept = models.ForeignKey('Department',on_delete=models.CASCADE)

class Section(UpdateMixin):
    id = models.AutoField(primary_key=True)
    sec = models.CharField(max_length=50,unique=False)
    teacher = models.CharField(max_length=100,unique=False)
    timeslot = models.CharField(max_length=100,unique=False)
    date = models.CharField(max_length=100,unique=False)
    venue = models.CharField(max_length=100,unique=False)
    course = models.ForeignKey('Course',on_delete=models.CASCADE)

class Schedule(UpdateMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50,unique=True)
    sections = models.ManyToManyField(Section)


