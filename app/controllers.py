from http import HTTPStatus

from flask_restplus import Resource

from app.namespaces import FoldersNs, TaskNs, ErrorNs
from app import views
from app import tasks


@FoldersNs.ns.route('/<folderId>/search')
class VideoDuplicateProc(Resource):
    @FoldersNs.ns.doc({'folderId': 'ID of google drive folder'})
    @FoldersNs.ns.expect(FoldersNs.post_expect_model)
    @FoldersNs.ns.response(HTTPStatus.ACCEPTED, HTTPStatus.ACCEPTED.phrase,
                           model=FoldersNs.post_response_model)
    @FoldersNs.ns.response(HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND.phrase,
                           model=ErrorNs.error_model)
    @FoldersNs.ns.response(HTTPStatus.FORBIDDEN, HTTPStatus.FORBIDDEN.phrase,
                           model=ErrorNs.error_model)
    @FoldersNs.ns.marshal_with(fields=FoldersNs.post_response_model,
                               code=HTTPStatus.CREATED)
    def post(self, folderId):
        """Start searching duplicates"""
        email = FoldersNs.ns.payload['email']

        views.check_access(folderId)
        spreadsheet_id = views.create_result_table(email)
        task = tasks.process.delay(folderId, spreadsheet_id)

        return {'tableLink': 'https://docs.google.com/spreadsheets/d/' + spreadsheet_id,
                'taskId': task.id}, HTTPStatus.ACCEPTED


@TaskNs.ns.route('/<taskId>/status')
class TaskStatus(Resource):
    @TaskNs.ns.doc({'folderId': 'ID of the task'})
    @TaskNs.ns.response(HTTPStatus.OK, HTTPStatus.OK.phrase,
                        model=TaskNs.get_task_id_model)
    @TaskNs.ns.response(HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND.phrase,
                        model=ErrorNs.error_model)
    def get(self, taskId):
        """Get task status"""

        views.check_task_existing()

        return {'taskStatus': views.get_task_status(taskId)}, HTTPStatus.OK
