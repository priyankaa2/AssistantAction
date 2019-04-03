response_lightson = requests.get('http://192.168.87.24:8081/sunits/lights_on')
print(response_lightson)

response_lightsoff = requests.get('http://192.168.87.24:8081/sunits/lights_off')
print(response_lightsoff)

response_get_bed = requests.post('http://192.168.87.24:8081/sunits/switch_mode', json={'mode':'night'})
json_response_get_bed = response_get_bed.json()
print(json_response_get_bed)

response_get_clothes = requests.post('http://192.168.87.24:8081/sunits/switch_mode', json={'mode':'morning'})
json_response_get_clothes = response_get_clothes.json()
print(json_response_get_clothes)


response_raise_all = requests.post('http://192.168.87.24:8081/sunits/raise_all', json={'speed_factor':'3000'})
json_response_raise_all = response_raise_all.json()
print(json_response_raise_all)
