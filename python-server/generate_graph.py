import requests
from pyvis.network import Network
import json

base_url = 'https://python-server-ohgaalojiq-de.a.run.app'

def get_rs(subject):
  response_names = json.loads(requests.get(rf'{base_url}/relationships-with-names/?subject={subject}').content)
  return (response_names)
##print(get_rs(1))

# def get_photo(name):
#   ref_pic = json.loads(requests.get(rf'{base_url}/stakeholders/?name={name}&summary=true&headline=true&photo=true').content)
#   pic_url = ref_pic[0].get("photo")
#   return pic_url

# print(get_photo("Ben Carson"))

def get_photo(name):
    response = requests.get(rf'{base_url}/stakeholders/?name={name}&summary=true&headline=true&photo=true').content
    ref_pic = json.loads(response)
    if ref_pic and isinstance(ref_pic, list) and len(ref_pic) > 0:
        photo_field = ref_pic[0].get("photo")
        if photo_field:
            pic_url = photo_field.split("||")[0].strip()  # Split by "||" and take the first URL
            return pic_url
        else:
            print(f"No photo field for get_photo({name}): {response}")
            return None
    else:
        print(f"Unexpected response for get_photo({name}): {response}")
        return None

def map_algs(g, alg="barnes"):
  if alg=="barnes":
    g.barnes_hut()
  if alg=="force":
    g.force_atlas_2based()
  if alg=="hr":
    g.hrepulsion()

def map_data(relationships, subj_color="#77E4C8", obj_color="#3DC2EC", edge_color="#96C9F4",subj_shape="image",obj_shape="image", alg="hr", buttons=False):
  g = Network(height="1024px", width="100%",font_color="black")
  if buttons == True:
    g.width = "75%"
    g.show_buttons(filter_=["edges", "physics"])
  for rs in relationships:
    subj = rs[0]
    pred = rs[1]
    obj = rs[2]
    s_pic = get_photo(subj)
    o_pic = get_photo(obj)
    g.add_node(subj, color=subj_color, shape=subj_shape, image=s_pic)
    g.add_node(obj, color=obj_color, shape=obj_shape, image=o_pic)
    g.add_edge(subj,obj,label=pred, color=edge_color, smooth=False)
  map_algs(g,alg=alg)
  g.toggle_physics(False)
  g.set_edge_smooth("dynamic")
  # print(type(g))
  # print("Debugging - g object:", g)
  # g.show("network1.html")
  print(g.generate_html(name='test.html', local=True))

if __name__ == '__main__':
  subject = 1
  nw = get_rs(subject)
  map_data(relationships= nw, subj_shape="circularImage", alg="hr", buttons=False)