from http import HTTPStatus

from flask_restplus import Resource

from app.namespaces import VideoDuplicateNs, ErrorNs
from app import views
from app import tasks


@VideoDuplicateNs.ns.route('/<folderId>/search')
class VideoDuplicateProc(Resource):
    @VideoDuplicateNs.ns.doc({'folderId': 'ID of file or folder'})
    @VideoDuplicateNs.ns.expect(VideoDuplicateNs.post_expect_model)
    @VideoDuplicateNs.ns.response(HTTPStatus.ACCEPTED, HTTPStatus.ACCEPTED.phrase,
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

        gauth = views.check_access(id)
        service, spreadsheet_id = views.create_result_table(email)
        tasks.process(id, gauth, service, spreadsheet_id)

        return {'table', 'https://docs.google.com/spreadsheets/d/' + spreadsheet_id}, \
            HTTPStatus.ACCEPTED


@VideoDuplicateNs.ns.route('/<TaskId>/status')
class TaskStatus(Resource):
    @VideoDuplicateNs.ns.response(HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND.phrase,
                                  model=ErrorNs.error_model)
    def get(self):
        """"""

        return views.get_task_status(), HTTPStatus.OK
