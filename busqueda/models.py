# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Center(models.Model):
    name = models.CharField(max_length=150)

    def __unicode__(self):
        return self.name

class Building(models.Model):
    name = models.CharField(max_length=50)
    center = models.ForeignKey(Center)

    def __unicode__(self):
        return self.name

class Classroom(models.Model):
    number = models.CharField(max_length=15)
    type = models.CharField(max_length=10)
    building = models.ForeignKey(Building)

    def __unicode__(self):
        return self.number + self.type

class Cycle(models.Model):
    year = models.IntegerField()
    calendar = models.CharField(max_length=1)

    def __unicode__(self):
        return self.year

class Subject(models.Model):
    title = models.CharField(max_length=150)
    key = models.CharField(max_length=10)

    def __unicode__(self):
        return self.title

class Course(models.Model):
    isOfficial = models.BooleanField(default=True)
    cycle = models.ForeignKey(Cycle)
    subject = models.ForeignKey(Subject)

class Teacher(models.Model):
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)

    def __unicode__(self):
        return self.firstName + ' ' + self.lastName

class Day(models.Model):
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

class Schedule(models.Model):
    classroom = models.ForeignKey(Classroom)
    startTime = models.CharField(max_length=10)
    endTime = models.CharField(max_length=10)
    teacher = models.ForeignKey(Teacher)
    course = models.ForeignKey(Course)
    nrc = models.CharField(max_length=10)
    section = models.CharField(max_length=10)
    credits = models.CharField(max_length=5)
    maxQuotas = models.CharField(max_length=10)
    quotas = models.CharField(max_length=10)

    def __unicode__(self):
        return self.nrc

class ScheduleDays(models.Model):
    schedule = models.ForeignKey(Schedule)
    day = models.ForeignKey(Day)
