from src.api.settings import api
from flask_restplus import fields

# fields that will be searched and help keep track of what fields are used


token_model = api.model('Token Model',
                        {'owner': fields.String(required=True, description="Owner of the token"),
                         'creation time': fields.String(required=True, description="Time of creation")
                         # TODO fix fields (components and types)
                        })


token_model_id = api.inherit('Id Token Model', token_model,
                        {'id': fields.String(required=True, description="Identifier of token"),
                         # TODO fix fields (components and types)
                        })
