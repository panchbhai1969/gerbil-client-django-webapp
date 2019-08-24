from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Question
from django.http import Http404
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import urllib.parse as urlparse
from urllib.parse import unquote
import urllib
from bs4 import BeautifulSoup
import json
import os
import subprocess
from django.views.decorators.csrf import csrf_exempt
import logging


def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]

    context = {
        'latest_question_list': latest_question_list,
    }
    return render(request, 'polls/question_answer.html', context)


def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist.")
    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})


def vote(request, question_id):
    question = Question.objects.get(pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except(KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {'question': question,
                                                     'error_message': "You did not sekect a choice"
                                                     })
    else:
        selected_choice.votes += 1
        selected_choice.save()

    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


def qaserver(request, query):
    url = request.get_full_path()
    url = unquote(url)
    url = url.replace("/query", "/?query", 1)
    parsed = urlparse.urlparse(url)
    query = urlparse.parse_qs(parsed.query)['query']
    base = "/home/petrichor/Projects/GSoC/working-gsoc-anand/"
    subprocess.call("cd "+base+r" && ./ask.sh data/new_test_frequency_fixed_attention_drop07 " +
                    "\"" + query[0][:-1].strip() + "\"" + " deactivate && cat nmt/output_decoded.txt > example", shell=True,)
    print("cd "+base+r"&& ./ask.sh data/new_test_frequency_fixed_attention_drop07 " +
          "\"" + query[0][:-1].strip() + "\"" + " && cat nmt/output_decoded.txt > example")
    answer_query = open(base+"example").readline()

    answer_query = answer_query.replace("limit\n", "limit 1\n")
    query = urllib.parse.quote(answer_query)

    url2 = "https://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&query="+query + \
        "&format=text%2Fhtml&CXML_redir_for_subjs=121&CXML_redir_for_hrefs=&timeout=30000&debug=on&run=+Run+Query+"
    page = urllib.request.urlopen(url2)
    soup = BeautifulSoup(page, "html.parser")
    answer = []
    for rows in (soup.find_all("tr")):
        for td in rows.find_all("a"):
            for a in td:
                answer.append(a)

    return HttpResponse(';'.join(answer))


@csrf_exempt
def qaserver_json(request):
    # Create a logger object
    logger = logging.getLogger()

    # Configure logger
    logging.basicConfig(filename="logfile.log", format='%(filename)s: %(message)s', filemode='a')

    # Setting threshold level
    logger.setLevel(logging.DEBUG)

    # Use the logging methods
    #logger.debug("This is a debug message")   

    query = (request.POST.get("query"))
    
    """ url = request.get_full_path()
    url = unquote(url)
    url = url.replace("/query","/?query",1)
    parsed = urlparse.urlparse(url)
    query = urlparse.parse_qs(parsed.query)['query'] """
    original_query = query
    base = "/home/petrichor/Projects/GSoC/working-gsoc-anand/"
    subprocess.call("cd "+base+r" && ./ask.sh data/new_test_frequency_fixed_attention_drop07 " +
                    "\"" + query + "\"" + " deactivate && cat nmt/output_decoded.txt > example", shell=True,)
    print("cd "+base+r"&& ./ask.sh data/new_test_frequency_fixed_attention_drop07 " +
          "\"" + query + "\"" + " && cat nmt/output_decoded.txt > example")
    answer_query = open(base+"example").readline()

    answer_query = answer_query.replace("limit\n", "limit 1\n")
    query = urllib.parse.quote(answer_query)

    url2 = "https://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&query="+query+"&format=application%2Fsparql-results%2Bjson&CXML_redir_for_subjs=121&CXML_redir_for_hrefs=&timeout=30000&debug=on&run=+Run+Query+"
    page = urllib.request.urlopen(url2)
    soup = BeautifulSoup(page, "html.parser")
    #print(str(soup))
    logger.info(request.POST.get("query"))
    
    dic_answer = json.loads(str(soup))
    logger.info( dic_answer )
    
    val = {"questions": [{"id": "1", "question": [{"language": "en", "string": original_query}], "query": {"sparql": answer_query}, "answers":[{"head":dic_answer["head"], "results" : {"bindings":dic_answer["results"]["bindings"]}}]}]}
    #print(type(val))
    j = json.dumps(val)
    resp = JsonResponse(val, safe=False)
    logger.info(j)
    logger.info("**********************")
    resp['Access-Control-Allow-Origin'] = '*'
    return resp
