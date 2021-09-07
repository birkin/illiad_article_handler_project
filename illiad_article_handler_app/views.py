import logging, pprint

import django  # for type() test
from django.conf import settings as project_settings
from django.http import HttpResponse, HttpResponseRedirect
from illiad_article_handler_app.lib.shib_handler import Shibber
from illiad_article_handler_app.lib.view_handler_helper import HandlerHelper


log = logging.getLogger(__name__)


def handler(request):
    """ Creates ILLiad new-user if necessary, then redirects user to ILLiad form.
        On problem, stores error-message to session and redirects user to problem view. """
    log.debug( f'request.GET, ``{pprint.pformat(request.GET)}``' )
    ## setup ----------------------------------------------
    params_query_dict_copy = request.GET.copy()  # <https://stackoverflow.com/questions/5036498/django-rebuild-a-query-string-without-one-of-the-variables>
    log.debug( f'params_query_dict_copy, ``{pprint.pformat(params_query_dict_copy)}``' )
    assert type(params_query_dict_copy) == django.http.request.QueryDict, type(params_query_dict_copy)
    ## check for new ILLiad user --------------------------
    shibber = Shibber()
    handler_helper = HandlerHelper()
    ( good_shib_dct, err ) = shibber.prep_shib_dct( request.META, request.get_host() )
    if err:
        problem_response = handler_helper.create_problem_response( err, request ); return problem_response
    ( is_new_user, err ) = new_user_helper.check_new_user_status( shib_dct['eppn'] )
    if err:
        problem_response = handler_helper.create_problem_response( err, request ); return problem_response
    ## create new ILLiad user if necessary ----------------
    if is_new_user:
        ( create_result, err ) = new_user_helper.create_new_user( shib_dct )
        if err:
            problem_response = handler_helper.create_problem_response( err, request ); return problem_response
    ## redirect to ILLiad form ----------------------------
    ( redirect_url, err ) = handler_helper.create_illiad_redirect_url( params_query_dict_copy )
    if err:
        problem_response = handler_helper.create_problem_response( err, request ); return problem_response
    else:
        return HttpResponseRedirect( redirect_url )


def message( request ):
    """ Shows user problem message. """
    log.debug( '\n\nstarting views.message()' )
    error_message = request.session.get( 'error_message', '' )
    if error_message:
        log.debug( 'returning error_message' )
        # return HttpResponse( message )
        context = msg_hlpr.build_problem_context( error_message, uu_id )
        # return render( request, 'easyborrow_depositor_app_templates/message.html', context )
        return render( request, 'message.html', context )
    ## prep context -------------------------------
    ( context, err ) = msg_hlpr.prepare_good_context()
    log.debug( f'err, ``{err}``' )
    log.debug( f'context, ``{context}``' )
    if err:
        assert type(err) == str
        return HttpResponse( err )
    ## return request-submitted message -----------
    assert type(context) == dict
    # return render( request, 'easyborrow_depositor_app_templates/message.html', context )
    return render( request, 'message.html', context )


def info(request):
    return HttpResponse( 'info response coming' )


## for development convenience ------------------------------------------------


def error_check( request ):
    """ For an easy way to check that admins receive error-emails.
        To view error-emails in runserver-development:
        - run, in another terminal window: `python3 -m smtpd -n -c DebuggingServer localhost:1026`,
          (or substitute your own settings for localhost:1026)
    """
    log.debug( f'project_settings.DEBUG, ``{project_settings.DEBUG}``' )
    if project_settings.DEBUG == True:
        raise Exception( 'error-check triggered; admin emailed' )
    else:
        return HttpResponseNotFound( '<div>404 / Not Found</div>' )


def version(request):
    return HttpResponse( 'version response coming' )
