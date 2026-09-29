from django.db import models


class Course(models.Model):
    code = models.CharField(max_length=80, unique=True)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


class Exam(models.Model):
    key = models.CharField(max_length=80, unique=True)
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.PROTECT, related_name='exams')
    academic_term = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.key


class ExamSession(models.Model):
    key = models.CharField(max_length=80)
    exam = models.ForeignKey(Exam, on_delete=models.PROTECT, related_name='sessions')
    label = models.CharField(max_length=160, blank=True)
    scheduled_start_at = models.DateTimeField(null=True, blank=True)
    scheduled_end_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['exam', 'key'], name='one_session_key_per_exam')]

    def __str__(self):
        return self.key


class Room(models.Model):
    key = models.CharField(max_length=80, unique=True)
    label = models.CharField(max_length=160, blank=True)
    building = models.CharField(max_length=160, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.key
