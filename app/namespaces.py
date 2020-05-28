from flask_restplus import Namespace, fields


class VideoDuplicateNs:
    """VideoDuplicate flask_restplus Namespace"""

    ns = Namespace('')

    post_expect_model = ns.model('PostExpectModel',
                                 {'email': fields.String()})

    post_response_model = ns.model('PostResponseModel',
                                   {'tableLink': fields.String(),
                                    'statusId': fields.String()})


class TaskNs:
    """Task flask_restplus Namespace"""

    ns = Namespace('')

    get_task_id_model = ns.model('GetTaskIdModel',
                                 {'taskStatus': fields.String()})


class ErrorNs:
    """Namespace for errors"""

    ns = Namespace('')

    error_model = ns.model('ErrorModel',
                           {'message': fields.String()})
