from flask_restplus import Resource

from app.namespaces import VideoDuplicateNs


@VideoDuplicateNs.ns.route('/<int:id>')
@VideoDuplicateNs.ns.doc({'id': 'Video or folder id'})
@VideoDuplicateNs.ns.marshal_with(VideoDuplicateNs.output_post_model)
class VideoDuplicateProc(Resource):
    def post(self, id: int):
        pass
