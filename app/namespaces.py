from flask_restplus import Namespace, fields


class VideoDuplicateNs:
    """VideoDuplicate flask_restplus Namespace"""

    ns = Namespace('duplicate-video')

    input_get_model = ns.model('InputGetModel',
                               {'email': fields.String()})
    output_get_model = ns.model('OutputGetModel',
                                {'email': fields.String()})
    output_post_model = ns.model('OutputPostModel',
                                 {'table': fields.String()})


class ErrorNs:
    """Namespace for errors"""

    ns = Namespace('')

    error_model = ns.model('ErrorModel',
                           {'message': fields.String()})
