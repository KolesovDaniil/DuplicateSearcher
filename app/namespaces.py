from flask_restplus import Namespace, fields


class FoldersNs:
    """VideoDuplicate flask_restplus Namespace"""

    ns = Namespace('folders')

    post_expect_model = ns.model('PostExpectModel',
                                 {'email': fields.String()})

    post_response_model = ns.model('PostResponseModel',
                                   {'tableLink': fields.String(),
                                    'taskId': fields.String()})


class TaskNs:
    """Task flask_restplus Namespace"""

    ns = Namespace('tasks')

    get_task_id_model = ns.model('GetTaskIdModel',
                                 {'taskStatus': fields.String()})


class ErrorNs:
    """Namespace for errors"""

    ns = Namespace('')

    error_model = ns.model('ErrorModel',
                           {'message': fields.String()})
