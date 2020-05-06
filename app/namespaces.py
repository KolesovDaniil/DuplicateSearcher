from flask_restplus import Namespace, fields


class VideoDuplicateNs:
    """VideoDuplicate flask_restplus Namespace"""

    ns = Namespace('duplicate-video')

    post_expect_model = ns.model('PostExpectModel',
                                 {'email': fields.String(),
                                  'id': fields.String(required=True)})

    post_response_model = ns.model('PostResponseModel',
                                   {'table': fields.String()})


class ErrorNs:
    """Namespace for errors"""

    ns = Namespace('')

    error_model = ns.model('ErrorModel',
                           {'message': fields.String()})
