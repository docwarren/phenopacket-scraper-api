# encoding=utf8

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
import requests
from bs4 import BeautifulSoup
from phenopacket.PhenoPacket import *
from phenopacket.models.Meta import *
import json



class TestView(APIView):
    """
    A simple test view to check
    whether the API is working.
    """

    def get(self, request, *args, **kw):
        arg = request.GET.get('arg', None)
        return Response({"test response" : "Test View", 'arg' :arg})




server_url = 'https://scigraph-ontology.monarchinitiative.org/scigraph'


class ScrapeView(APIView):
    """
    Takes a URL, scrapes the abstract  
    and HPO Terms using BeautifulSoup and
    produces them as output.
    """

    def get(self, request, *args, **kw):
        url = request.GET.get('url', None)
     
 
        if url:

            response= {}
            try:
                req_ob = requests.get(str(url).strip())
            except:
                return Response({"response" : "Invalid URL"})
            
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

            response['response'] = 'OK'     

            return Response(response)  
        else:
            return Response({"response" : "Url Not Found"})




class AnnotateView(APIView):
    """
    Takes a url, scrapes the abstract
    and HPO Terms and annotates them
    using scigraph annotator.
    """


    def get(self, request, *args, **kw):
        url = request.GET.get('url', None)
 
        if url:

            try:
                req_ob = requests.get(str(url).strip())
            except:
                return Response({"response" : "Invalid URL"})
            
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

            response['response'] = 'OK'

            return Response(response)  
        else:
            return Response({"response" : "URL Not Found"})




class PhenoPacketView(APIView):
    """
    Takes a url, scrapes the HPO Terms,
    annotates them using scigraph-annotator
    to extract HPO Term ids.

    Creates a phenopacket using phenopacket-
    python. 

    """

    def get(self, request, *args, **kw):
        url = request.GET.get('url', None)


        if url:

            try:
                req_ob = requests.get(str(url).strip())
            except:
                return Response({"response" : "Invalid URL"})
            
            gaussian = BeautifulSoup(req_ob.content, "html.parser")

            try:
                title = gaussian.find_all("title")[0]
                title = str(title.text.decode('utf-8'))

            except:
                title= ""
            

            try: 

                hpo_obs = gaussian.find_all("a", {"class": "kwd-search"})

                if hpo_obs:
                    hpo_terms=[]

                    for ob in hpo_obs:
                        hpo_terms.append(str(ob.text).strip())

                    phenotype_data = []
                    for term in hpo_terms:
                        data={'content' : str(term)}
                        response = requests.get(server_url+ '/annotations/entities', params = data)
                        if response.status_code == 200:
                            annotated_data = response.json()
                            for ob in annotated_data:
                                token = ob['token']
                                try:
                                    token_term = str(token['terms'][0])
                                except:
                                    continue
                                if str(token_term).lower() == str(term).lower():
                                    term_id = token['id']
                                    phenotype_data.append((term_id, term))
                        else:
                            self.app.stdout.write(str(response.status_code))


                    journal = Entity(
                                    id = str(url),
                                    type = EntityType.paper)

                    phenopacket_entities = [journal]


                    environment = Environment()
                    severity = ConditionSeverity()
                    onset = TemporalRegion()
                    offset = TemporalRegion()

                    evidence_type = OntologyClass(
                                                class_id="ECO:0000501",
                                                label="Evidence used in automatic assertion")

                    evidence = Evidence(types= [evidence_type])
                    
                    phenotype_profile = []
                    
                    for element in phenotype_data:
                        types_ob = OntologyClass(
                                                class_id= element[0],
                                                label= element[1])
                        types=[types_ob]

                        phenotype  =    Phenotype(
                                            types= types,
                                            environment=environment,
                                            severity=severity,
                                            onset=onset,
                                            offset=offset)

                        phenotype_association   = PhenotypeAssociation(
                                                    entity = journal.id,
                                                    evidence_list = [evidence],                                                    
                                                    phenotype = phenotype)

                        phenotype_profile.append(phenotype_association)


                    phenopacket = PhenoPacket(
                                        packet_id = "gauss-packet",
                                        title = title,
                                        entities = phenopacket_entities,
                                        phenotype_profile = phenotype_profile)



                    return Response({"phenopacket" : str(phenopacket), "response" : 'OK' })   
               
                else:
                    return Response({"response" : "HPO Terms Not found"})


            except:
                return Response({"response" : "HPO Terms Not found"})
        else:
            return Response({"response" : "URL Not Found"})

      

