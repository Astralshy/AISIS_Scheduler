from django.shortcuts import render
from .models import Department, Course, Section, Schedule
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework import status
from django.http import Http404
from .serializers import DepartmentSerializer, CourseSerializer, SectionSerializer, ScheduleSerializer
import os
import json
import requests


# Create your views here.
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def list(self, request):
        if 'id' in request.GET.keys():
            return Response(self.serializer_class(Department.objects.get(pk=request.GET['id'])).data)
        elif 'name' in request.GET.keys():
            return Response(self.serializer_class(Department.objects.get(name__exact=request.GET['name'])).data)
        return super(DepartmentViewSet, self).list(request)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def list(self, request):
        if 'code' in request.GET.keys():
            return Response(self.serializer_class(Course.objects.get(code__iexact=request.GET['code'])).data)
        if 'dept' in request.GET.keys():
            return Response([self.serializer_class(x).data for x in Course.objects.filter(dept_id=Department.objects.get(name__iexact=request.GET['dept']).id)])
        return super(CourseViewSet, self).list(request)


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

    def list(self, request):
        if 'code' in request.GET.keys() and 'sec' in request.GET.keys():
            data = self.serializer_class(Section.objects.filter(course_id__exact = Course.objects.get(code__iexact=request.GET['code'])).get(
                sec__iexact=request.GET['sec'])).data

            return Response(data)
        if 'code' in request.GET.keys():
            return Response([ self.serializer_class(x).data for x in Section.objects.filter(course_id__exact=Course.objects.get(code__iexact=request.GET['code']).id)])
        return super(SectionViewSet, self).list(request)


class CustomSectionView(ListAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

    def parse_date(self, date):
        data = []
        for s in date.split('-'):
            if s == 'Th':
                data.append('THURSDAY')
            elif s == 'T':
                data.append('TUESDAY')
            elif s == 'W':
                data.append('WEDNESDAY')
            elif s == 'M':
                data.append('MONDAY')
            elif s == 'F':
                data.append('FRIDAY')
            else:
                data.append('SATURDAY')
        return data

    def get_sections(self, section_list):
        data = []
        for section in section_list:
            data.append(SectionSerializer(Section.objects.get(pk=section)).data)
        return data

    def get(self, request, pk, format=None):
        sched = ScheduleSerializer(Schedule.objects.get(pk=pk)).data
        sec_list = self.get_sections(sched['sections'])

        if 'code' in request.GET.keys():
            sections = Section.objects.all().filter(course_id__exact=Course.objects.get(code__iexact=request.GET['code']))
        else:
            sections = None
            for course in Course.objects.filter(dept_id__exact=Department.objects.get(name__iexact=request.GET['dept']).id):
                if not sections:
                    sections = Section.objects.filter(course_id__exact=course.id)
                else:
                    sections = sections.union(Section.objects.filter(course_id__exact=course.id))

        for sec in sec_list:
            for section in sections:
                s = self.serializer_class(section).data
                sec_d = self.parse_date(sec['date'])
                s_d = self.parse_date(s['date'])
                match = False
                for d in sec_d:
                    if d in s_d:
                        match = True
                    break
                if match:
                    try:
                        sec_time = [int(x[0:2]) for x in sec['timeslot'].split('-')]
                        s_time = [int(x[0:2]) for x in s['timeslot'].split('-')]

                        if ((sec_time[0] == s_time[0]) or ((sec_time[1] < s_time[0]) and (sec_time[0] > s_time[1]))):
                            sections = sections.exclude(pk=s['id'])
                    except Exception as e:
                        pass

        return Response([self.serializer_class(section).data for section in sections])


class ScheduleView(APIView):
    def get(self, request, format=None):
        users = Schedule.objects.all()
        serializer = ScheduleSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        print(request.data)
        serializer = ScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ScheduleClasses(APIView):
    def put(self, request, format=None):
        if ('code' in request.query_params.keys() and 'sec' in request.query_params.keys()):
            id = json.loads(requests.get('http://localhost:8000/api/section/?code=%s&sec=%s' % (
            request.query_params['code'], request.query_params['sec'])).text)['id']
            if 'id' in request.query_params.keys():

                if 'op' in request.query_params.keys():

                    if request.query_params['op'] == 'rmv':
                        Schedule.objects.get(pk=request.query_params['id']).sections.remove(Section.objects.get(pk=id))
                        s = Schedule.objects.get(pk=request.query_params['id'])
                        s.save()
                    else:
                        Schedule.objects.get(pk=request.query_params['id']).sections.add(Section.objects.get(pk=id))
                        s = Schedule.objects.get(pk=request.query_params['id'])
                        s.save()
                else:
                    Schedule.objects.get(pk=request.query_params['id']).sections.add(Section.objects.get(pk=id))
                    s = Schedule.objects.get(pk=request.query_params['id'])
                    s.save()
            else:
                return Response['ID missing']
        else:
            return Response['Code and/or Section missing']
        return Response(['Class updated'])


class SchedulePKView(APIView):
    def get_object(self, pk):
        try:
            return Schedule.objects.get(pk=pk)
        except:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = ScheduleSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        user = Schedule.objects.get(pk=pk)
        serializer = ScheduleSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = Schedule.objects.get(pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ScraperView(APIView):
    def post(self, request, format=None):
        fields = request.data
        os.system('java -jar AISIS_Scraper.jar %s %s' % (fields['username'], fields['password']))
        os.system('java -jar AISIS_Scraper.jar %s %s' % (fields['username'], fields['password']))
        os.remove('cookies')

        with open('dept.txt', 'r') as file:
            for line in file:
                requests.post('http://localhost:8000/api/dept/', data={'name': line.split(' ')[0].replace('_', ' ')})
        file.close()
        os.remove('dept.txt')

        course_list = {}
        with open('output.txt', 'r') as file:
            for line in file:
                line = line.replace('[', '').replace(']', '').split(',')
                line = [x.strip() for x in line]
                if line[0] not in course_list.keys():
                    course_list[line[0]] = line[14]
                    id = json.loads(requests.get('http://localhost:8000/api/dept/?name=%s' % line[14]).text)['id']
                    requests.post('http://localhost:8000/api/course/',
                                  data={'name': line[2], 'code': line[0].replace(' ', ''), 'dept': id})
                id = \
                    json.loads(
                        requests.get('http://localhost:8000/api/course/?code=%s' % line[0].replace(' ', '')).text)[
                        'id']
                if line[4] != 'TBA':
                    time = line[4].split(' ')[1]
                    date = line[4].split(' ')[0]
                else:
                    time = 'TBA'
                    date = 'TBA'
                requests.post('http://localhost:8000/api/section/', data={
                    'sec': line[1],
                    'teacher': line[6],
                    'timeslot': time,
                    'date': date,
                    'venue': line[5],
                    'course': id
                })
        file.close()
        os.remove('output.txt')

        return Response(['Success'])
