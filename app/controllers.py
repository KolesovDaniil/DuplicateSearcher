from http import HTTPStatus

from flask_restplus import Resource

from app.namespaces import VideoDuplicateNs, TaskNs, ErrorNs
from app import views
from app import tasks


@VideoDuplicateNs.ns.route('/<folderId>/search')
class VideoDuplicateProc(Resource):
    @VideoDuplicateNs.ns.doc({'folderId': 'ID of google drive folder'})
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


@TaskNs.ns.route('/<TaskId>/status')
class TaskStatus(Resource):
    @TaskNs.ns.doc({'folderId': 'ID of the task'})
    @TaskNs.ns.response(HTTPStatus.OK, HTTPStatus.OK.phrase,
                        model=TaskNs.get_task_id_model)
    @TaskNs.ns.response(HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND.phrase,
                        model=ErrorNs.error_model)
    def get(self):
        """"""

        views.check_task_existing()

        return views.get_task_status(), HTTPStatus.OK
