from rest_framework import viewsets
from main.serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
import requests
from bs4 import BeautifulSoup


class TestView(APIView):

    def get(self, request, *args, **kw):
        arg1 = request.GET.get('arg1', None)
        return Response({"test data" : "test", 'arg1' :arg1})



class ScrapeView(APIView):

    def get(self, request, *args, **kw):
        url = request.GET.get('url', None)
     
 
        if url:

            response= {}
            try:
                req_ob = requests.get(str(url).strip())
            except:
                return Response({"Response" : "Invalid URL"})
            
            gaussian = BeautifulSoup(req_ob.content, "html.parser")
            
            try:
                title = gaussian.find_all("title")[0]
                response['Title'] = str(title.text)         
            except:
                response['Title'] = ""
            
            try:        
                abstract = gaussian.find_all("p", {"id" : "p-2"})[0]
                abs_text = abstract.text.encode('ascii','ignore')
                response['Abstract'] = str(abs_text) 

            except:
                response['Abstract'] = "Not Found"


            hpo_obs = gaussian.find_all("a", {"class": "kwd-search"})

            if hpo_obs:
                # self.app.stdout.write(str(hpo_obs)+'\n\n')
                response['HPO Terms'] = []
                for ob in hpo_obs:
                    # self.app.stdout.write(ob.text + '\n')
                    response['HPO Terms'].append(str(ob.text))
                    # self.app.stdout.write('\n')
            else:
                response['HPO Terms'] = "Not Found"       

            return Response(response)  
        else:
            return Response({"Response" : "Url Not Found"})



server_url = 'https://scigraph-ontology-dev.monarchinitiative.org/scigraph'


class AnnotateView(APIView):

    def get(self, request, *args, **kw):
        url = request.GET.get('url', None)
 
        if url:

            try:
                req_ob = requests.get(str(url).strip())
            except:
                return Response({"Response" : "Invalid URL"})
            
            response = {}
            gaussian = BeautifulSoup(req_ob.content, "html.parser")
            

            try:        
                abstract = gaussian.find_all("p", {"id" : "p-2"})[0]
                abs_text = abstract.text.encode('ascii','ignore')
                data = {'content' : str(abs_text)}

                sci_graph_response = requests.get(server_url + '/annotations/entities', params = data)

                if sci_graph_response.status_code == 200:
                    annotated_data = sci_graph_response.json()
                    response['Annotated Abstract'] = str(annotated_data)



                    # Code to identify HPO Terms from annotated text
                    # hpo_terms = []
                    # for ob in annotated_data:
                    #     token = ob['token']
                    #     if 'Phenotype' in token['categories']:
                    #         term = str(token['terms'][0])
                    #         if term not in hpo_terms:
                    #             hpo_terms.append(token['terms'][0])

                else:
                    response['Annotated Abstract'] = ""


            except:
                response['Annotated Abstract'] = ""
      

            try:        
                hpo_obs = gaussian.find_all("a", {"class": "kwd-search"})
                hpo_terms= []
                if hpo_obs:
                    for ob in hpo_obs:
                        hpo_terms.append(str(ob.text).strip())

                response['Annotated HPO Terms'] = []
                for term in hpo_terms:          
                    data = {'content' : str(term)}

                    sci_graph_response = requests.get(server_url + '/annotations/entities', params = data)

                    if sci_graph_response.status_code == 200:
                        annotated_data = sci_graph_response.json()
                        response['Annotated HPO Terms'].append(str(annotated_data)) 

                    else:
                        response['Annotated HPO Terms'].append("")


            except:
                response['Annotated HPO Terms'] = []

            return Response(response)  
        else:
            return Response({"Response" : "URL Not Found"})


