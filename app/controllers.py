from http import HTTPStatus

from flask_restplus import Resource

from app.namespaces import VideoDuplicateNs, ErrorNs
from app.exceptions import ForbiddenError


@VideoDuplicateNs.ns.route('/processing')
class VideoDuplicateProc(Resource):
    @VideoDuplicateNs.ns.doc({'id': 'ID of file or folder'})
    @VideoDuplicateNs.ns.response()
    @VideoDuplicateNs.ns.marshal_with(VideoDuplicateNs.output_post_model)
    def post(self):
        """Get GoogleSheets link"""
        raise ForbiddenError('123')
