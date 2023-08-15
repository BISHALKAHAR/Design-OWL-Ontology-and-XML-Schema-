import os
import rdflib
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import FOAF, XSD
from rdflib.namespace import  RDF, RDFS
import xml.etree.ElementTree as ET

myNamespace="http://www.semanticweb.org/bishal/ontologies/2023/3/tournament"
namedIndividual = URIRef('http://www.w3.org/2002/07/owl#NamedIndividual')
rdftype = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")

def isDefined(subs):
    for s in g.subjects():
        if(subs in str(s)):
            return True
    return False

cwd=os.getcwd()
tree = ET.parse('TOURNAMENT.xml')

root = tree.getroot()
matches={}
teams= {}
players= {}

tree = ET.parse('TOURNAMENT.xml')
root = tree.getroot()

matches = {}
teams = {}
players = {}

# Extract match data
for match in root.iter('match'):
    match_id = int(match.get('id'))
    

    # Extract team and player data
    team_data = []
    for team in match.iter('team'):
        team_dict = {
            'team': team.find('name').text,
            'players': []
        }
        for player in team.iter('player'):
            player_dict = {
                'id': int(player.get('id')),
                'name': player.find('name').text,
                'assists': int(player.find('assists').text),
                'points': int(player.find('points').text),
                'total_score': int(player.find('total_score').text)
            }
            team_dict['players'].append(player_dict)
            players[player_dict['id']] = player_dict
        team_data.append(team_dict)
    teams[match_id] = team_data



g=Graph()
g.parse("Tournament.ttl", format='xml')
print("OWL File Loaded")

# Add RDF triples for matches
for match_id in matches:
    match_name = f"Match_{match_id}"
    match_individual = URIRef(myNamespace + match_name)
    g.add((match_individual, RDF.type, namedIndividual))
    g.add((match_individual, RDF.type, URIRef(myNamespace + "Match")))
    g.add((match_individual, URIRef(myNamespace + "match_id"), Literal(str(match_id), datatype=XSD.integer)))
    g.add((match_individual, URIRef(myNamespace + "match_date"), Literal(matches[match_id]['date'], datatype=XSD.string)))
    g.add((match_individual, URIRef(myNamespace + "match_venue"), Literal(matches[match_id]['venue'], datatype=XSD.string)))
    g.add((match_individual, URIRef(myNamespace + "match_result"), Literal(matches[match_id]['result'], datatype=XSD.string)))

    # Add RDF triples for teams and players
    for team_data in teams[match_id]:
        team_name = f"Team_{team_data['team']}"
        team_individual = URIRef(myNamespace + team_name)
        g.add((team_individual, RDF.type, namedIndividual))
        g.add((team_individual, RDF.type, URIRef(myNamespace + "Team")))
        g.add((team_individual, URIRef(myNamespace + "team_name"), Literal(team_data['team'], datatype=XSD.string)))
        g.add((match_individual, URIRef(myNamespace + "has_team"), team_individual))

        for player_data in team_data['players']:
            player_name = f"Player_{player_data['name']}"
            player_individual = URIRef(myNamespace + player_name)


g.serialize(destination="Tournament.ttl", format='xml')


##Checking consitency and inferences

from owlready2 import *
# onto_path_append(cwd)
onto = get_ontology(cwd+"/Tournament.ttl").load()

#Checking consistency approach 1
with onto:
    sync_reasoner()
onto.save("Tournament_consistent.ttl")

g2=rdflib.Graph()
g2.parse("Tournament_final.ttl", format='xml')

count = 0
for s,p,o in g2:
    count=count+1
    
print("No of Triples Before :  " ,count)

g3=rdflib.Graph()
g3.parse("Tournament_consistent.ttl", format='xml')

count = 0
for s,p,o in g3:
    count=count+1

print("No of Triples After :  " ,count)

from rdflib.compare import to_isomorphic, graph_diff
iso1 = to_isomorphic(g2)
iso2 = to_isomorphic(g3)

if(iso1 == iso2):
    print("No Inferences")
else:
    in_both, in_first, in_second = graph_diff(iso1,iso2)
    print(" New Inderences and All Inferences Generated....")
    def dump_nt_sorted(g,f):
        for l in sorted(g.serialize(format='nt').splitlines()):
            if(l) : 
                # print(l)
                f.write(l)
                f.write("\n") 
               
    f = open("newInferences.txt", "w")
    dump_nt_sorted(in_second, f)
    f.close()

    f = open("allInferences.txt", "w")
    # dump_nt_sorted(in_first, f)
    dump_nt_sorted(in_both, f)
    dump_nt_sorted(in_second, f)
    f.close()
