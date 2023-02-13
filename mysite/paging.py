from pybo.models import Question
from django.utils import timezone

for i in range(100):
    q = Question(subject='테스트 게시글입니다:[%03d]' %i, content='내용무', create_date=timezone.now())
    q.save()
