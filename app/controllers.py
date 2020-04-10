from flask_restplus import Resource

from app.namespaces import VideoDuplicateNs


@VideoDuplicateNs.ns.route('<int:id>')
class VideoDuplicateProc(Resource):
    @VideoDuplicateNs.ns.doc({'id': 'ID of file or folder'})
    @VideoDuplicateNs.ns.marshal_with(VideoDuplicateNs.output_post_model)
    def get(self, id: int):
        """Get GoogleSheets link"""
        return {'table': f'test{id}'}
