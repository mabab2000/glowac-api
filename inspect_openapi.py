import json
from main import app

openapi = app.openapi()
paths = openapi.get('paths', {})
ceo_post = paths.get('/ceo', {}).get('post')
ceo_put = paths.get('/ceo/{ceo_id}', {}).get('put')
print('POST /ceo schema:')
print(json.dumps(ceo_post, indent=2))
print('\nPUT /ceo/{ceo_id} schema:')
print(json.dumps(ceo_put, indent=2))
components = openapi.get('components', {}).get('schemas', {})
for name in ('Body_create_ceo_ceo_post', 'Body_update_ceo_ceo__ceo_id__put'):
	schema = components.get(name)
	print(f"\nComponent {name}:")
	print(json.dumps(schema, indent=2))
