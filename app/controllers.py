from http import HTTPStatus

from flask_restplus import Resource

from app.namespaces import VideoDuplicateNs, ErrorNs
from app import views


@VideoDuplicateNs.ns.route('/processing')
class VideoDuplicateProc(Resource):
    @VideoDuplicateNs.ns.doc({'id': 'ID of file or folder'})
    @VideoDuplicateNs.ns.expect(VideoDuplicateNs.post_expect_model)
    @VideoDuplicateNs.ns.response(HTTPStatus.CREATED, HTTPStatus.CREATED.phrase,
                                  model=VideoDuplicateNs.post_response_model)
    @VideoDuplicateNs.ns.response(HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND.phrase,
                                  model=ErrorNs.error_model)
    @VideoDuplicateNs.ns.response(HTTPStatus.FORBIDDEN, HTTPStatus.FORBIDDEN.phrase,
                                  model=ErrorNs.error_model)
    @VideoDuplicateNs.ns.marshal_with(VideoDuplicateNs.post_response_model,
                                      code=HTTPStatus.CREATED)
    def post(self):
        """Get GoogleSheets link"""

        id = VideoDuplicateNs.ns.payload['id']
        email = VideoDuplicateNs.ns.payload['email']

        return {'table', views.process(id, email)}, HTTPStatus.CREATED
